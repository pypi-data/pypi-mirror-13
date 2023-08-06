import ctxlogger

from .. import ParseException

##
## eg.
##
## record_batch(
##     multi_record = {
##         '01': header_record,
##         '02': order_record,
##         '05': component_record,
##         '09': footer_record,
##     }
## )
##
## record_batch(
##     single_record = csv_record
## )
##

class record_batch( object ):

	def __init__( self, single_record = None, multi_record = None, linebreak = '\n', header = False ):
		if not single_record and not multi_record:
			ctxlogger.exception( ParseException, u'No record type specified' )

		self.linebreak = linebreak
		self.header = header

		self.single_record = single_record
		self.multi_record = multi_record

	def parse( self, batch ):
		data = []
		for idx, record in enumerate( batch.splitlines(), 1 ):
			with ctxlogger.context( u'line', idx ):

				# ignore blank or header lines
				if record.strip() == '' or ( self.header and idx == 1 ):
					ctxlogger.debug( u'Ignoring' )
					continue

				if self.single_record:
					fields = self.single_record.parse( record )

					if u'_line' in fields and fields[ u'_line' ] != idx:
						ctxlogger.exception(
							ParseException,
							u'Line number "{}" does not match'.format(
								fields[ u'_line' ]
							)
						)

					data.append( fields )

				else:
					for rtype, parser in self.multi_record.items():
						# try all our records,
						# and find which ones can parse this line
						try:
							fields = parser.parse( record )
						except ParseException: # didn't match
							continue

						# is this the correct record for this line?
						if fields[ u'_type' ] != rtype:
							continue

						if u'_line' in fields and fields[ u'_line' ] != idx:
							ctxlogger.exception(
								ParseException,
								u'Line number "{}" does not match'.format(
									fields[ '_line' ]
								)
							)

						data.append( fields )
						break

					else:
						ctxlogger.exception(
							ParseException, u'Unrecognised record type'
						)

		return data

	def unparse( self, data ):
		records = []

		# check if we need to add a header line
		if self.header:
			try:
				records.append( self.single_record.as_header() )
			except NotImplementedError as e:
				ctxlogger.exception(
					ParseException,
					u'Header line unsupported for this format',
					orig_exc = e,
				)
			except AttributeError as e:
				ctxlogger.exception(
					ParseException,
					u'No header information supplied',
					orig_exc = e
				)
			except ParseException:
				raise

		for idx, recdata in enumerate( data, 1 ):
			with ctxlogger.context( u'line', idx ):
				# adding this to recdata modifies the actual
				# parsing spec, which we don't want to do
				copydata = dict( recdata )
				copydata[ u'_line' ] = idx

				if self.single_record:
					records.append( self.single_record.unparse( copydata ) )
				else:
					try:
						rectype = copydata[ u'_type' ]
					except KeyError as e:
						ctxlogger.exception(
							ParseException,
							u'No type field in record',
							orig_exc = e,
						)

					try:
						records.append(
							self.multi_record[ rectype ].unparse( copydata )
						)
					except KeyError as e:
						ctxlogger.exception(
							ParseException,
							u'Unrecognised record type "{}"'.format(
								str(rectype)
							),
							orig_exc = e
						)
					except ParseException:
						raise

		return self.linebreak.join( records )
