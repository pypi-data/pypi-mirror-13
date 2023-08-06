"""This is the "list_sweep.py" module. It provides one fuction called 'list_sweep' which prints lists that may or may not contain inner lists."""

def list_sweep(any_list):

	"""This function takes a positional arguement called "any_list", which is any Python list (which may include inner lists). Each data item within the list, and its inner list(s), respectively, is printed, recursively, to the screen on its own line."""

	for each_item in any_list:
		if isinstance(each_item, list):
			list_sweep(each_item)
		else:
			print(each_item)

