'''this is a nest-list printer module
'''

'''movies = ["The Holy Grail", 1975, "Terry Jones & Terry Gilliam", 91, 
                ["Graham Chapman", ["Michael Palin", "John Cleese",
                        "Terry Gilliam", "Eric Idle", "Terry Jones"]]]
'''

def print_lol(your_list):
	'''this functions goes 3 lnesting level deep'''
	for item in your_list:
		if isinstance(item,list):
			for nested_item  in item:
				if isinstance(nested_item,list):
					for deeper_nested_item in nested_item:
						print deeper_nested_item
				else:
					print nested_item
		else:
			print item