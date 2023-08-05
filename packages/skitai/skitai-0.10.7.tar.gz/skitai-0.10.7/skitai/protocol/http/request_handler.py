from . import response as http_response
from skitai.client import adns
import base64
from skitai.server import utility
from hashlib import md5

class Authorizer:
	def __init__ (self):
		self.db = {}
	
	def get (self, netloc, auth, method, uri, data):
		if netloc not in self.db:
			return ""
			
		infod = self.db [netloc]
		if infod ["meth"] == "basic":
			return "Basic " + base64.encodestring ("%s:%s" % auth) [:-1]	
		else:
			infod ["nc"] += 1
			hexnc = hex (infod ["nc"])[2:].zfill (8)
			infod ["cnonce"] = utility.md5uniqid ()
			
			A1 = md5 (("%s:%s:%s" % (auth [0], infod ["realm"], auth [1])).encode ("utf8")).hexdigest ()
			if infod ["qop"] == "auth":
				A2 = md5 (("%s:%s" % (method, uri)).encode ("utf8")).hexdigest ()
			elif type (data) is bytes:
				entity = md5 (data).hexdigest ()
				A2 = md5 (("%s:%s" % (method, uri)).encode ("utf8")).hexdigest ()
			else:
				return # sorry data is not bytes
						
			Hash = md5 (("%s:%s:%s:%s:%s:%s" % (
				A1,
				infod ["nonce"],
				hexnc,
				infod ["cnonce"],
				infod ["qop"],
				A2
				)).encode ("utf8")
			).hexdigest ()
			
			return (
				'Digest username="%s", realm="%s", nonce="%s", '
				'uri="%s", response="%s", opaque="%s", qop=%s, nc=%s, cnonce="%s"' % (
					auth [0], infod ["realm"], infod ["nonce"], uri, Hash, 
					infod ["opaque"], infod ["qop"], hexnc, infod ["cnonce"]
				)
			)
			
	def set (self, netloc, authreq, auth):
		if auth is None:
			return
			
		amethod, authinfo = authreq.split (" ", 1)
		infod = {"meth": amethod.lower ()}		
		infod ["nc"] = 0
		for info in authinfo.split (","):
			k, v = info.strip ().split ("=", 1)
			if not v: return self.get_www_authenticate ()
			if v[0] == '"': v = v [1:-1]
			infod [k]	 = v
		
		if "qop" in infod:
			qop = list (map (lambda x: x.strip (), infod ["qop"].split (",")))
			if "auth" in qop:
				infod ["qop"] = "auth"
			else:
				infod ["qop"] = "auth-int"
				
		self.db [netloc] = infod
		

authorizer = Authorizer ()

