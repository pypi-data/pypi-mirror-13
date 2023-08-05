""" This is my first module: nester.py for python,
	and it provides one function called print_lol.
	The following code is learned from book: <Head First Python>. """
def print_lol(the_list, indent=False, level=0, out=sys.stdout):

	""" The function checks wether the 'the_list' has a nest list or not.
		if it has a nest list, then call itself again(recursive). if not,
		print the whole list.
		A second argument called "indent" is used to adding extra intent to printing
		A third argument called "level" is used to insert tab-stops when
		 a nested list is ecountered.
		A forth argument called "out" is used to stand for the destination where data go"""

# comments

	for ei in the_list:
		if isinstance(ei, list):
			print_lol(ei, indent, level+1, out)
		else:
			if indent==True:
				for tab_stops in range(level):
					print('\t', end='', file=out)
			print(ei, file=out)