import os
os.chdir('d:\py_wing')
count=10
try:
  #data = open('missing.txt')
  with open('missing.txt','w') as data:
    while count>0:
      print("It's...",file=data)
      count=count-1
except OSError as err:
  print('File error'+str(err))
