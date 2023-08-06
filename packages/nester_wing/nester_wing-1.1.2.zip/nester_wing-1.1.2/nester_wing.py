#这是"nester_wing.py"模块
#兼容性API
def print_lol(the_list,level=0):
  for each_outher in the_list:
    if isinstance(each_outher,list):
      print_lol(each_outher,level+1)
    else:
      for tab_stop in range(level):
        print('\t',end='')
      print(each_outher)

