import json
import requests
from requests import auth
from exception import error

class network:
	requests.packages.urllib3.disable_warnings()
	
	def __init__( self, quiubas ):
		self.quiubas = quiubas

	def get ( self, path, params = None ):
		return self.request( path, params, 'GET' )

	def post ( self, path, params = None ):
		return self.request( path, params, 'POST' )

	def delete( self, path, params = None ):
		return self.request( path, params, 'DELETE' )

	def put( self, path, params = None ):
		return self.request( path, params, 'PUT' )

	def request( self, path, params = dict(), method = 'GET' ):

		if type (path) is list:
			path = self.quiubas.format( path.pop(0), path.pop() );

		url = self.formatBaseURL( path )

		request_method = getattr(requests, method.lower())

		headers = {'user-agent': 'Quiubas-Python/' + self.quiubas.lib_version}

		auth_info = self.quiubas.getAuth()
		auth_info = auth.HTTPBasicAuth( auth_info['api_key'], auth_info['api_private'] )

		timeout = 20

		try:
			if method == 'GET':
				request = request_method( url, auth=auth_info, timeout=timeout, headers=headers, verify=False, params=params )
			else:
				request = request_method( url, auth=auth_info, timeout=timeout, headers=headers, verify=False, data=params )
		except ValueError as e:
			raise error( 'There was an error trying communicating with Quiubas Server: ' + str(e) )

		try:
			response = json.loads(request.text)
		except ValueError as e:
			raise error( 'There was an error parsing the response: ' + str(e) )

		return response

	def getBaseURL( self ):
		return self.quiubas.getBaseURL() + '/' + self.quiubas.version + '/'

	def formatBaseURL( self, path ):
		return self.getBaseURL() + path;

