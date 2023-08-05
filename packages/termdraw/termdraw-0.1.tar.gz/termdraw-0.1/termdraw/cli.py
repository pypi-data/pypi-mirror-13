#!/usr/bin/env python
# vim:fenc=utf8:ts=4:sw=4:sts=4:noet:

def _any_pref(haystack, preflist):
	return any([haystack.startswith(pref) for pref in preflist])

class CLIParser(object):
	def __init__(self):
		self.shortoptlist       = []    # List of all one letter options
		self.longoptlist        = []    # List of all --long-options
		self.shortopts_with_arg = []    # List of short opts with arguments
		self.longopts_with_arg  = []    # List of long opts with arguments
		self.shortopts_required = []    # List of required short opts
		self.longopts_required  = []    # List of required long opts
		self.short_long_mapping = {}    # Long options equivalent to short ones
		self.rawargs_opt        = ''    # with_arg option alternatively
		                                # supplied with rawargs
		self.rawargs_opt_long   = None
		self.help_override_req  = True  # --help overrides arg requirements
		self.shortoptions       = {}    # Parsed option->value dictionary
		self.longoptions        = {}
		self.rawargs            = []    # Non-option arguments
		self.accept_bare_dash   = False # Double bare dash -- works
		self.argv0              = None  # Name of the program

	def parse(self, argv):
		bare_dash_on = False

		tmp_shortopt_required_list = self.shortopts_required
		tmp_longopt_required_list = self.longopts_required

		if len(argv) <= 0:
			raise ValueError('argv is empty, something has gone very wrong')

		self.argv0 = argv[0]

		optiter = enumerate(argv[1:])

		for idx, option in optiter:
			if option is '--':
				if self.accept_bare_dash:
					if bare_dash_on:
						self.rawargs.append(option)
						continue

					else:
						bare_dash_on = True

				else:
					self.rawargs.append(option)

			elif option.startswith('--'):
				if self.accept_bare_dash and bare_dash_on:
					rawargs.append(option)

				else:
					optstring = option[2:]

					if optstring in self.longoptlist:
						if optstring not in self.longopts_with_arg:
							self.longoptions[optstring] = True
							continue

						else:
							# Fail if there is no argument to the right
							if (idx+2 == len(argv)) or (argv[idx+2] is '--') or (argv[idx+2].startswith('-')):
								raise ValueError('option '+optstring+' requires an argument')

							else:
								self.longoptions[optstring] = argv[idx+2]
								next(optiter, None)
								continue

					else:
						if not _any_pref(optstring, self.longoptlist):
							raise ValueError('unknown option '+optstring)

						elif not _any_pref(optstring, [p+'=' for p in self.longopts_with_arg]):
							raise ValueError('unknown option '+optstring)

						else:
							eq_idx = optstring.index('=')
							optname = optstring[:eq_idx]
							optval = optstring[eq_idx+1:]
							self.longoptions[optname] = optval
							continue

			elif option.startswith('-'):
				if self.accept_bare_dash and bare_dash_on:
					rawargs.append(option)

				else:
					optstring = option[1:]
					chariter = enumerate(optstring)

					if optstring == '':
						self.rawargs.append(option)

					for i, char in chariter:
						if char not in self.shortoptlist:
							raise ValueError('unknown option '+char)

						else:
							if char not in self.shortopts_with_arg:
								if char not in self.short_long_mapping:
									self.shortoptions[char] = True

								else:
									self.longoptions[self.short_long_mapping[char]] = True
								continue

							else:
								if (i+1 != len(optstring)) or (idx+2 == len(argv)):
									raise ValueError('option '+char+' requires an argument')

								else:
									if char not in self.short_long_mapping:
										self.shortoptions[char] = argv[idx+2]

									else:
										self.longoptions[self.short_long_mapping[char]] = argv[idx+2]

									next(optiter, None)

			else:
				self.rawargs.append(option)

		if len(argv) is 1:
			self.longoptions = {}
			self.shortoptions = {}
			self.rawargs = []

		if self.rawargs_opt is not '' and len(self.rawargs) == 1:
			if self.rawargs_opt_long:
				if not self.longoptions.has_key(self.rawargs_opt):
					tmp_longopt_required_list.remove(self.rawargs_opt)
					self.longoptions[self.rawargs_opt] = self.rawargs[0]
			else:
				if not self.shortoptions.has_key(self.rawargs_opt):
					tmp_shortopt_required_list.remove(self.rawargs_opt)
					self.shortoptions[self.rawargs_opt] = self.rawargs[0]

		if not ('help' in self.longoptions and self.help_override_req):
			for o in tmp_shortopt_required_list:
				if o not in self.shortoptions:
					raise ValueError('option '+o+' required')

			for o in tmp_longopt_required_list:
				if o not in self.longoptions:
					raise ValueError('option '+o+' required')
