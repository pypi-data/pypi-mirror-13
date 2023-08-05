"""This is the "nester.py" module and it provides one function called print_lol()
   which prints lists that may or may not include nested lists."""
def print_lol (the_list, ident=False ,level=0):
     """This function takes one positional argument called "the_list", which
        is any Python list (of - possibly - nested lists). Each data item in the
        provided list is (recursively) printed to the screen on it’s own line."""
     for item in the_list:
        if isinstance(item, list):
            print_lol(item, ident, level + 1);
        else:
            if ident:
                for i in range(level):
                    print("\t", end='');
            print(item);