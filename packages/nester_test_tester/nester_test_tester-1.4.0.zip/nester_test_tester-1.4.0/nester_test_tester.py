'''This is the "nester.py" module, and it provides one function called
print_lol() which prints lists that may or may not include nested lists.'''
import sys

def print_lol(the_list, indent=False, tab=0, fh=sys.stdout):
   for each_item in the_list:
       if isinstance(each_item, list):
               print_lol(each_item, indent, tab+1, fh)
       else:
          if indent:
             for ntab in range(tab):
                print("\t", end='', file=fh)
          print(each_item, file=fh)
