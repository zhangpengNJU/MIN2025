import re
import io
import subprocess
import csv
import numpy as np


np.random.seed(0)

# 1获取全部变异体
import os


key= 'org.apache.commons.lang3.math.NumberUtils'.replace(".",'-')
mutantpath="/home/fl/Desktop/DeepMu/DeepMutation/dist/data/out/Lang/1f"
def getAllMutantList(mutantpath, key):
    mutant_list = []
    # 定义递归函数来查找符合条件的文件夹
    def find_mutants(folder):
        for item in os.listdir(folder):
            item_path = os.path.join(folder, item)
            if os.path.isdir(item_path):
                # 如果是文件夹，且名称为"mutants"，则在其下查找符合条件的文件
                #if item == "mutants":
                    find_mutants(item_path)
                #else:
                #    continue
            elif item.endswith(key+".java"):
                # 如果是以".java"结尾且包含指定关键词的文件，则将其所在文件夹路径添加到mutant_list中
                mutant_list.append(item_path)
    # 在给定路径下查找符合条件的文件夹
    find_mutants(mutantpath)
    return mutant_list


l=getAllMutantList(mutantpath, key)



def copy(path1, path2):
    p = subprocess.Popen('cp -rf ' + path1 + ' ' + path2, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.communicate()


def gettriggertests(cwdpath):
    p = subprocess.Popen('cat defects4j.build.properties', shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, cwd=cwdpath)
    z = p.stdout.read()
    z = str(z)
    p.communicate()
    lis = z.split('d4j.tests.trigger=')
    triggertest = lis[-1][:-3]
    # c = triggertest.count("::")
    # if c > 1:
    #    print('more than one triggertests')
    return triggertest


def getnumberofalltest(cwdpath):
    p = subprocess.Popen('cat all_tests', shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, cwd=cwdpath)
    z = p.stdout.read()
    z = str(z)
    p.communicate()
    lis = z.split("\\n")
    return len(lis) - 1


# 测试
import time
import func_timeout
from func_timeout import func_set_timeout


@func_set_timeout(300)
def runtest(cwdpath):
    # defects4j test
    # -r只执行相关测试用例
    p = subprocess.Popen('defects4j test -r', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwdpath)
    z = p.stdout.read().decode()[:-1]
    p.communicate()
    if 'Failing tests:\n' in z:
        ft = z.split('-')[1]
        return ft
    else:
        return z


def getclassname(cwdpath):
    p = subprocess.Popen('cat defects4j.build.properties', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         cwd=cwdpath)
    z = p.stdout.read()
    p.communicate()
    lis = z.decode().split('d4j.classes.modified=')
    c = lis[1]
    lis = c.split('d4j.classes.relevant')
    classname = lis[0][:-1]
    return classname


def findclasspath(classname, cwdpath):
    lis = classname.split(",")
    ans = []
    for l in lis:
        find = "find . -name " + l.split('.')[-1] + '.java'
        print("find:", find)
        p = subprocess.Popen(find, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwdpath)
        z = p.stdout.read().decode()[:-1]
        p.communicate()
        # 找到多个：检查文件夹位置
        if "\n" in z:
            zs = z.split("\n")
            for zi in zs:
                d = zi.split("/")[-2]
                if d == l.split(".")[-2]:
                    ans.append(zi)
                    break
        elif z != "":
            ans.append(z)
    return ans


#先找到类，再找到文件的位置，



# 2.处理一个变异体：复制到指定位置，再run test. 输入的m是m的地址




def dealwithonemutant(m,originpath, cwdpath):
    # ans=[]
    # 先要把origin移到一个暂存点，测试完移动回来。
    # '/home/fl/Desktop/DeepMu/DeepMutation/dist/data/out/Lang/1f/50len_ident_lit/mutants/168_data-in-Lang-1f-src-main-java-org-apache-commons-lang3-math-NumberUtils.java'
    mutantpath = m
    #originpath = "./" + m.split("-.-")[1].replace("-", "/")
    # originpath = "./source/org/jfree/data/time/TimeSeries.java"
    tmppath = '/tmp/1.java'
    copy(originpath, tmppath)
    copy(mutantpath, originpath)
    testresult = runtest(cwdpath)
    triggertest = gettriggertests(cwdpath)
    numberofalltests = getnumberofalltest(cwdpath)
    ans = [m, testresult, numberofalltests, triggertest]
    print([testresult, numberofalltests, triggertest])
    copy(tmppath, originpath)
    print("ans: ", ans)
    return ans




m='/home/fl/Desktop/DeepMu/DeepMutation/dist/data/out/Lang/1f/50len_ident_lit/mutants/170_data-in-Lang-1f-src-main-java-org-apache-commons-lang3-math-NumberUtils.java'
#originpath="/home/fl/Desktop/DeepMu/DeepMutation/dist/data/in/Lang/1f/src/main/java/org/apache/commons/lang3/math/NumberUtils.java"
originpath="/home/fl/Desktop/DeepMu/DeepMutation/dist/data"+m.split("mutants/")[1].split('_data')[1].replace("-","/")
#cwdpath要指向checkout目录/
cwdpath="/home/fl/Desktop/DeepMu/DeepMutation/dist/data"+m.split("mutants/")[1].split('_data')[1].split('f-')[0].replace("-","/")+"f"
#dealwithonemutant(m,originpath, cwdpath)


#prepath="/home/fl/Desktop/DeepMu/DeepMutation/dist/data"
def runallmutant(mlist, prepath):
    ans = []
    # mlist=getAllmutantList(mutantpath="./Mutants/")
    for m in mlist:
        originpath = prepath + m.split("mutants/")[1].split('_data')[1].replace("-", "/")
        cwdpath = prepath + m.split("mutants/")[1].split('_data')[1].split('f-')[0].replace("-", "/") + "f"
        try:
            ans.append(dealwithonemutant(m,originpath, cwdpath))
        except:
            tmppath = '/tmp/1.java'
            #copy(tmppath, originpath)
            copy(tmppath, originpath)
            print([m, "超时"])
            ans.append([m, "超时"])
            continue
    return ans


#存储结果
import pickle


def writeans(x):
    p = subprocess.Popen('rm -rf /home/fl/Desktop/ans0429.pkl', shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    p.communicate()
    content = pickle.dumps(x)
    f = open("/home/fl/Desktop/ans0429.pkl", 'wb')
    f.write(content)
    f.close()




#main:
#prepath="/home/fl/Desktop/DeepMu/DeepMutation/dist/data"
def dealwithonepv(p, v, prepath,ans):
    pv = "-p " + p + " -v " + v + "f"
    classname = getclassname(prepath+"/in/"+p+'/'+v+"f")
    #cps = findclasspath(classname, cwdpath)
    key = classname.replace(".", '-')
    mutantpath = prepath+"/out/"+p+'/'+v+"f"
    mlist = getAllMutantList(mutantpath, key)
    ans.append(runallmutant(mlist, prepath))
    return ans




ans=[]
prepath="/home/fl/Desktop/DeepMu/DeepMutation/dist/data"
project = [
['Math', 1, 106, []], ['Mockito', 1, 38, []],
           ['Time', 1, 27, [21]]]

for i in range(1, 6):
    for j in range(project[i][1], project[i][2] + 1):
        #print("i:", i, "j:", j, "project[i][0]:", project[i][0], "project[i][1]:", project[i][1])
        if j not in project[i][3]:
            try:
                p = project[i][0]
                v = str(j)
                pv = "-p " + p + " -v " + v + "f"
                ans=dealwithonepv(p, v, prepath,ans)
            except:
                print("i:", i, "j:", j, " error")
                continue

writeans(ans)
    