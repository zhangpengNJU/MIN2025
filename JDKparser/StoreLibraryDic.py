import os

import GetLibraryDIC


import subprocess
def runGetMethodJar(path, jarpath=".\\GetAllMethods.jar"):
    p = subprocess.Popen('copy ' + jarpath + " " + path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.communicate()
    p = subprocess.Popen("java -jar GetAllMethods.jar", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         cwd=path)
    p.communicate()



testpath="D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\AllMethods\\"
classmethodpairs=GetLibraryDIC.getDIC(testpath)
typeDic=GetLibraryDIC.typeDic

dupl=GetLibraryDIC.dupl
duplDic=GetLibraryDIC.duplDic
newclassmethodpairs=[]
for c in classmethodpairs:
    if c[0] not in duplDic:
        newclassmethodpairs.append(c)
    else:
        duplDic[c[0]] += 1

classmethodpairs=newclassmethodpairs



for a in dupl:
    os.chdir('D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\')
    print(a[1][:-len(a[1].split('\\')[-1])-1])
    p1=a[1][:-len(a[1].split('\\')[-1])-1]
    p2=a[2][:-len(a[2].split('\\')[-1])-1]
    runGetMethodJar(p1)
    runGetMethodJar(p2)
    classname=a[1][-len(a[1].split('\\')[-1]):][:-5]
    classmethodpairs+=GetLibraryDIC.makeDifferentDicForPKG(p1+"\\AllMethods", classname)
    classmethodpairs+=GetLibraryDIC.makeDifferentDicForPKG(p2+"\\AllMethods", classname)





import pickle

#import subprocess
def writeans(x, outputpath):
    #p = subprocess.Popen('rm -rf ' + outputpath, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #p.communicate()
    content = pickle.dumps(x)
    f = open(outputpath, 'wb')
    f.write(content)
    f.close()


writeans([typeDic,classmethodpairs,duplDic],"D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\libraryDic.pkl")

x=1


duplDic2={}
for d in dupl:
    #if d[1].split("\\")[-1][:-5] not in duplDic2:
        duplDic2[d[1].split("\\")[-1][:-5]]=[d[1].split("\\")[-2]+'.'+d[1].split("\\")[-1][:-5]]
    #else:
        duplDic2[d[1].split("\\")[-1][:-5]].append(d[2].split("\\")[-2]+'.'+d[2].split("\\")[-1][:-5])
