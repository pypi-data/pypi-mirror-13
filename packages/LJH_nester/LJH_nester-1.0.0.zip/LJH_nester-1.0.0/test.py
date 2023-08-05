# This is my module for displaye a multiple layers list
def print_lol(param):
	if isinstance(param, list):
		for inner_list in param:
			print_lol(inner_list)
	else:
		print(param)
