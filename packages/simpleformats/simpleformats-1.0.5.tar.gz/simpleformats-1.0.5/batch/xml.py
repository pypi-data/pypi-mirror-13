import ctxlogger
import xmltodict

from .. import ParseException

class xml_batch( object ):

	def __init__( self, format = None ):
		self.format = format

	def element_as_list( self, element ):
		"""
		Utility function to ensure a child element is a list for iteration,
		since it won't be if there was only one.
		We can't use the nicer hasattr( 'next' ) since that would be true
		for a dictionary too.
		"""
		if not isinstance( element, list ):
			return [ element ]
		return element

	def parse( self, batch ):
		content = xmltodict.parse( batch )
		if not self.format:
			return content
		return self._parse_element( self.format, content )

	def _parse_element( self, format, xml ):
		if isinstance( format, list ):
			return self._parse_list( format, self.element_as_list( xml ) )
		if isinstance( format, dict ):
			return self._parse_dict( format, xml )

		try: # leaf data, try and parse it
			return format.parse( xml )
		except AttributeError as e: # no parse
			ctxlogger.exception(
				ParseException,
				u'No parse method on {}'.format( type( format ) ),
				orig_exc = e,
			)

	def _parse_list( self, format, xml ):
		content = []
		for section in format:
			for element in xml:
				content.append( self._parse_element( section, element ) )
		return content

	def _parse_dict( self, format, xml ):
		content = {}
		for name, section in format.items():
			element = xml.get( name, '' )
			with ctxlogger.context( u'element', name ):
				content[ name ] = self._parse_element( section, element )
		return content

	def unparse( self, data ):
		"""
		Converts the incoming data into XML.
		Expects the format described here:
		http://www.xml.com/pub/a/2006/05/31/converting-between-xml-and-json.html

		data - a dict following the above format
		"""
		if not isinstance( data, dict ):
			ctxlogger.exception( ParseException, u'Invalid data structure' )

		if len(data) > 1: # must be one XML element at the top level
			ctxlogger.exception( ParseException, u'Only one top-level element allowed' )

		element, content = list(data.items())[0]
		return self._unparse_element( content, element, self.format )

	def _unparse_element( self, data, element, format ):
		# only care about the format details inside
		if format and isinstance( format, list ):
			format = format[0] # TODO, can you have more than one?

		with ctxlogger.context( u'element', element ):
			if data == None:
				return u'<{} />'.format( str(element) )

			if isinstance( data, list ):
				return ''.join( [ self._unparse_element( e, element, format ) for e in data ] )

			if isinstance( data, dict ):
				try:
					return self._unparse_dict(
						data, element, format[ element ]
					)
				except KeyError as e:
					ctxlogger.exception(
						ParseException,
						u'Missing format for element',
						orig_exc = e
					)
				except TypeError: # format is None
					return self._unparse_dict( data, element, None )

			try:
				return u'<{element}>{data}</{element}>'.format(
					element = str(element),
					data = format[ element ].unparse( data )
				)
			except TypeError: # format is None, treat as string
				return u'<{element}>{data}</{element}>'.format(
					element = element, data = str( data ) )
			except KeyError as e:
				ctxlogger.exception(
					ParseException, u'Missing format for element', orig_exc = e
				)
			except AttributeError as e: # no unparse
				ctxlogger.exception(
					ParseException,
					u'No unparse method on {}'.format( type(format[ element ]) ),
					orig_exc = e
				)

	def _unparse_dict( self, data, element, format ):
		atts, content = u'', u''

		for key, value in sorted(list(data.items())):
			if key == u'#text':
				try:
					content += format[ element ].unparse( value )
				except TypeError:
					content += str(value)
				except KeyError:
					ctxlogger.exception(
						ParseException, u'Missing format for element'
					)
				except AttributeError: # no unparse
					ctxlogger.exception(
						ParseException,
						u'No unparse method on {}'.format( type(format[element]))
					)
			elif key.startswith( u'@' ):
				atts += u' {}="{}"'.format( str(key[1:]), str(value) )
			else:
				content += self._unparse_element( value, key, format )

		if not content:
			return u'<{}{} />'.format( str(element), atts )
		return u'<{element}{atts}>{content}</{element}>'.format(
			element = str(element), atts = atts, content = content
		)
