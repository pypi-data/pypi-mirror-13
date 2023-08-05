from base import base

class sms( base ):
	def __init__( self, quiubas ):
		base.__init__( self, quiubas )
		self.base_name		= 'sms'
		self.action_name	= 'sms/{id}'

	def send( self, params ):
		return self.action( params )

	def getResponses( self, id, params = None ):
		return self.quiubas.network.get( [ self.action_name + '/responses', { 'id': id } ], params )

