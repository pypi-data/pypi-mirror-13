from base import base

class keywords( base ):
	def __init__( self, quiubas ):
		base.__init__( self, quiubas )
		self.base_name		= 'keywords'
		self.action_name	= 'keywords/{id}'

	def create ( self, params ):
		return self.action( params )

