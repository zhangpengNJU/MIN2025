# 脚本要有管理员权限

# from transformers import RobertaConfig, RobertaTokenizer, RobertaForMaskedLM, pipeline
import re
import io
import subprocess
import csv
import numpy as np
# import scipy as sp

# from sklearn import cluster
np.random.seed(0)

# 1获取全部变异体
import os


def getAllmutantList(mutantpath="./Mutants/"):
    mlist = os.listdir(mutantpath)
    return mlist


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


# 2.处理一个变异体：复制到指定位置，再run test
def dealwithonemutant(m, cwdpath):
    # ans=[]
    # 先要把origin移到一个暂存点，测试完移动回来。
    mutantpath = "./Mutants/" + m
    originpath = "./" + m.split("-.-")[1].replace("-", "/")
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


# cwdpath="/tmp/0224"

# ans=dealwithonemutant(m,cwdpath)

def runallmutant(mlist, cwdpath):
    ans = []
    # mlist=getAllmutantList(mutantpath="./Mutants/")
    for m in mlist:
        try:
            ans.append(dealwithonemutant(m, cwdpath))
        except:
            mutantpath = "./Mutants/" + m
            originpath = "./" + m.split("-.-")[1].replace("-", "/")
            # originpath = "./source/org/jfree/data/time/TimeSeries.java"
            tmppath = '/Users/luzeyu/Desktop/mytmp/1.java'
            copy(tmppath, originpath)
            print([m, "超时"])
            ans.append([m, "超时"])
            continue
    return ans


import pickle


def writeans(x):
    p = subprocess.Popen('rm -rf /home/fl/Desktop/ans1201.pkl', shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    p.communicate()
    content = pickle.dumps(x)
    f = open("/home/fl/Desktop/ans1201.pkl", 'wb')
    f.write(content)
    f.close()

# writeans(ans)


if __name__ == "__main__":
    # mlist = getAllmutantList(mutantpath="/Users/luzeyu/Desktop/jfreechart/chart_3_fixed/source/org/jfree/data/time
    # /AllMethods/Mutants/")
    mlist = getAllmutantList(mutantpath="/Users/luzeyu/Desktop/jfreechart/chart_3_fixed/Mutants/")
    print("mlist: ", mlist)

    cwdpath = "/Users/luzeyu/Desktop/jfreechart/chart_3_fixed/"
    # runallmutant(mlist, cwdpath)

    # m = "39。.。source。org。jfree。data。time。TimeSeries.java"
    #
    # mutantpath = "./Mutants/" + m
    # originpath = "./" + m.split("。.。")[1].replace("。", "/")
    # tmppath = './tmp/1.java'
    #
    # print("mutantpath: ", mutantpath)
    # print("originpath: ", originpath)
    # print("tmppath: ", tmppath)
