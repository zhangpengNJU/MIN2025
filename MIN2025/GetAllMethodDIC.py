def readmethdpath(javapath):
    f = open(javapath)
    lines = f.read()
    # print(lines)
    f.close()
    return lines


# 删除注释(剩下一种解决不了的：传入字符串参数，参数是网址，里面有\\,会被当成行注释删除）
def deletecomment(code):
    code = code.replace("\n", " \n ")
    code = code.replace("/*", " /* ")
    ncode = ''
    lis = code.split(' ')
    while '' in lis:
        lis.remove('')
    # 代表/*块注释
    incomment = 0
    skip = 0
    for i in range(0, len(lis)):
        # print([i,incomment])
        if skip == 1:
            skip = 0
            continue
        if incomment == 0:
            # print([i, incomment])
            if lis[i] == '/*' or lis[i] == '*/*':
                # if lis[i + 1] == '*':
                incomment = 1
            elif lis[i].startswith('/*'):
                incomment = 1
            else:
                ncode = ncode + ' ' + lis[i]
        else:
            # print([i, incomment])
            if lis[i] == '/*':
                # skip=1
                incomment = 1
            if lis[i] == '*/' or lis[i] == '*/*':
                # skip = 1
                incomment = 0
            if lis[i].endswith('*/'):
                incomment = 0
    code = ncode
    l = code.split('//')
    while len(l) > 1:
        l2 = l[1].split('\n')
        CODE = l[0] + ' /* ' + l2[0] + ' */ ' + l[1][len(l2[0]):]
        for i in range(2, len(l)):
            CODE = CODE + '//' + l[i]
        code = CODE
        l = CODE.split('//')
    ncode = ''
    lis = code.split(' ')
    while '' in lis:
        lis.remove('')
    # 代表/*块注释
    incomment = 0
    skip = 0
    for i in range(0, len(lis)):
        # print([i,incomment])
        if skip == 1:
            skip = 0
            continue
        if incomment == 0:
            # print([i, incomment])
            if lis[i] == '/*' or lis[i] == '*/*':
                # if lis[i + 1] == '*':
                incomment = 1
            else:
                ncode = ncode + ' ' + lis[i]
        else:
            # print([i, incomment])
            if lis[i] == '/*':
                # skip=1
                incomment = 1
            if lis[i] == '*/' or lis[i] == '*/*':
                # skip = 1
                incomment = 0
    return ncode


def preprocess(code):
    check = code.startswith(" ") or code.startswith("\n")
    while check:
        code = code[1:]
        while code.startswith("@"):
            code = code[len(code.split("\n")[0]) + 1:]
        check = code.startswith(" ") or code.startswith("\n")
    # 遇到synchronized，删除该词
    code = code.replace("\n", "")
    if "synchronized " in code[:30]:
        code = code[:30].replace("synchronized ", "") + code[30:]
    if code.startswith("public"):
        code = code[len("public") + 1:]
    elif code.startswith("private"):
        code = code[len("private") + 1:]
    elif code.startswith("default"):
        code = code[len("default") + 1:]
    elif code.startswith("protected"):
        code = code[len("protected") + 1:]
    if code.startswith("static"):
        code = code[len("static") + 1:]
    if code.startswith("abstract"):
        code = code[len("abstract") + 1:]
    if code.startswith("final"):
        code = code[len("final") + 1:]
    code = code.replace("  ", " ")
    check = code.startswith(" ") or code.startswith("\n")
    return code



def getReturnType(code):
    # 如果遇到泛型方法，跳过
    if code[0] == "<":
        return 0
    ty = code.split(" ")[0]
    if "<" in ty:
        # 要做括号匹配
        start = 0
        count = 0
        for c in range(len(code)):
            if count == 0 and start == 1:
                break
            if code[c] == "<":
                start = 1
                count = count + 1
            if code[c] == ">":
                count = count - 1
        ty = code[:c]
        # 处理public Class<?>[] getTargetImplements() {}
        if "<?>" in ty:
            if code[c] == "[":
                ty = ty + code[c:].split("]")[0] + "]"
    return ty


