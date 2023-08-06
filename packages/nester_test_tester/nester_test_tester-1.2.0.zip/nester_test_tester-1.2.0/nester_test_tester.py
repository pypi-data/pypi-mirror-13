'''This is the "nester.py" module, and it provides one function called
print_lol() which prints lists that may or may not include nested lists.'''

def print_lol(the_list, tab=0):
   for each_item in the_list:
       if isinstance(each_item, list):
               print_lol(each_item, tab+1)
       else:
          for ntab in range(tab):
             print("\t",end='')
          print(each_item)
