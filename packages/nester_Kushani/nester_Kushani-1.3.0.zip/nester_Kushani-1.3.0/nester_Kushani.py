"""This is the “nester.py" module, and it provides one function called
print_lol() which prints lists that may or may not include nested lists."""


"""This function takes a positional argument called “the_list", which is any
Python list (of, possibly, nested lists). Each data item in the provided list
is (recursively) printed to the screen on its own line."""


def print_lol(the_list, indent=False, level=0):
        for each_item in the_list:
                if isinstance(each_item,list):
                        print_lol(each_item, indent, level+1)
                else:
                        if indent:
                                for tab_stop in range(level):
                                        print("\t", end='')
                        print(each_item)

		
        
        

        
	




# function 1
"""
def print_lol(the_list):
     
	for each_item in the_list:
		if isinstance(each_item,list):
			print_lol(each_item)
		else:
			print(each_item)


"""

"""
movies = [
"The Holy Grail", 1975, "Terry Jones & Terry Gilliam", 91,
["Graham Chapman",
["Michael Palin", "John Cleese", "Terry Gilliam", "Eric Idle", "Terry Jones"]]]

print_lol(movies,0)
"""
"""
names = ['John', 'Eric', ['Cleese', 'Idle'], 'Michael', ['Palin']]
print_lol(names,True,0)
"""
