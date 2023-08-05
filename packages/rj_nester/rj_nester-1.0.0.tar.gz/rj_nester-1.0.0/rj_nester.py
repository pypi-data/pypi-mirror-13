#This is the 'nester.py' module, and it provides one function called
#recur_fun() which prints lists that may or may not include nested lists.

def recur_fun(fun_list):

#This function takes a positional argument called 'fun_list', which is any
#Python list (of, possibly, nested lists). Each data item in the provided list is (recursively) printed to the screen on its own line.

	for each_rose in fun_list:
		if(isinstance(each_rose, list)):
			recur_fun(each_rose)
		else:
			print(each_rose)
