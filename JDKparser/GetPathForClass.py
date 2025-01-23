pathDic={}


import os
def getAllClasses(path, dirlist=[], filelist=[]):
    flist = os.listdir(path)
    for filename in flist:
        subpath = os.path.join(path, filename)
        if os.path.isdir(subpath):
            dirlist.append(subpath)  # 如果是文件夹，添加到文件夹列表中
            getAllClasses(subpath, dirlist, filelist)  # 向子文件内递归
        if os.path.isfile(subpath):
            if subpath.endswith(".java"):
                filelist.append(subpath)  # 如果是文件，添加到文件列表中
    return dirlist, filelist


path=".\\jdk-7fcf35286d52\\src\\share\\classes\\java"
dirlist,filelist=getAllClasses(path)


for f in filelist:
    classname=f.split('\\')[-1][:-5]
    classpackage=f.split('classes\\java\\')[1].split("\\")[0]
    if classname not in pathDic:
        pathDic[classname]=[classpackage]
    else:
        pathDic[classname].append(classpackage)




path2=".\\jdk-7fcf35286d52\\src\\share\\classes\\java\\lang"
dirlist1,filelist1=getAllClasses(path2)
nflist=[]
for f in filelist1:
    if f.startswith(path2):
        if "\\" not in f[len(path2)+1:]:
            nflist.append(f[len(path2)+1:-5])


dic={}
for f in nflist:
    if f not in dic:
        dic[f]=1




import pickle

#import subprocess
def writeans(x, outputpath):
    #p = subprocess.Popen('rm -rf ' + outputpath, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #p.communicate()
    content = pickle.dumps(x)
    f = open(outputpath, 'wb')
    f.write(content)
    f.close()


writeans(pathDic,".\\libraryPathDic.pkl")


m=1