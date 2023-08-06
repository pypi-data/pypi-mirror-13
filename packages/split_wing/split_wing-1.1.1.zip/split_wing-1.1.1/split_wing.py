#只能处理一个异常
#if语句可读性差

#文件格式发生改变要修改代码

import os


os.chdir('d:\py_wing')
data = open('rilegou.txt')

for each_line in data:
  #if each_line.find(":")!=-1:
  #if not each_line.find(":")==-1:
  try:
    (role,line_spoken)= each_line.split(":",1)
    print(role,end='')
    print(" : ",end='')
    print(line_spoken,end='')
  except:    
    pass
data.close()
