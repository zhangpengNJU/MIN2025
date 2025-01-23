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
            # 当tpyeDIC过大的时候，值为0，取mod744
            return math.exp(-(typeDic[returntype]% 744))
        else:
            v = 1
            for a in ans:
                v = v * typeDic[a]
            return v * math.exp(-(typeDic[returntype]% 744))


typeDic = {}
# 一个类维护一个methoddic。
# 对于一个method，先计算其值，


import os, glob


# 稍作修改，存储函数名的时候增加存储参数列表。
# 2023.5.5修改：增加访问控制，对于库函数，只爬取public和protected。分存两个dic，public和public+protected。如果检索时待替换方法定义所在类为库函数子类，则调用后者。

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


def isPublic(methodcode):
    if getAccess(methodcode)=="public":
        return 1
    return 0


def isProtected(methodcode):
    if getAccess(methodcode)=="protected":
        return 1
    return 0




#testpath=path+"/AllMethods"

#已经修改：
def getDIC(testpath):
    os.chdir(testpath)
    classmethodpairs = []
    l = glob.glob("*.txt")
    l.sort()
    for file in l:
        try:
            # print(file)
            classname = file.split(".java")[0]
            # methoddic={}
            if classmethodpairs == []:
                PUBLICmethoddic = {}
                PUBLICPROTECTEDmethoddic={}
                Staticmethoddic={}
                classmethoddic = {}
                classmethodpairs.append([classname, PUBLICmethoddic, classmethoddic, PUBLICPROTECTEDmethoddic,Staticmethoddic])
            else:
                if classname == classmethodpairs[-1][0]:
                    PUBLICmethoddic = classmethodpairs[-1][1]
                    classmethoddic = classmethodpairs[-1][2]
                    PUBLICPROTECTEDmethoddic = classmethodpairs[-1][3]
                    Staticmethoddic=classmethodpairs[-1][4]
                else:
                    PUBLICmethoddic ={}
                    PUBLICPROTECTEDmethoddic = {}
                    Staticmethoddic={}
                    classmethoddic = {}
                    classmethodpairs.append([classname, PUBLICmethoddic, classmethoddic,PUBLICPROTECTEDmethoddic,Staticmethoddic])
            code = readmethdpath(testpath + "/" + file)
            code = deletecomment(code)
            access = getAccess(code)

            print(access)
            isstatic= isStatic(code)

            isprivate = isPrivate(code)
            ispublic = isPublic(code)
            isprotected = isProtected(code)
            #如果既不是public，也不是protect,static，跳过
            if ispublic+isprotected+isstatic<1:
                continue

            code = preprocess(code)
            code = preprocess(code)
            code = preprocess(code)
            returntype = getReturnType(code)
            if returntype == 0:
                #泛型，跳过
                continue
            if returntype not in typeDic:
                # a是素数表
                #这里故意不定义a，因为理论上不会执行到这里。
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

            if isstatic:
                if methodval not in Staticmethoddic:
                    Staticmethoddic[methodval] =  [returntype, ans, [methodname, pans,access]]
                else:
                    if [methodname, pans, access] not in Staticmethoddic[methodval]:
                        Staticmethoddic[methodval].append([methodname, pans, access])


            if ispublic:
                if methodval not in PUBLICPROTECTEDmethoddic:
                    # 增存顺序
                    PUBLICPROTECTEDmethoddic[methodval] = [returntype, ans, [methodname, pans,access]]
                else:
                    if [methodname, pans,access] not in PUBLICPROTECTEDmethoddic[methodval]:
                        PUBLICPROTECTEDmethoddic[methodval].append([methodname, pans,access])
                if methodval not in PUBLICmethoddic:
                    # 增存顺序
                    PUBLICmethoddic[methodval] = [returntype, ans, [methodname, pans,access]]
                else:
                    if [methodname, pans,access] not in PUBLICmethoddic[methodval]:
                        PUBLICmethoddic[methodval].append([methodname, pans,access])
            if isprotected:
                if methodval not in PUBLICPROTECTEDmethoddic:
                    # 增存顺序
                    PUBLICPROTECTEDmethoddic[methodval] = [returntype, ans, [methodname, pans,access]]
                else:
                    if [methodname, pans,access] not in PUBLICPROTECTEDmethoddic[methodval]:
                        PUBLICPROTECTEDmethoddic[methodval].append([methodname, pans,access])
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
'''
testpath="D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\AllMethods\\"
classmethodpairs=getDIC(testpath)
#以上把一个项目中所有方法，按所在类进行了归放，存放在classmethoddic，并且可以替换的方法具有相同的值存放在methoddic。

c=classmethodpairs[1]
for ci in c[1]:
    for g in c[1][ci][2:]:
        print(g[0][0])


# 再获取一个根据方法名找到对应类的函数
def getMethodClassDIC(classmethodpairs):
    MethodClassDic = {}
    for c in classmethodpairs:
        classmethoddic = c[2]
        for d in classmethoddic:
            if d not in MethodClassDic:
                MethodClassDic[d] = [c[0]]
            else:
                MethodClassDic[d].append(c[0])
    return MethodClassDic



#获取方法的返回类型：
x=1
'''
dupl=[[2, 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\awt\\List.java', 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\util\\List.java'], [2, 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\beans\\Statement.java', 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\sql\\Statement.java'], [2, 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\io\\Bits.java', 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\nio\\Bits.java'], [2, 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\io\\FileSystem.java', 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\nio\\file\\FileSystem.java'], [2, 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\lang\\annotation\\Annotation.java', 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\text\\Annotation.java'], [25, 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\lang\\annotation\\package-info.java', 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\lang\\invoke\\package-info.java', 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\lang\\package-info.java', 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\lang\\reflect\\package-info.java', 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\math\\package-info.java', 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\net\\package-info.java', 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\nio\\channels\\package-info.java', 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\nio\\file\\attribute\\package-info.java', 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\nio\\file\\package-info.java', 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\nio\\file\\spi\\package-info.java', 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\security\\acl\\package-info.java', 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\security\\cert\\package-info.java', 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\security\\interfaces\\package-info.java', 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\security\\package-info.java', 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\security\\spec\\package-info.java', 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\time\\chrono\\package-info.java', 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\time\\format\\package-info.java', 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\time\\package-info.java', 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\time\\temporal\\package-info.java', 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\time\\zone\\package-info.java', 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\util\\concurrent\\atomic\\package-info.java', 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\util\\concurrent\\locks\\package-info.java', 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\util\\concurrent\\package-info.java', 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\util\\function\\package-info.java', 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\util\\stream\\package-info.java'], [2, 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\lang\\reflect\\Array.java', 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\sql\\Array.java'], [2, 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\lang\\reflect\\Proxy.java', 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\net\\Proxy.java'], [2, 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\net\\ConnectException.java', 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\rmi\\ConnectException.java'], [2, 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\net\\UnknownHostException.java', 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\rmi\\UnknownHostException.java'], [2, 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\nio\\file\\attribute\\AclEntry.java', 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\security\\acl\\AclEntry.java'], [2, 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\security\\acl\\Permission.java', 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\security\\Permission.java'], [2, 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\security\\cert\\Certificate.java', 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\security\\Certificate.java'], [2, 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\security\\Timestamp.java', 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\sql\\Timestamp.java'], [2, 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\sql\\Date.java', 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\util\\Date.java'], [3, 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\time\\chrono\\Ser.java', 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\time\\Ser.java', 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\time\\zone\\Ser.java'], [2, 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\util\\Base64.java', 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\util\\prefs\\Base64.java'], [2, 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\util\\Formatter.java', 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\util\\logging\\Formatter.java'], [2, 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\util\\stream\\Tripwire.java', 'D:\\14771\\Desktop\\学习\\5\\MIN\\MIN\\MIN\\JDKparser\\jdk-7fcf35286d52\\src\\share\\classes\\java\\util\\Tripwire.java']]

duplDic={'List': 1, 'Statement': 1, 'Bits': 1, 'FileSystem': 1, 'Annotation': 1, 'package-info': 1, 'Array': 1, 'Proxy': 1, 'ConnectException': 1, 'UnknownHostException': 1, 'AclEntry': 1, 'Permission': 1, 'Certificate': 1, 'Timestamp': 1, 'Date': 1, 'Ser': 1, 'Base64': 1, 'Formatter': 1, 'Tripwire': 1}

#对于lib中的重名类，采用如下方案：不仅仅存储类名，还存前一个文件夹名，比如awt.List

def makeDifferentDicForPKG(path1,classname):
    os.chdir(path1)
    classmethodpairs = []
    l = glob.glob(classname+".java*.txt")
    l.sort()
    for file in l:
        try:
            # print(file)
            classname = file.split(".java")[0]
            # methoddic={}
            if classmethodpairs == []:
                PUBLICmethoddic = {}
                PUBLICPROTECTEDmethoddic={}
                Staticmethoddic={}
                classmethoddic = {}
                classmethodpairs.append([path1.split('\\')[-2]+'.'+classname, PUBLICmethoddic, classmethoddic, PUBLICPROTECTEDmethoddic,Staticmethoddic])
            else:
                if path1.split('\\')[-2]+'.'+classname == classmethodpairs[-1][0]:
                    PUBLICmethoddic = classmethodpairs[-1][1]
                    classmethoddic = classmethodpairs[-1][2]
                    PUBLICPROTECTEDmethoddic = classmethodpairs[-1][3]
                    Staticmethoddic=classmethodpairs[-1][4]
                else:
                    PUBLICmethoddic ={}
                    PUBLICPROTECTEDmethoddic = {}
                    Staticmethoddic={}
                    classmethoddic = {}
                    classmethodpairs.append([path1.split('\\')[-2]+'.'+classname, PUBLICmethoddic, classmethoddic,PUBLICPROTECTEDmethoddic,Staticmethoddic])
            code = readmethdpath(path1 + "/" + file)
            code = deletecomment(code)
            access = getAccess(code)

            print(access)
            isstatic= isStatic(code)

            isprivate = isPrivate(code)
            ispublic = isPublic(code)
            isprotected = isProtected(code)
            #如果既不是public，也不是protect,static，跳过
            if ispublic+isprotected+isstatic<1:
                continue

            code = preprocess(code)
            code = preprocess(code)
            code = preprocess(code)
            returntype = getReturnType(code)
            if returntype == 0:
                #泛型，跳过
                continue
            if returntype not in typeDic:
                # a是素数表
                #这里故意不定义a，因为理论上不会执行到这里。
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

            if isstatic:
                if methodval not in Staticmethoddic:
                    Staticmethoddic[methodval] =  [returntype, ans, [methodname, pans,access]]
                else:
                    if [methodname, pans, access] not in Staticmethoddic[methodval]:
                        Staticmethoddic[methodval].append([methodname, pans, access])


            if ispublic:
                if methodval not in PUBLICPROTECTEDmethoddic:
                    # 增存顺序
                    PUBLICPROTECTEDmethoddic[methodval] = [returntype, ans, [methodname, pans,access]]
                else:
                    if [methodname, pans,access] not in PUBLICPROTECTEDmethoddic[methodval]:
                        PUBLICPROTECTEDmethoddic[methodval].append([methodname, pans,access])
                if methodval not in PUBLICmethoddic:
                    # 增存顺序
                    PUBLICmethoddic[methodval] = [returntype, ans, [methodname, pans,access]]
                else:
                    if [methodname, pans,access] not in PUBLICmethoddic[methodval]:
                        PUBLICmethoddic[methodval].append([methodname, pans,access])
            if isprotected:
                if methodval not in PUBLICPROTECTEDmethoddic:
                    # 增存顺序
                    PUBLICPROTECTEDmethoddic[methodval] = [returntype, ans, [methodname, pans,access]]
                else:
                    if [methodname, pans,access] not in PUBLICPROTECTEDmethoddic[methodval]:
                        PUBLICPROTECTEDmethoddic[methodval].append([methodname, pans,access])
            if not checkname(methodname, file):
                print(file)
                #break
            if getARGS(code) == 0:
                print([methodname, file])
                break
        except:
            continue
    return classmethodpairs

