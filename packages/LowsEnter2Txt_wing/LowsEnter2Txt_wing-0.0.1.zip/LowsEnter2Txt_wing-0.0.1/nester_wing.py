#这是"nester.py"模块
#提供了一个 print_lol() 函数,
#这个函数的作用是打印列表,

#其中有可能包含嵌套列表

#添加列表内缩进功能

#添加indent属性,可对是否打印进行选择

#添加文件属性 fn  ,内嵌进with_as.py  实现换行输出txt
import sys
def print_lol(the_list,indent=False,level=0,fh=sys.stdout):
  for each_outher in the_list:
    if isinstance(each_outher,list):
      print_lol(each_outher,indent,level+1,fh)
    else:
      if indent:
        #print('\t'*level,end='',file=fh)
        for tab_stop in range(level):
          print('\t',end='',file=fh)
      print(each_outher,file=fh)