def getMethodname(code):
    ty = getReturnType(code)
    return code[len(ty) + 1:].split("(")[0]


def checkname(methodname, file):
    return file.split(".java")[1].startswith(methodname)


def getARGS(code):
    if "(" in code:
        # 要做括号匹配
        start = 0
        count = 0
        for c in range(len(code)):
            if count == 0 and start == 1:
                break
            if code[c] == "(":
                start = 1
                count = count + 1
            if code[c] == ")":
                count = count - 1
        ty = code[:c]
        return ty
    else:
        print("wrong")
        return 0


def getType(code):
    code = preprocess(code)
    return getReturnType(code)


def changeDOT(code):
    if "<" in code:
        # 要做括号匹配
        start = 0
        count = 0
        for c in range(len(code)):
            if count > 0 and code[c] == ",":
                code = code[:c] + "。" + code[c + 1:]
            if count == 0 and start == 1:
                break
            if code[c] == "<":
                start = 1
                count = count + 1
            if code[c] == ">":
                count = count - 1
    return code


def changeDOTback(ans):
    newans = []
    for a in ans:
        newans.append(a.replace("。", ","))
    return newans


def getANS(ARGS):
    ARGS = ARGS[1:-1]
    if ARGS.count(" ") == len(ARGS):
        return []
    if "<" not in ARGS:
        lis = ARGS.split(",")
        ans = []
        for l in lis:
            # @Nullable
            if "@" not in l:
                ans.append(getType(l))
            else:
                l = l.split("@")[0] + l.split("@")[1][l.split("@")[1].index(" ") + 1:]
                ans.append(getType(l))
        return ans
    else:
        # 先把<>内的“，”换成“。”，最后再换回来
        ARGS = changeDOT(ARGS)
        lis = ARGS.split(",")
        ans = []
        for l in lis:
            # @Nullable
            if "@" not in l:
                ans.append(getType(l))
            else:
                l = l.split("@")[0] + l.split("@")[1][l.split("@")[1].index(" ") + 1:]
                ans.append(getType(l))
        ans = changeDOTback(ans)
        return ans


# a是素数表
def isPrime(x):
    for i in a:
        if i * i > x: return True
        if x % i == 0: return False
    return True


a = [2]


# 返回第i个素数
def primes(n):
    x = 3
    while len(a) < n:
        if isPrime(x):
            a.append(x)
        x += 1
    return a[-1]


primes(10000)

import math


def computeVal(returntype, ans):
    if returntype == "void":
        if ans == []:
            return 1
        else:
            v = 1
            for a in ans:
                v = v * typeDic[a]
            return v
    else:
        if ans == []:
            # 当tpyeDIC过大的时候，值为0，取mod499
            return math.exp(-(typeDic[returntype]% 744))
        else:
            v = 1
            for a in ans:
                v = v * typeDic[a]
            return v * math.exp(-(typeDic[returntype]% 744))



#引入预设的library type dic

import pickle
def readpkl(pklpath):
    with open(pklpath, 'rb') as f:
        libraryDic = pickle.load(f)
    return libraryDic

import os
pklpath=os.getcwd()+"/JDKparser/libraryDic.pkl"

libraryDic=readpkl(pklpath)

typeDic = libraryDic[0]
libraryclassmethodpairs=libraryDic[1]
# 一个类维护一个methoddic。
# 对于一个method，先计算其值，
dupldic=libraryDic[2]



import glob


# 稍作修改，存储函数名的时候增加存储参数列表。
# 2023.4.27新增修改：将修饰符纳入考虑。如果标识符是private，将不允许类外调用：调用类=定义类时才进行后续搜索。

