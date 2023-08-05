import re
import urllib
from network import network
from balance import balance
from callback import callback
from keywords import keywords
from sms import sms

class Quiubas:
	def __init__( self ):
		self.lib_version		= '1.0.1'
		self.api_key			= None
		self.api_private		= None
		self.base_url			= 'https://rest.quiubas.com'
		self.version			= '1.0'

		self.network = network( self )

		self.balance = balance( self )
		self.callback = callback( self )
		self.keywords = keywords( self )
		self.sms = sms( self )

	def setBaseURL( self, url ):
		self.base_url = url
		return self.base_url

	def getBaseURL( self ):
		return self.base_url

	def setAuth( self, api_key, api_private ):
		self.api_key = api_key
		self.api_private = api_private

	def getAuth( self ):
		return {
			'api_key': self.api_key,
			'api_private': self.api_private
		}

	def format(self, path, vars = None):
		if not vars:
			vars = dict()

		parsed_vars = dict()

		for k in vars.keys():
			if vars[k] is not None:
				parsed_vars['{' + k + '}'] = urllib.quote_plus(vars[k])

		regex = re.compile("(%s)" % "|".join(map(re.escape, parsed_vars.keys())))

		if len(parsed_vars) != 0:
			return regex.sub(lambda mo: str(parsed_vars[mo.string[mo.start():mo.end()]]), path)
		else:
			return path

