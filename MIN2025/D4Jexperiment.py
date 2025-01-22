# 只对bug相关的类进行变异


import subprocess

import os
import GenerateMutants
import runMutant

import pickle


# 1.获取类，返回的多个类用逗号隔开。com.google.javascript.jscomp.RemoveUnusedVars一个实例。
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


def writeans(x, outputpath):
    p = subprocess.Popen('rm -rf ' + outputpath, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.communicate()
    content = pickle.dumps(x)
    f = open(outputpath, 'wb')
    f.write(content)
    f.close()


# 1:pv示例：-p Lang -v 1f
def getfixversion(pv, cwdpath, workpath):
    p = subprocess.Popen('defects4j checkout ' + pv + ' -w ' + cwdpath, shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, cwd=workpath)
    p.communicate()


def clean(cwdpath):
    p = subprocess.Popen('rm -rf ' + cwdpath, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.communicate()

import InheritanceAnalysis
def dealwithonepv(p, v, cwdpath, workpath):
    pv = "-p " + p + " -v " + v + "f"
    getfixversion(pv, cwdpath, workpath)
    classname = getclassname(cwdpath)
    cps = findclasspath(classname, cwdpath)
    # cp是一个可以直接打开的java文件
    jarpath = workpath + "/GetAllMethods.jar"
    GenerateMutants.runGetMethodJar(cwdpath, jarpath)
    GenerateMutants.cpRmvCmtJar(cwdpath, workpath + "/RemoveComment.jar")
    classmethodpairs = GenerateMutants.getDIC(cwdpath + "/AllMethods")
    MethodClassDIC = GenerateMutants.getMethodClassDIC(classmethodpairs)
    AllDic=InheritanceAnalysis.MakeTreeFromOPath(cwdpath,GenerateMutants.libraryDic)
    os.chdir(cwdpath)
    for cp in cps:
        proc = subprocess.Popen("java -jar RemoveComment.jar " + cp, shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, cwd=cwdpath)
        proc.communicate()
        GenerateMutants.generateMutantsForOneClass(cp, MethodClassDIC, classmethodpairs, AllDic, 10)
        # 原代码也拷贝走
        runMutant.copy(cp, workpath + "/FixCode/" + p + v + cp.split("/")[-1])
    # 变异体生成在了Mutants文件夹下，先把它复制走。
    runMutant.copy("./Mutants", workpath + "/" + p + v)
    # 执行变异体
    mlist = runMutant.getAllmutantList(mutantpath="./Mutants/")
    ans = []
    for m in mlist:
        try:
            ans.append(runMutant.dealwithonemutant(m, cwdpath))
            # 正确代码还原
            originpath = "./" + m.split("-.-")[1].replace("-", "/")
            runMutant.copy(workpath + "/FixCode/" + p + v + m.split("-")[-1], originpath)
        except:
            originpath = "./" + m.split("-.-")[1].replace("-", "/")
            runMutant.copy(workpath + "/FixCode/" + p + v + m.split("-")[-1], originpath)
            print([m, "超时"])
            ans.append([m, "超时"])
            continue
    outputpath = workpath + "/FixCode/" + p + v + ".pkl"
    writeans(ans, outputpath)
    os.chdir(workpath)


'''
project = [['Chart', 1, 26, [1, 2,3,4,5]], ['Cli', 1, 40, [6]], ['Closure', 1, 176, [63, 93]], ['Codec', 1, 18, []],
           ['Collections', 25, 28, []], ['Compress', 1, 47, []], ['Csv', 1, 16, []], ['Gson', 1, 18, []],
           ['JacksonCore', 1, 26, []], ['JacksonDatabind', 1, 112, []], ['JacksonXml', 1, 6, []], ['Jsoup', 1, 93, [1]],
           ['JxPath', 1, 22, []], ['Lang', 63, 65, [2]], ['Math', 1, 106, []], ['Mockito', 1, 38, []],
           ['Time', 1, 27, [21]], ]
           
project = [['Chart', 1, 26, [14, 18]], ['Cli', 1, 40, [6, 13, 16, 21, 30, 31, 34, 36]], ['Closure', 1, 176, [30, 34, 37, 47, 54, 63, 72, 79, 89, 90, 93, 103, 106, 110, 134, 135, 136, 137, 138, 141, 142, 143, 144, 147, 148, 149, 153, 154, 155, 157, 158, 162, 163, 165, 167, 169, 171, 173, 174]],
            ['Codec', 1, 18, [1, 8, 13, 14]], ['Collections', 25, 28, []], ['Compress', 1, 47, [4, 29, 33, 42]], ['Csv', 1, 16, [13]], ['Gson', 1, 18, [4, 9]],
           ['JacksonCore', 1, 26, [1, 2, 9, 12, 18, 19, 24]], ['JacksonDatabind', 1, 112, [10, 13, 15, 22, 25, 30, 38, 48, 52, 53, 59, 61, 65, 73, 79, 90, 95, 103, 109, 111]],
           ['JacksonXml', 1, 6, []], ['Jsoup', 1, 93, [3, 14, 21, 22, 23, 28, 31, 52, 56, 58, 60, 63, 65, 71, 83, 87, 91, 92]],
           ['JxPath', 1, 22, [1, 4, 7, 9, 11, 13, 16, 17, 19]], ['Lang', 1, 65, [2]], ['Math', 1, 106, [1, 4, 6, 14, 22, 71, 77, 98]],
           ['Mockito', 1, 38, [14, 16, 17, 19, 30]], ['Time', 1, 27, [1, 2, 12, 21, 26]], ]
           

'''

# 先把关键的做了
# project = [['Time', 22, 27, [1, 2, 12, 19, 20, 21, 23, 25, 26]], ]
# project = [
#             ['Codec', [17]],
#             ['Cli', [3, 39, 40]],
#             ['Chart', [20]],
#             ['Math', [5]],
#            ]
# project = [
#             ['Mockito', [12, 15, 22, 23, 28, 29, 31, 37, 38]],
#             ['Jsoup', [1, 2, 5, 7, 8, 10, 11, 12, 13, 15, 16, 17, 18, 19, 20, 24, 25, 26, 27, 29, 30, 32, 33, 34, 35,
#                        36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 53, 54, 69, 70, 84, 85, 86, 88,
#                        89]],
#             ['JacksonDatabind', [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 14, 16, 17, 18, 19, 20, 21, 23, 24, 26, 27, 28, 29,
#                                  31, 32, 33, 34, 35, 36, 37, 39, 40, 41, 42, 43, 44, 45, 46, 47, 49, 55, 56, 57, 58, 62,
#                                  69, 71, 72, 77]],
#             ['Closure', [1, 3, 5, 8, 9, 12, 13, 16, 20, 23, 24, 28, 29, 36, 45, 46, 50, 53, 55, 58, 67, 74,
#                          76, 78, 83, 85, 87, 100, 101, 102, 105, 107, 108, 111, 114, 121]],
#             ['Math', [5, 15]],
#            ]

project = [
            ['Jsoup', [90, 93]],
            ['Math', [11, 44, 72]],
            ['Time', [19, 23, 25]],
           ]

project = [['Chart', 1, 26, [14, 18]], ['Cli', 1, 40, [6, 13, 16, 21, 30, 31,32, 34,35, 36]], ['Closure', 1, 176,
                                                                                         [30, 34, 37, 47, 54, 63, 72,
                                                                                          79, 89, 90, 93, 103, 106, 110,
                                                                                          134, 135, 136, 137, 138, 141,
                                                                                          142, 143, 144, 147, 148, 149,
                                                                                          153, 154, 155, 157, 158, 162,
                                                                                          163, 165, 167, 169, 171, 173,
                                                                                          174]],
           ['Codec', 1, 18, [1, 8, 13, 14]], ['Collections', 25, 28, []], ['Compress', 1, 47, [4, 29, 33, 42]],
           ['Csv', 1, 16, [13]], ['Gson', 1, 18, [4, 9]],
           ['JacksonCore', 1, 26, [1, 2, 9, 12, 18, 19, 24]], ['JacksonDatabind', 1, 112,
                                                               [10, 13, 15, 22, 25, 30, 38, 48, 52, 53, 59, 61, 65, 73,
                                                                79, 90, 95, 103, 109, 111]],
           ['JacksonXml', 1, 6, []],
           ['Jsoup', 1, 93, [3, 14, 21, 22, 23, 28, 31, 52, 56, 58, 60, 63, 65, 71, 83, 87, 91, 92]],
           ['JxPath', 1, 22, [1, 4, 7, 9, 11, 13, 16, 17, 19]], ['Lang', 1, 65, [2]],
           ['Math', 1, 106, [1, 4, 6, 14, 22, 71, 77, 98]],
           ['Mockito', 1, 38, [14, 16, 17, 19, 30]], ['Time', 1, 27, [1, 2, 12, 21, 26]], ]

# def main():

cwdpath="/tmp/0509"
workpath=os.getcwd()
os.mkdir('FixCode',workpath)
'''
p="Cli"
v="35"
dealwithonepv(p, v, cwdpath, workpath)

p="Cli"
v="32"
dealwithonepv(p, v, cwdpath, workpath)

'''
for i in range(15,18):
    for j in range(project[i][1], project[i][2] + 1):
        print("i:", i, "j:", j, "project[i][0]:", project[i][0], "project[i][1]:", project[i][1])
        try:
            clean(cwdpath)
            p = project[i][0]
            v = str(j)
            dealwithonepv(p, v, cwdpath, workpath)
        except:
            continue

# for i in range(0, 1):
#     for j in range(project[i][1], project[i][2] + 1):
#         print("i: ", i, "project[i][0]: ", project[i][0], "project[i][1]: ", project[i][1], "project[i][2]: ", project[i][2], "project[i][3]: ", project[i][3])
#         if j not in project[i][3]:
#             try:
#                 clean(cwdpath)
#                 p = project[i][0]
#                 v = str(j)
#                 dealwithonepv(p, v, cwdpath, workpath)
#             except:
#                 continue