class RequestHandler:
	def __init__ (self, asyncon, request, callback, http_version = "1.1", connection = "keep-alive"):
		self.asyncon = asyncon
		self.buffer = b""	
		self.wrap_in_chunk = False
		self.end_of_data = False		
		
		self.request = request
		self.callback = callback
		self.http_version = http_version
		self.logger = request.logger
		self.connection = connection		
		self.retry_count = 0
		self.reauth_count = 0
		self.response = None	
		
		self.method, self.uri = (
			self.request.get_method (),			
			self.asyncon.is_proxy () and self.request.uri or self.request.path
		)
		self.header = []
		if request.get_address () is None:
			request.set_address (self.asyncon.address)
		
		self.asyncon.set_terminator (b"\r\n\r\n")	
	
	def _del_ (self):
		self.callback = None
		self.asyncon = None
		self.request = None
		self.response = None

	def log (self, message, type = "info"):
		self.logger.log ("%s - %s" % (self.request.uri, message), type)

	def log_info (self, message, type='info'):
		self.log (message, type)

	def trace (self):
		self.logger.trace (self.request.uri)
	
	#------------------------------------------------
	# handler must provide these methods
	#------------------------------------------------
	def get_request_buffer (self):
		data = self.request.get_data ()		
		is_data_producer = False
		
		hc = {}
		if (self.http_version == "1.1" and self.connection == "close") or (self.http_version == "1.0" and self.connection == "keep-alive"):
			hc ["Connection"] = self.connection
		
		address = self.request.get_address ()
		if address [1] in (80, 443):			
			hc ["Host"] = "%s" % address [0]
		else:
			hc ["Host"] = "%s:%d" % address

		hc ["Accept"] = "*/*"		
		hc ["Accept-Encoding"] = "gzip"
		
		if data:			
			try:
				cl = data.get_content_length ()
				is_data_producer = True
			except AttributeError:
				cl = len (data)				
			hc ["Content-Length"] = cl
		
			ct = self.request.get_content_type ()		
			if ct:
				hc ["Content-Type"] = self.request.get_content_type ()
				
		auth = self.request.get_auth ()
		if auth:
			uri = self.asyncon.is_proxy () and self.request.uri or self.request.path
			auth_header = authorizer.get (self.request.get_address (), auth, self.method, uri, data)
			if auth_header is None:
				raise AssertionError ("Unknown authedentification method")
			if auth_header:
				hc ["Authorization"] = auth_header
		
		ua = self.request.get_useragent ()
		if ua:
			hc ["User-Agent"] = ua
			
		for k, v in self.request.get_headers ():
			hc [k] = v
		
		self.header = ["%s: %s" % x for x in list(hc.items ())]					
		req = ("%s %s HTTP/%s\r\n%s\r\n\r\n" % (
			self.method,
			self.uri,
			self.http_version,
			"\r\n".join (self.header)
		)).encode ("utf8")
		
		#print (req)
		#print (data)
		if is_data_producer:
			return [req, data]
		else:	
			return [req + data]
	
	def recalibrate_response (self, error, msg):
		if self.response is None and not error and self.buffer: 
			s = self.buffer.find (b"\n\n")
			if s != -1:
				body = self.buffer [s+2:]
				self.buffer = self.buffer [:s]
				try:
					self.create_response ()
					self.response.collect_incoming_data (body)							
				except:
					self.trace ()
					self.response = None
					error, msg = 707, "HTTP Header or Body Error"
					self.log ("%d %s" % (error, msg), "error")
						
		if self.response is None:
			if error:
				self.response = http_response.FailedResponse (error, msg, self.request)
			else:
				error, msg = 708, "No Data Recieved"
				self.response = http_response.FailedResponse (error, msg, self.request)	
				self.log ("%d %s" % (error, msg), "error")
		
		# finally call done, even if failed or error occured in recving body, just done.
		self.response.done ()
		return error, msg
		
	def done (self, error = 0, msg = ""):		
		# handle abnormally raised exceptions like network error etc.
		self.recalibrate_response (error, msg)		
		
		if self.reauth_count == 0 and self.response.code == 401:
			self.reauth_count = 1		
			try: 
				authorizer.set (self.request.get_address (), self.response.get_header ("WWW-Authenticate"), self.request.get_auth ())
				bufs = self.get_request_buffer ()
			except:
				self.trace ()				
				self.response = http_response.FailedResponse (706, "Unknown Authedentification Method", self.request)
			else:
				for buf in bufs:
					self.asyncon.push (buf)				
				self.response = None
				self.asyncon.set_terminator (b"\r\n\r\n")
				self.asyncon.start_request (self)
				return 401
		
		if self.asyncon:
			self.asyncon.request = None		
						
		if self.callback:
			self.callback (self)
		
	def collect_incoming_data (self, data):
		if not self.response or self.asyncon.get_terminator () == b"\r\n":
			self.buffer += data
		else:
			try:
				self.response.collect_incoming_data (data)
			except:
				self.response = http_response.FailedResponse (709, "Invalid Content", self.request)
				raise
			
	def found_terminator (self):
		if self.response:
			if self.end_of_data:
				self.asyncon.handle_close ()
				return
			
			if self.wrap_in_chunk:			
				if self.asyncon.get_terminator () == 0:
					self.asyncon.set_terminator (b"\r\n")
					self.buffer = b""
					return
						
				if not self.buffer:
					return
				
				chunked_size = int (self.buffer.split (b";") [0], 16)				
				self.buffer = b""
				
				if chunked_size == 0:
					self.end_of_data = True
					self.asyncon.set_terminator (b"\r\n")
					
				elif chunked_size > 0:
					self.asyncon.set_terminator (chunked_size)
			
			elif self.asyncon.get_terminator () == 0:
				self.asyncon.handle_close ()
						
		else:
			try:
				self.create_response ()
			except:	
				# I don't know why handle exception here.
				# If not, recv data continuously T.T
				self.asyncon.handle_error ()
				return
			
			# 100 Continue etc. try recv continued header
			if self.response is None:
				return
				
			self.asyncon.close_it = self.will_be_close ()			
			if self.used_chunk ():
				self.wrap_in_chunk = True
				self.asyncon.set_terminator (b"\r\n") #chunked transfer
			
			else:			
				try:
					clen = self.get_content_length ()
				except TypeError:
					if self.asyncon.close_it:
						clen = ""
					else:
						clen = 0 # no transfer-encoding, no content-lenth
				
				if clen == 0:
					self.asyncon.handle_close ()
					return
					
				self.asyncon.set_terminator (clen)
			
			#self.buffer = ""

	def create_response (self):
		# overide for new Response
		buffer, self.buffer = self.buffer, b""
		#print (repr (buffer))
		try:
			self.response = http_response.Response (self.request, buffer.decode ("utf8"))		
		except:
			self.log ("response header error: `%s`" % repr (buffer.decode ("utf8") [:80]), "error")
			raise
		self.is_continue_response ()
		
	def is_continue_response (self):	
		# default header never has "Expect: 100-continue"
		# ignore, wait next message	
		if self.response.code == 100:			
			self.response = None
			self.asyncon.set_terminator (b"\r\n\r\n")
			return True
		return False	
			
	def start (self):		
		if adns.query:
			adns.query (self.asyncon.address [0], "A", callback = self.continue_start)
		else:
			self.continue_start (True)
		
	def continue_start (self, answer):
		if not answer:
			self.log ("DNS not found - %s" % self.asyncon.address [0], "error")
			return self.done (704, "DNS Not Found")
		
		for buf in self.get_request_buffer ():
			self.asyncon.push (buf)
		self.asyncon.start_request (self)
	
	def retry (self):
		if self.retry_count:
			return False
			
		self.response = None
		self.asyncon.close_socket ()
		self.asyncon.request = None # unlink back ref.
		self.retry_count = 1		
		self.asyncon.cancel_request ()
		for buf in self.get_request_buffer ():
			self.asyncon.push (buf)
		self.asyncon.start_request (self)
		return True
					
	def will_be_close (self):
		if self.response is None:
			return True
		
		if self.connection == "close": #server misbehavior ex.paxnet
			return True
				
		close_it = True
		connection = self.response.get_header ("connection")
		if self.response.version in ("1.1", "1.x"):
			if not connection or connection.lower () == "keep-alive":
				close_it = False
		else:
			if connection and connection.lower () == "keep-alive":
				close_it = False
		
		if not close_it:
			keep_alive = self.response.get_header ("keep-alive")
			if keep_alive:
				for each in keep_alive.split (","):
					try: 
						k, v = each.split ("=", 1)
					except ValueError:
						continue
					
					if k.strip () == "timeout": 
						timeout = int (v)
						if timeout < self.asyncon.keep_alive_timeout:
							self.asyncon.set_keep_alive_timeout (timeout)
					elif k.strip () == "max" and int (v) == 0:
						close_it = True
		
		return close_it
	
	def used_chunk (self):
		transfer_encoding = self.response.get_header ("transfer-encoding")
		return transfer_encoding and transfer_encoding.lower () == "chunked"
	
	def get_content_length (self):
		return int (self.response.get_header ("content-length"))
	
	def get_content_type (self):
		return self.response.get_header ("content-type")
		
	def get_http_version (self):
		return self.response.version
   	
   	
   	