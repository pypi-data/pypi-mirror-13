
from ..utilities import category, pmath, rename
from ..core import LarchError, ParameterAlias
from io import StringIO



class LatexModelReporter():

	def latex_params(self, groups=None, display_inital=False, **format):

		# keys fix
		existing_format_keys = list(format.keys())
		for key in existing_format_keys:
			if key.upper()!=key: format[key.upper()] = format[key]
		if 'PARAM' not in format: format['PARAM'] = '< 12.4g'
		if 'TSTAT' not in format: format['TSTAT'] = ' 0.2f'

		number_of_columns = 5
		if display_inital:
			number_of_columns += 1


		if groups is None and hasattr(self, 'parameter_groups'):
			groups = self.parameter_groups

		table = StringIO()
		
		table.write(r"""%
\providecommand{\tableheadfont}{\textbf}%
\providecommand{\tablebodyfont}{}%
\providecommand{\thead}[1]{\tableheadfont{#1}}%
\providecommand{\tbody}[1]{{#1}}%
\providecommand{\tablefont}{}%
\providecommand{\theadc}[1]{\multicolumn{1}{c}{\thead{{#1}}}}%
\providecommand{\theadl}[1]{\multicolumn{1}{l}{\thead{{#1}}}}%
\providecommand{\theadr}[1]{\multicolumn{1}{r}{\thead{{#1}}}}%""")
		

		def append_simple_row(name, initial_value, value, std_err, tstat, nullvalue, holdfast):
			table.write(r'\\')
			table.write(name)
			table.write(r' & ')
			if display_inital:
				table.write("{:{PARAM}}".format(initial_value, **format     ))
				table.write(r' & ')
			table.write("{:{PARAM}}".format(value , **format))
			table.write(r' & ')
			if holdfast:
				table.write(r'\multicolumn{2}{l}{fixed value}')
				table.write(r' & ')
			else:
				table.write("{:.3g}".format(std_err   , **format))
				table.write(r' & ')
				table.write("{:{TSTAT}}".format(tstat , **format  ))
				table.write(r' & ')
			table.write("{:.1f}".format(nullvalue , **format))

		def append_derivative_row(name, initial_value, value, refers_to, multiplier):
			table.write(r'\\')
			table.write(name)
			table.write(r' & ')
			if display_inital:
				table.write("{:{PARAM}}".format(initial_value, **format     ))
				table.write(r' & ')
			table.write("{:{PARAM}}".format(value , **format))
			table.write(r' & ')
			table.write(r"\multicolumn{{3}}{{l}}{{= {} * {} }}".format(refers_to,multiplier))

		table.write(r'\theadc{Parameter} & ')
		if display_inital:
			table.write(r'\theadc{Initial Value} & ')
		table.write(r'\theadc{Estimated Value} & ')
		table.write(r'\theadc{Std Error} & ')
		table.write(r'\theadc{t-Stat} & ')
		table.write(r'\theadc{Null Value} \\')


		if groups is None:
			for par in self.parameter_names():
				append_simple_row(
					par,
					self.parameter(par).initial_value,
					self.parameter(par).value,
					self.parameter(par).std_err,
					self.parameter(par).t_stat(),
					self.parameter(par).null_value,
					self.parameter(par).holdfast
				)

		else:
			
			## USING GROUPS
			listed_parameters = set([p for p in groups if not isinstance(p,category)])
			for p in groups:
				if isinstance(p,category):
					listed_parameters.update( p.complete_members() )
			unlisted_parameters = (set(self.parameter_names()) | set(self.alias_names())) - listed_parameters


			def write_param_row(p, *, force=False):
				if p is None: return
				if force or (p in self) or (p in self.alias_names()):
					if isinstance(p,category):
						table.write(r'\multicolumn{{ {} }}{{l}}{{ \thead{{ {} }} }}'.format(number_of_columns, p.name))
						for subp in p.members:
							write_param_row(subp)
					else:
						if isinstance(p,rename):
							append_simple_row(par,
								self[p].initial_value,
								self[p].value,
								self[p].std_err,
								self[p].t_stat(),
								self[p].null_value,
								self[p].holdfast
							)
						else:
							pwide = self.parameter_wide(p)
							if isinstance(pwide,ParameterAlias):
								append_derivative_row(pwide.name,
									self.metaparameter(pwide.name).initial_value,
									self.metaparameter(pwide.name).value,
									pwide.refers_to,
									pwide.multiplier
								)
							else:
								append_simple_row(pwide.name,
									pwide.initial_value,
									pwide.value,
									pwide.std_err,
									pwide.t_stat(),
									pwide.null_value,
									pwide.holdfast
								)


			# end def
			for p in groups:
				write_param_row(p)
			if len(groups)>0 and len(unlisted_parameters)>0:
				write_param_row(category("Other Parameters"),force=True)
			if len(unlisted_parameters)>0:
				for p in unlisted_parameters:
					write_param_row(p)
		return table.getvalue()
	latex_param = latex_parameters = latex_params




