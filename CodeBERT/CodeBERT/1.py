# from transformers import RobertaConfig, RobertaTokenizer, RobertaForMaskedLM, pipeline
#
# model = RobertaForMaskedLM.from_pretrained("microsoft/codebert-base-mlm")
# tokenizer = RobertaTokenizer.from_pretrained("microsoft/codebert-base-mlm")
# fill_mask = pipeline('fill-mask', model=model, tokenizer=tokenizer)
# # CODE = "if (x is not None) <mask> (x>1)"
# file1 = open("TimeSeries.java", "r+")
# CODE = file1.read()
# print(CODE)
#
#
# outputs = fill_mask(CODE)
# print(outputs)
#
# for output in outputs:
#     print(output['token_str'])
#     print(output['sequence'])




from transformers import RobertaConfig, RobertaTokenizer, RobertaForMaskedLM, pipeline
import re
import io
import subprocess
import csv
import numpy as np
import scipy as sp

# from sklearn import cluster
np.random.seed(0)

from func_timeout import func_set_timeout

import pickle

import os


# pv = '-p Csv -v 2f'


# 1:pv示例：-p Lang -v 1f
def getfixversion(pv, cwdpath):
    p = subprocess.Popen('defects4j checkout ' + pv + ' -w' + cwdpath, shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    p.communicate()


# 2:获得class name：
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


# 3:获取该class 代码全文：
def getclasscode(classname, cwdpath):
    find = "find . -name " + classname.split('.')[-1] + '.java'
    p = subprocess.Popen(find, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwdpath)
    z = p.stdout.read().decode()[:-1]
    p.communicate()
    print("z:", z)
    return z
    # p = subprocess.Popen('cat ' + z, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwdpath)
    # z = p.stdout.read()
    # p.communicate()
    # return z.decode()


# 4:对每一个token进行mask：
# 注释内的内容跳过，空格跳过，换行跳过，标点符号跳过
# 似乎不能删除注释，因为注释有信息，我已试验过，保留注释可以提高预测准确性。


skipdic = {"@Override": 1, 'abstract': 1, 'assert': 1, 'boolean': 1, 'break': 1, 'byte': 1, 'case': 1, 'catch': 1,
           'char': 1, 'class': 1, 'const': 1,
           'continue': 1, 'default': 1, 'do': 1, 'double': 1, 'else': 1, 'enum': 1, 'extends': 1, 'final': 1,
           'finally': 1, 'float': 1, 'for': 1,
           'goto': 1, 'if': 1, 'implements': 1, 'import': 1, 'instanceof': 1, 'int': 1, 'interface': 1, 'long': 1,
           'native': 1, 'new': 1, 'package': 1,
           'private': 1, 'protected': 1, 'public': 1, 'return': 1, 'strictfp': 1, 'short': 1, 'static': 1, 'super': 1,
           'switch': 1, 'synchronized': 1,
           'this': 1, 'throw': 1, 'throws': 1, 'transient': 1, 'try': 1, 'void': 1, 'volatile': 1, 'while': 1, }

model = RobertaForMaskedLM.from_pretrained("microsoft/codebert-base-mlm")
tokenizer = RobertaTokenizer.from_pretrained("microsoft/codebert-base-mlm")
fill_mask = pipeline('fill-mask', model=model, tokenizer=tokenizer)


def mymin(pos):
    if pos-255 < 0:
        return 0
    return pos-255


def mymax(pos, code):
    if pos+255 > len(code):
        return len(code)
    return pos+255


def generate_mutants(path, classname, maskpath, mutpath):
    p = subprocess.Popen("java -jar GenerateMask.jar " + path, shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    p.communicate()
    index = 0
    mask_file = os.listdir(maskpath)
    for f in mask_file:
        file1 = open(maskpath + f, "r+")
        # p = subprocess.Popen("find . -name '.DS_Store' -type f -delete", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd="/Users/luzeyu/Desktop/MyMask/")
        # p.communicate()
        code = file1.read()
        pos = code.find("<mask>")
        print("pos:", pos)
        idx1 = mymin(pos)
        print("idx1:", idx1)
        idx2 = mymax(pos, code)
        print("idx2:", idx2)
        mask_code = code[idx1: idx2]
        print("mask_code:", mask_code)


        outputs = fill_mask(mask_code)
        for output in outputs:
            CODE = code
            mutant_code = CODE.replace('<mask>', output['token_str'])
            print("mutant_code: ", mutant_code)
            # mutant_code = output
            write_mutants(mutant_code, index, classname, mutpath)
            index += 1


# 5：调用codebert,放在方法外，全局只用下载一次。
# 已经前置，第五步改为过滤编译不通过的mutant。不需要！，我们只要看生成的变异体最好的表现，所以先计算评价指标，再看最好的变异体能否通过编译。


def clean0224(cwdpath):
    p = subprocess.Popen('rm -rf' + cwdpath, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.communicate()


# 8:检查能否编译通过


# 7:获取realfault，可以直接上main函数了
# getfixversion(pv)


# BLEU是不行的了。我们需要为mutant编译计算指标。


# 文件名包含了修改的class，mutant编号
def write_mutants(mutantCode, index, classname, outputpath):
    # p = subprocess.Popen('mkdir MyMutants', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # p.communicate()
    f = open(outputpath + str(index) + "-" + classname, 'w')
    f.write(mutantCode)
    f.close()


def get_all_mutant_list(mutantpath):
    mlist = os.listdir(mutantpath)
    return mlist


# 覆盖原始类
def writein(code, classname, cwdpath):
    find = "find . -name " + classname.split('.')[-1] + '.java'
    p = subprocess.Popen(find, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwdpath)
    z = p.stdout.read().decode()[:-1]
    p.communicate()
    z = z.split('\n')[0]
    f = open(cwdpath + z, 'wb')
    f.write(code.encode())
    f.close()

# writein(ncode)


# run test
@func_set_timeout(300)
def runtest(cwdpath):
    # defects4j test
    p = subprocess.Popen('defects4j test -r', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwdpath)
    z = p.stdout.read().decode()[:-1]
    p.communicate()
    if 'Failing tests:\n' in z:
        ft = z.split('-')[1]
        return ft
    else:
        return z


def getnumberofalltests(cwdpath):
    p = subprocess.Popen('cat all_tests', shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, cwd=cwdpath)
    z = p.stdout.read()
    z = str(z)
    p.communicate()
    lis = z.split("\\n")
    return len(lis) - 1


def gettriggertests(cwdpath):
    p = subprocess.Popen('cat defects4j.build.properties', shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, cwd=cwdpath)
    z = p.stdout.read()
    z = str(z)
    p.communicate()
    lis = z.split('d4j.tests.trigger=')
    triggertests = lis[-1][:-3]
    # c = triggertest.count("::")
    # if c > 1:
    #    print('more than one triggertests')
    return triggertests


def writeans(x, outputpath):
    # p = subprocess.Popen('rm -rf ' + outputpath, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # p.communicate()
    content = pickle.dumps(x)
    f = open(outputpath, 'wb')
    f.write(content)
    f.close()
    return 0



# if __name__ == "__main__":
#     for i in range(0, 1):
#         for j in range(project[i][1], project[i][2] + 1):
#             if j not in project[i][3]:
#                 # pv示例：-p Lang -v 1f
#                 pv = '-p ' + project[i][0] + ' -v ' + str(j) + 'f'
#                 print("pv:", pv)
#                 getfixversion(pv)
#                 classname = getclassname()
#                 print("classname:", classname)
#                 code = getclasscode(classname)
#                 # print("code:", code)
#                 mutantlist = maskcode(code)
#                 print("mutantlist:", mutantlist)


    # generate_mutants("./TimeSeries.java")

project = [['Chart', 1, 26, [1, 2]], ['Cli', 1, 40, [6]], ['Closure', 1, 176, [63, 93]], ['Codec', 1, 18, []],
               ['Collections', 25, 28, []], ['Compress', 1, 47, []], ['Csv', 1, 16, []], ['Gson', 1, 18, []],
               ['JacksonCore', 1, 26, []], ['JacksonDatabind', 1, 112, []], ['JacksonXml', 1, 6, []],
               ['Jsoup', 1, 93, []],
               ['JxPath', 1, 22, []], ['Lang', 1, 65, [2]], ['Math', 1, 106, []], ['Mockito', 1, 38, []],
               ['Time', 1, 27, [21]], ]



ans=[]


maskpath = "./"
mutpath = "./"
#respath = "/Users/luzeyu/Desktop/MyCodeBERT/"

cwdpath = "/tmp/0509"
workpath = os.getcwd()

for i in range(len(project)):
    pv = '-p ' + project[i][0] + ' -v ' + str(1) + 'f'
    print("pv:", pv)
    getfixversion(pv, cwdpath)
    import time
    start=time.time()
    classname = getclassname(cwdpath)
    path = getclasscode(classname, cwdpath)
    print("path:", path)
    path = path.replace("./", cwdpath)
    print("path:", path)
    generate_mutants(path, classname, maskpath, mutpath)
    end=time.time()
    execution_time = end_time - start_time
    mutantlist = get_all_mutant_list(mutpath)
    ans.append([execution_time,len(mutantlist)])
    




