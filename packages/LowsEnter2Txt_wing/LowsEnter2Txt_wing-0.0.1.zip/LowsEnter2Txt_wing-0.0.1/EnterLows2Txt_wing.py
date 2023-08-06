#换行写进txt
import os
import nester_wing
man=[]
other=[]
os.chdir('d:/nester')
try:
  data = open('666.txt')
  for each_line in data:
    try:
      (role,line_spoken)= each_line.split(":",1)
      line_spoken= line_spoken.strip()
      if role=='Man':
        man.append(line_spoken)
      elif role=='Other Man':
        other.append(line_spoken)
    except ValueError:
      print("ValueError===================================================值错误")
  data.close()
except FileNotFoundError:
  print("FileNotFoundError:your have the not disk")
except OSError:
  print('OSError: 文件名不正确')
"""-----------------------------"""
try:
  with open("manout.txt","w") as mout:
    nester_wing.print_lol(man,fh=mout)
  with open("otherout.txt","w") as oout:
    nester_wing.print_lol(other,fh=oout)
except e:
  print('异常:'+e)