#不含comment
def getAccess(methodcode):
    code=methodcode
    check = code.startswith(" ") or code.startswith("\n")
    while check:
        code = code[1:]
        while code.startswith("@"):
            code = code[len(code.split("\n")[0]) + 1:]
        check = code.startswith(" ") or code.startswith("\n")
    # 遇到synchronized，删除该词
    code = code.replace("\n", "")
    if "synchronized " in code[:30]:
        code = code[:30].replace("synchronized ", "") + code[30:]
    if "static" in code[:20]:
        return "static"
    if "public" in code[:30]:
        return "public"
    if "private" in code[:30]:
        return "private"
    if "protected" in code[:30]:
        return "protected"
    return "default"



def isStatic(methodcode):
    if getAccess(methodcode)=="static":
        return 1
    return 0

def isPrivate(methodcode):
    if getAccess(methodcode)=="private":
        return 1
    return 0



#返回classmethodpairs，每一元素包括：classname，findfeasible的key字典，其中方法的字典，静态方法的key字典
#不需要额外的static字典。
def getDIC(testpath):
    #os.chdir(testpath)
    classmethodpairs = []
    l = glob.glob(testpath+"/*.txt")
    l.sort()
    for file in l:
        try:
            # print(file)
            classname = file.split('/')[-1].split(".java")[0]
            # methoddic={}
            if classmethodpairs == []:
                methoddic = {}
                classmethoddic = {}
                #Staticmethoddic ={}
                #classmethodpairs.append([classname, methoddic, classmethoddic,Staticmethoddic])
                classmethodpairs.append([classname, methoddic, classmethoddic])
            else:
                if classname == classmethodpairs[-1][0]:
                    methoddic = classmethodpairs[-1][1]
                    classmethoddic = classmethodpairs[-1][2]
                    #Staticmethoddic =classmethodpairs[-1][3]
                else:
                    methoddic = {}
                    classmethoddic = {}
                    #Staticmethoddic ={}
                    classmethodpairs.append([classname, methoddic, classmethoddic])
                    #classmethodpairs.append([classname, methoddic, classmethoddic,Staticmethoddic])
            code = readmethdpath(file)
            code = deletecomment(code)
            #增存access
            access = getAccess(code)
            #print(access)
            isstatic=isStatic(code)
            isprivate = isPrivate(code)
            #私有方法通过加一个-号，只在类内匹配
            code = preprocess(code)
            code = preprocess(code)
            code = preprocess(code)
            returntype = getReturnType(code)
            if returntype == 0:
                continue
            if returntype not in typeDic:
                # a是素数表
                typeDic[returntype] = a[len(typeDic)]
            methodname = getMethodname(code)
            if methodname not in classmethoddic:
                classmethoddic[methodname] = 1
            else:
                classmethoddic[methodname] += 1
            # print([returntype,methodname,file])
            code = code.split(methodname)[1]
            ARGS = getARGS(code)
            ans = getANS(ARGS)
            # pans是参数对应的素数（按顺序排列）
            pans = []
            for an in ans:
                if an not in typeDic:
                    typeDic[an] = a[len(typeDic)]
                pans.append(typeDic[an])
            # print(getARGS(code),ans)
            methodval = computeVal(returntype, ans)
            # 如果私有，-.这个操作还是取消掉，后续检查access
            #if isprivate==1:
            #    methodval = -methodval
            '''
            if isstatic:
                if methodval not in Staticmethoddic:
                    Staticmethoddic[methodval] =  [returntype, ans, [methodname, pans,access]]
                else:
                    if [methodname, pans, access] not in Staticmethoddic[methodval]:
                        Staticmethoddic[methodval].append([methodname, pans, access])
            '''
            if methodval not in methoddic:
                # 增存顺序
                methoddic[methodval] = [returntype, ans, [methodname, pans,access]]
            else:
                if [methodname, pans,access] not in methoddic[methodval]:
                    methoddic[methodval].append([methodname, pans,access])
            if not checkname(methodname, file):
                print(file)
                #break
            if getARGS(code) == 0:
                print([methodname, file])
                break
        except:
            continue
    return classmethodpairs


m=1
