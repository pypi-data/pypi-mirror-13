#这是"nester_wing.py"模块
#提供了一个 print_lol() 函数,
#这个函数的作用是打印列表,
#其中有可能包含嵌套列表
def print_lol(the_list):
  for each_outher in the_list:
    if isinstance(each_outher,list):
      print_lol(each_outher)
    else:
      print(each_outher)
