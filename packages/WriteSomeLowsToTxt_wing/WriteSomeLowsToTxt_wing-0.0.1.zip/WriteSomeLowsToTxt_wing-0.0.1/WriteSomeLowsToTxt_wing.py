#FilePath:根目录
#FileName:创建的文件名
#FileContent:文件内容
#lows:行数
import os
def writefile(FilePath,FileName,FileContent,lows=10):
  os.chdir(FilePath)
  
  try:
  #data = open('missing.txt')
    with open(FileName,'w') as TempFile:
      while lows>0:
        print(FileContent,file=TempFile)
        lows=lows-1
  except OSError as err:
    print('File error'+str(err))
