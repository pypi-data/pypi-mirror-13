'''this is moudle memory
'''
def print_lol(the_list,indent=False,level=0):
    '''this is the def memory'''
    for each_item in the_list:
         if isinstance(each_item,list):
             print_lol(each_item,indent,level+1)
         else:
             if indent:
                 for stepx in range(level):
                     print ("\t",end="")
             else:
                 print(each_item)
