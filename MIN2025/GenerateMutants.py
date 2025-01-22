import GetAllMethodDIC
import subprocess


def runGetMethodJar(path, jarpath="./GetAllMethods.jar"):
    p = subprocess.Popen('cp ' + jarpath + " " + path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.communicate()
    p = subprocess.Popen("java -jar GetAllMethods.jar", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         cwd=path)
    p.communicate()


def cpRmvCmtJar(path, jarpath="./RemoveComment.jar"):
    p = subprocess.Popen("cp " + jarpath + " " + path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.communicate()


def getDIC(path):
    # 每次需要先清0dic
    # 不需要了，要保证lib的type存在
    GetAllMethodDIC.typeDic = GetAllMethodDIC.libraryDic[0]
    return GetAllMethodDIC.getDIC(path)


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


# 给定方法名，搜索定义它的类，进一步的，在该类中寻找可以替代的方法（相同返回类型，相同输入类型）。
# # PS：值得注意的是，方法理论上不考虑传入参数的顺序，即不同的顺序也会有相同的key，但是运行时可能会导致编译不通过（即，替代后理论上需要考虑更换参数顺序），FIX IT
# # 已经fix：现在要返回带有参数顺序的结果。

# 2023.5.6更新，对于一个方法，首先获得其access

LibTreePath="/home/fl/Downloads/MIN/libraryTreeDic.pkl"
libraryDic=GetAllMethodDIC.readpkl(LibTreePath)


#返回父类方法名
#这个是搜的库函数Dic，需要对库函数进行拓展，把Dic拓展到当前包

import InheritanceAnalysis


def findfathers(classname,libraryDic):
    ans=[]
    if classname not in libraryDic:
        return []
    a=libraryDic[classname]
    while a:
        if a.father:
            ans.append(a.father.name)
            a=a.father
        else:
            break
    return ans

libraryclassmethodpairs=GetAllMethodDIC.libraryclassmethodpairs

LibMethodClassDIC=getMethodClassDIC(libraryclassmethodpairs)


LibPath="./libraryPathDic.pkl"
libraryPathDic=GetAllMethodDIC.readpkl(LibPath)




#寻找access不为给定值的feasible方法。
#注意classmethodpairs和libclassmethodpairs的格式是不一样的。
#lib中有五个元素：类名，public方法的feasible值dic，方法名dic，public+protected的feasibledic，static的feasibledic

def findKeyForMethod(feasibleDIC,methodname):
    Keys=[]
    wantedorder=[]
    for d in feasibleDIC:
        find = 0
        if len(feasibleDIC[d])>2:
            for f in feasibleDIC[d][2:]:
                if f[0] == methodname:
                    find = 1
                    Keys.append(d)
                    #wantedorder = f[1]
                    break
    return Keys



#在字典里搜索具有特定key的方法，并且ACCESS不为给定值
def findFeasibleMethodsByKeyNONACCESS(Keys,feasibleDIC,ACCESS=""):
    ans=[]
    for key in Keys:
        if key not in feasibleDIC:
            continue
        tocheck=feasibleDIC[key]
        wantedorder = tocheck[2][1]
        wantedC=[]
        for ci in tocheck[2:]:
            if ci[-1] != ACCESS:
                wantedC.append(ci)
        if wantedC != []:
            ans.append([wantedorder, wantedC])
            break
    return ans



#在字典里搜索具有特定key的方法，并且ACCESS为给定值
def findFeasibleMethodsByKeyACCESS(Keys,feasibleDIC,ACCESS=""):
    ans=[]
    for key in Keys:
        if key not in feasibleDIC:
            continue
        tocheck=feasibleDIC[key]
        wantedorder=tocheck[2][1]
        wantedC=[]
        for ci in tocheck[2:]:
            if ci[-1] == ACCESS:
                wantedC.append(ci)
        if wantedC != []:
            ans.append([wantedorder,wantedC])
            break
    return ans



#非lib
#对于一堆待定类，
def findKeyInClasses(classnames,classmethodpairs,methodname):
    Keys=[]
    for classmethodpair in classmethodpairs:
        if classmethodpair[0] in classnames:
            feasibleDIC=classmethodpair[1]
            Keys+=findKeyForMethod(feasibleDIC,methodname)
    return Keys


def findKeyInLibClasses(classnames,libraryclassmethodpairs,methodname):
    Keys=[]
    for classmethodpair in libraryclassmethodpairs:
        if classmethodpair[0] in classnames:
            feasibleDIC=classmethodpair[3]
            Keys+=findKeyForMethod(feasibleDIC,methodname)
            feasibleDIC=classmethodpair[4]
            Keys+=findKeyForMethod(feasibleDIC,methodname)
    return Keys




def findFeasibleMethodsInClassMethodPiarsACCESS(Keys,classmethodpairs,classname,ACCESS=""):
    ans=[]
    for classmethodpair in classmethodpairs:
        if classmethodpair[0] == classname:
            feasibleDIC = classmethodpair[1]
            ans+=findFeasibleMethodsByKeyACCESS(Keys, feasibleDIC, ACCESS)
    return ans


def findFeasibleMethodsInClassMethodPiarsNONACCESS(Keys,classmethodpairs,classname,ACCESS=""):
    ans=[]
    for classmethodpair in classmethodpairs:
        if classmethodpair[0] == classname:
            feasibleDIC = classmethodpair[1]
            ans+=findFeasibleMethodsByKeyNONACCESS(Keys, feasibleDIC, ACCESS)
    return ans




def findFeasibleMethodsInLibClassMethodPiarsACCESS(Keys,libraryclassmethodpairs,classname,ACCESS=""):
    ans=[]
    for classmethodpair in libraryclassmethodpairs:
        if classmethodpair[0] == classname:
            feasibleDIC = classmethodpair[3]
            ans+=findFeasibleMethodsByKeyACCESS(Keys, feasibleDIC, ACCESS)
            feasibleDIC = classmethodpair[4]
            ans+=findFeasibleMethodsByKeyACCESS(Keys, feasibleDIC, ACCESS)
    return ans


def findFeasibleMethodsInLibClassMethodPiarsNONACCESS(Keys,libraryclassmethodpairs,classname,ACCESS=""):
    ans=[]
    for classmethodpair in libraryclassmethodpairs:
        if classmethodpair[0] == classname:
            feasibleDIC = classmethodpair[3]
            ans+=findFeasibleMethodsByKeyNONACCESS(Keys, feasibleDIC, ACCESS)
            feasibleDIC = classmethodpair[4]
            ans+=findFeasibleMethodsByKeyNONACCESS(Keys, feasibleDIC, ACCESS)
    return ans






def checkMethodInClass(methodname,classname,AllDic,LibMethodClassDIC,MethodClassDIC):
    if '.' in classname:
        return 1
    allcan=findfathers(classname, AllDic)+[classname]
    A=set()
    B=set()
    if methodname in LibMethodClassDIC:
        A = set(LibMethodClassDIC[methodname])
    if methodname in MethodClassDIC:
        B=set(MethodClassDIC[methodname])
    if (A|B) & set(allcan):
        return 1
    return 0




dupld={'List': ['awt.List', 'util.List'], 'Statement': ['beans.Statement', 'sql.Statement'],
     'Bits': ['io.Bits', 'nio.Bits'], 'FileSystem': ['io.FileSystem', 'file.FileSystem'],
     'Annotation': ['annotation.Annotation', 'text.Annotation'],
     'package-info': ['annotation.package-info', 'invoke.package-info'], 'Array': ['reflect.Array', 'sql.Array'],
     'Proxy': ['reflect.Proxy', 'net.Proxy'], 'ConnectException': ['net.ConnectException', 'rmi.ConnectException'],
     'UnknownHostException': ['net.UnknownHostException', 'rmi.UnknownHostException'],
     'AclEntry': ['attribute.AclEntry', 'acl.AclEntry'], 'Permission': ['acl.Permission', 'security.Permission'],
     'Certificate': ['cert.Certificate', 'security.Certificate'], 'Timestamp': ['security.Timestamp', 'sql.Timestamp'],
     'Date': ['sql.Date', 'util.Date'], 'Ser': ['chrono.Ser', 'time.Ser'], 'Base64': ['util.Base64', 'prefs.Base64'],
     'Formatter': ['util.Formatter', 'logging.Formatter'], 'Tripwire': ['stream.Tripwire', 'util.Tripwire']}

def changeDuplType(duplty,code):
    ntp1=dupld[duplty][0]
    ntp2=dupld[duplty][1]
    if (ntp1 in code) and (ntp2 not in code):
        return ntp1
    if (ntp1 not in code) and (ntp2 in code):
        return ntp2
    if (ntp1 in code) and (ntp2 in code):
        if code.index(ntp1)<code.index(ntp1):
            return ntp1
    return ntp2

def changeDuplTypes(tps,code):
    newtps=[]
    for tp in tps:
        if tp not in dupld:
            newtps.append(tp)
        else:
            newtps.append(changeDuplType(tp,code))
    return set(newtps)



def findAnyInCurrentClass(currentclass, classmethodpairs, methodname):
    ans=[]
    Keys = findKeyInClasses([currentclass], classmethodpairs, methodname)
    ans += findFeasibleMethodsInClassMethodPiarsNONACCESS(Keys, classmethodpairs, currentclass, "")
    return ans








def findStaticInCurrentClass(currentclass,classmethodpairs,methodname):
    ans=[]
    Keys = findKeyInClasses([currentclass], classmethodpairs, methodname)
    ans += findFeasibleMethodsInClassMethodPiarsACCESS(Keys, classmethodpairs, currentclass, "static")
    return ans


def findfeasibleByType(methodname, MethodClassDIC, classmethodpairs, param_num, currentclass, AllDic, tp):
    # 不走这条路的有32个，其中只有4个通过编译了，留此注记。
    # 要先把tp扩充到它的父亲们。
    # findTargetClass是个伪命题。如果A.methodB,定义在A的父类C中，难道只搜索C吗？实际上需要搜索A和C，但是由于后续有搜索A的父亲的环节，所以这里只要A就可以了。
    # 进行修改：对于tp中的每一个类元素进行检查，检查其中是否定义了methodB，有返回1，如果没有，检查它的父亲，如果到根节点都没有，返回0
    tps = []
    for t in tp:
        if checkMethodInClass(methodname, t, AllDic, LibMethodClassDIC, MethodClassDIC):
            tps.append(t)
    # classnames=findTargetClass(methodname,MethodClassDIC,set(tps))
    classnames = tps
    ans = []
    newclassnames = []
    currentclassfathers = findfathers(currentclass, AllDic)
    # 再把所有的父类加入到classnames中
    for classname in classnames:
        fatherlist = findfathers(classname, libraryDic) + findfathers(classname, AllDic)
        for f in fatherlist:
            if f not in classnames:
                newclassnames.append(f)
    classnames = classnames + newclassnames
    classnames = list(set(classnames))
    Keys = findKeyInClasses(classnames, classmethodpairs, methodname) + findKeyInLibClasses(classnames,
                                                                                            libraryclassmethodpairs,
                                                                                            methodname)
    for classname in classnames:
        # 访问控制：当前类就是定义所在类，则全部可访问
        if classname == currentclass:
            ans+= findFeasibleMethodsInClassMethodPiarsNONACCESS(Keys, classmethodpairs, classname, "")
            ans+= findFeasibleMethodsInLibClassMethodPiarsNONACCESS(Keys, libraryclassmethodpairs, classname, "")
        # 访问控制：当前类是定义所在类的子类，当前包除了private都可以。lib包可以public，protected，static
        elif classname in currentclassfathers:
            # print("classname: ", classname)
            ans+= findFeasibleMethodsInClassMethodPiarsNONACCESS(Keys, classmethodpairs, classname, "private")
            ans += findFeasibleMethodsInLibClassMethodPiarsACCESS(Keys, libraryclassmethodpairs, classname, "public")
            ans += findFeasibleMethodsInLibClassMethodPiarsACCESS(Keys, libraryclassmethodpairs, classname, "protected")
            ans += findFeasibleMethodsInLibClassMethodPiarsACCESS(Keys, libraryclassmethodpairs, classname, "static")
        # 访问控制：只能访问public和static的情况：
        else:
            ans+= findFeasibleMethodsInClassMethodPiarsACCESS(Keys, classmethodpairs, classname, "public")
            ans+= findFeasibleMethodsInLibClassMethodPiarsACCESS(Keys, libraryclassmethodpairs, classname, "public")
            ans+= findFeasibleMethodsInClassMethodPiarsACCESS(Keys, classmethodpairs, classname, "static")
            ans+= findFeasibleMethodsInLibClassMethodPiarsACCESS(Keys, libraryclassmethodpairs, classname, "static")
    # 再检查一下参数个数
    newans = []
    for a in ans:
        if len(a[0]) == param_num:
            newans.append(a)
    return newans







# l是一个含有（的玩意，接下来就能找（前，.后的单词，
def getMethodName(lisl):
    print("getMethodName-l: ", lisl)  # l改为lisl: createCopy(RegularTimePeriod,
    methodname = lisl.split("(")[0]
    # 括号前的长度
    position = len(lisl.split("(")[0])
    if "." in methodname:
        methodname = methodname.split(".")[-1]
    return methodname, position


# 文件名包含了修改的class，mutant编号
def writeMutant(mutantCode, index, classname, outputpath="./Mutants/"):
    p = subprocess.Popen('mkdir Mutants', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.communicate()
    f = open(outputpath + str(index) + "-" + classname, 'w')
    f.write(mutantCode)
    f.close()


# lis是code按“ ”切开，lis【l】是方法名
def getMethodARG(lis, l):
    # 向后做括号匹配，先把函数这段代码找到。
    start = lis[l].count("(") - lis[l].count(")")
    print("getMethodARG-l: ", l)
    j = l  # l为split by 空格 后 整个.java文件的索引，例如212
    if start != 0:
        try:
            while start != 0:
                j = j + 1
                start = start + lis[j].count("(") - lis[j].count(")")
        except:
            return 0
    c = " ".join(lis[l:j + 1])
    startindex = c.index("(")
    endindex = c[::-1].index(")")
    ARGS = c[startindex + 1:-(endindex + 1)]
    if ARGS == "":
        return c, j, startindex, endindex, []  # startindex为方法名长度
    ARGLIST = ARGS.split(",")
    # 拼回去怎么拼：lis[:l]+c的变化+lis[j+1:]
    # C的变化：函数名，参数顺序
    # c【startindex】=“（”
    return c, j, startindex, endindex, ARGLIST


# eg：ARGLIST=[a1,a2,b],oldorder=223,neworder=322.其中a1a2具有相同的类型
# 也就是说，为了避免组合爆炸，我们将所有的顺序颠倒过来。
def changeOrder(ARGLIST, oldOrder, newOrder):
    dic = {}
    ans = []
    for o in range(len(oldOrder)):
        if oldOrder.count(oldOrder[o]) == 1:
            dic[oldOrder[o]] = [ARGLIST[o]]
        else:
            if oldOrder[o] not in dic:
                dic[oldOrder[o]] = [ARGLIST[o]]
            else:
                dic[oldOrder[o]].append(ARGLIST[o])
    # 不能生成太多的变异体，只交换一次
    for n in newOrder:
        if len(dic[n]) == 1:
            ans.append(dic[n][0])
        else:
            ans.append(dic[n][-1])
            dic[n] = dic[n][:-1]
    return ans


def changedCode(c, newmethodname, ARGLIST, oldOrder, newOrder, methodname, position):
    changedARGLIST = changeOrder(ARGLIST, oldOrder, newOrder)
    c = c.replace(",".join(ARGLIST), ",".join(changedARGLIST))
    return c[:position - len(methodname)] + newmethodname + c[position:]


def multiplyList(myList):
    result = 1
    for x in myList:
        result = result * x
    return result



langDic={'AbstractMethodError': 1, 'AbstractStringBuilder': 1, 'Appendable': 1, 'ApplicationShutdownHooks': 1, 'ArithmeticException': 1, 'ArrayIndexOutOfBoundsException': 1, 'ArrayStoreException': 1, 'AssertionError': 1, 'AssertionStatusDirectives': 1, 'AutoCloseable': 1, 'Boolean': 1, 'BootstrapMethodError': 1, 'Byte': 1, 'Character': 1, 'CharacterData': 1, 'CharacterName': 1, 'CharSequence': 1, 'Class': 1, 'ClassCastException': 1, 'ClassCircularityError': 1, 'ClassFormatError': 1, 'ClassLoader': 1, 'ClassNotFoundException': 1, 'ClassValue': 1, 'Cloneable': 1, 'CloneNotSupportedException': 1, 'Comparable': 1, 'Compiler': 1, 'ConditionalSpecialCasing': 1, 'Deprecated': 1, 'Double': 1, 'Enum': 1, 'EnumConstantNotPresentException': 1, 'Error': 1, 'Exception': 1, 'ExceptionInInitializerError': 1, 'Float': 1, 'FunctionalInterface': 1, 'IllegalAccessError': 1, 'IllegalAccessException': 1, 'IllegalArgumentException': 1, 'IllegalMonitorStateException': 1, 'IllegalStateException': 1, 'IllegalThreadStateException': 1, 'IncompatibleClassChangeError': 1, 'IndexOutOfBoundsException': 1, 'InheritableThreadLocal': 1, 'InstantiationError': 1, 'InstantiationException': 1, 'Integer': 1, 'InternalError': 1, 'InterruptedException': 1, 'Iterable': 1, 'LinkageError': 1, 'Long': 1, 'Math': 1, 'NegativeArraySizeException': 1, 'NoClassDefFoundError': 1, 'NoSuchFieldError': 1, 'NoSuchFieldException': 1, 'NoSuchMethodError': 1, 'NoSuchMethodException': 1, 'NullPointerException': 1, 'Number': 1, 'NumberFormatException': 1, 'Object': 1, 'OutOfMemoryError': 1, 'Override': 1, 'package-info': 1, 'Package': 1, 'Process': 1, 'ProcessBuilder': 1, 'Readable': 1, 'ReflectiveOperationException': 1, 'Runnable': 1, 'Runtime': 1, 'RuntimeException': 1, 'RuntimePermission': 1, 'SafeVarargs': 1, 'SecurityException': 1, 'SecurityManager': 1, 'Short': 1, 'Shutdown': 1, 'StackOverflowError': 1, 'StackTraceElement': 1, 'StrictMath': 1, 'String': 1, 'StringBuffer': 1, 'StringBuilder': 1, 'StringCoding': 1, 'StringIndexOutOfBoundsException': 1, 'SuppressWarnings': 1, 'System': 1, 'Thread': 1, 'ThreadDeath': 1, 'ThreadGroup': 1, 'ThreadLocal': 1, 'Throwable': 1, 'TypeNotPresentException': 1, 'UnknownError': 1, 'UnsatisfiedLinkError': 1, 'UnsupportedClassVersionError': 1, 'UnsupportedOperationException': 1, 'VerifyError': 1, 'VirtualMachineError': 1, 'Void': 1}


def checkLang(l):
    if l in langDic:
        return True
    return False





import importparser


#cp='D:/14771/Desktop/学习/5/MIN/MIN/MIN/JDKparser/jdk-7fcf35286d52/src/share/classes/java/nio/Bits.java'
import typeInference

def generateMutantsForOneClass(cp, MethodClassDIC, classmethodpairs, AllDic, maxMount=5):
    f = open(cp)
    # 用个中文句号，好换回来
    if "/" in cp:
        currentclass = cp.split("/")[-1][:-5]
    else:
        currentclass = cp.split("\\")[-1][:-5]
    classname = cp.replace("/", "-")
    lines = f.read()
    currentclassTypeDic=typeInference.typeInferenceForCode(lines)
    #importlibs=importparser.getLibImportsFromCode(lines)
    #importpkgs=importparser.getPKGImportsFromCode(lines)
    # print(lines)
    f.close()
    lis = lines.split(" ")
    #print("lis: ", lis)  # lis为整个java文件 split by 空格
    index = 0
    for l in range(len(lis)):
        maxMutant = 0
        if ("(" in lis[l]) and lis[l][0] != "(":  # 修改
            #print("lis[l-1]: ", l-1, lis[l-1], "lis[l-2]: ", l-2, lis[l-2])
            if (lis[l-2] == "private") or (lis[l-2] == "protected") or (lis[l-2] == "public"):
                continue
            if (lis[l-1] == "private") or (lis[l-1] == "protected") or (lis[l-1] == "public"):
                continue
            if lis[l-2] == "static":
                continue
            if lis[l-2] == "final":
                continue
            #POSTION是括号前的长度
            methodname, position = getMethodName(lis[l])
            # ans的格式【【正确参数顺序，【可替换函数1，函数1参数顺序】，【可替换函数2，函数2参数顺序】】，【正确参数顺序，【可替换函数1，函数1参数顺序】，【可替换函数2，函数2参数顺序】】】
            # 还要再写一个获取参数的方法
            g = getMethodARG(lis, l)
            #print("g: ", g)
            if g == 0:
                continue
            c, j, startindex, endindex, ARGLIST = g
            param_num=len(ARGLIST)
            #print("methodname: ", methodname)
            #如果是java.lang里的，importlibs修改为指定的类
            tocheck=lis[l].split(".")[0]
            if checkLang(tocheck):
                tp=set(langDic)
                ans=findfeasibleByType(methodname, MethodClassDIC, classmethodpairs, param_num, currentclass,
                                   AllDic, tp)
                #ans = findfeasibleByImport(methodname, MethodClassDIC, classmethodpairs, ["java.lang." + tocheck],param_num, currentclass, AllDic, importpkgs)
            else:
                # 如果是method（）：换本类里的任意方法
                if len(methodname) == position:
                    #ans = findStaticInCurrentClass(currentclass, classmethodpairs, methodname)
                    ans = findAnyInCurrentClass(currentclass, classmethodpairs, methodname)
                # 如果是A.method():先确定A的类型，再在这些类里找。
                else:
                    call = lis[l][:position - len(methodname) - 1]
                    if "." in call:
                        call = call.split(".")[-1]
                    # 解决case：optionGroups.put(option.getKey()，识别为put(option
                    if '(' in call:
                        call = call.split("(")[-1]
                    if call in currentclassTypeDic:
                        tp = currentclassTypeDic[call]
                    else:
                        tp = set()
                    tp=changeDuplTypes(tp, lines)
                    if tp != set():
                        ans = findfeasibleByType(methodname, MethodClassDIC, classmethodpairs, param_num, currentclass,
                                                 AllDic, tp)
                    else:
                        #A.method,但是A的类型不确定.先不处理这一类情形。
                        #0120:增补此情况,A为同目录下类，实际上直接去找其静态方法即可
                        if call in AllDic:
                            tp.add(call)
                        ans = findfeasibleByType(methodname, MethodClassDIC, classmethodpairs, param_num, currentclass,
                                                 AllDic, tp)
                        msa=1
            if ans == 0:
                continue
            useddic={}
            for an in ans:
                if maxMutant >= maxMount:
                    break
                if len(an[0]) != len(ARGLIST):
                    continue
                for a in an[1]:
                    if a[0] != methodname:
                        # 正确参数[1,2,3],函数1参数[3,2,1]
                        # 不需要调整的情况：顺序一致，且不重复
                        if a[1] == an[0]:
                            # if list(set(a[1]))==a[1]:
                            mutantCode = ''
                            if a[0] in useddic:
                                continue
                            useddic[a[0]]=1
                            for t in range(len(lis)):
                                if t != l:
                                    mutantCode = mutantCode + lis[t] + " "
                                else:
                                    mutantCode = mutantCode + lis[l][:position - len(methodname)] + a[0] + lis[l][
                                                                                                           position:] + " "
                            index = index + 1
                            writeMutant(mutantCode, index, classname)
                            maxMutant += 1
                            if maxMutant >= maxMount:
                                break
                            # 相等，但有重复
                            if len(list(set(a[1]))) != len(a[1]):
                                print([cp, methodname, an])
                                c = changedCode(c, a[0], ARGLIST, an[0], a[1], methodname, position)
                                # 拼回去怎么拼：lis[:l]+c的变化+lis[j+1:]
                                mutantCode = ''
                                for t in range(l):
                                    mutantCode = mutantCode + lis[t] + " "
                                mutantCode = mutantCode + c
                                for t in range(j + 1, len(lis)):
                                    mutantCode = mutantCode + lis[t] + " "
                                index = index + 1
                                writeMutant(mutantCode, index, classname)
                                maxMutant += 1
                            if maxMutant >= maxMount:
                                break
                        elif multiplyList(a[1]) == multiplyList(an[0]):
                            print([cp, methodname, an])
                            if a[0] in useddic:
                                continue
                            useddic[a[0]]=1
                            c = changedCode(c, a[0], ARGLIST, an[0], a[1], methodname, position)
                            # 拼回去怎么拼：lis[:l]+c的变化+lis[j+1:]
                            mutantCode = ''
                            for t in range(l):
                                mutantCode = mutantCode + lis[t] + " "
                            mutantCode = mutantCode + c
                            for t in range(j + 1, len(lis)):
                                mutantCode = mutantCode + lis[t] + " "
                            index = index + 1
                            writeMutant(mutantCode, index, classname)
                            maxMutant += 1
                            if maxMutant >= maxMount:
                                break
                    else:
                        # 相等，但有重复
                        if len(list(set(a[1]))) != len(a[1]):
                            #print([cp, methodname, an])
                            c = changedCode(c, a[0], ARGLIST, an[0], a[1], methodname, position)
                            # 拼回去怎么拼：lis[:l]+c的变化+lis[j+1:]
                            mutantCode = ''
                            for t in range(l):
                                mutantCode = mutantCode + lis[t] + " "
                            mutantCode = mutantCode + c
                            for t in range(j + 1, len(lis)):
                                mutantCode = mutantCode + lis[t] + " "
                            index = index + 1
                            writeMutant(mutantCode, index, classname)
                            maxMutant += 1
                        #方法名相等，参数无重复，看看是否有多态
                        #changecode的方法如下，所以要求oldORder！=neworder
                        #def changedCode(c, newmethodname, ARGLIST, oldOrder, newOrder, methodname, position):
                        elif an[0]!=a[1]:
                            c = changedCode(c, a[0], ARGLIST, an[0], a[1], methodname, position)
                            # 拼回去怎么拼：lis[:l]+c的变化+lis[j+1:]
                            mutantCode = ''
                            for t in range(l):
                                mutantCode = mutantCode + lis[t] + " "
                            mutantCode = mutantCode + c
                            for t in range(j + 1, len(lis)):
                                mutantCode = mutantCode + lis[t] + " "
                            index = index + 1
                            writeMutant(mutantCode, index, classname)
                            maxMutant += 1
                        if maxMutant >= maxMount:
                            break






def generteMutantsForAllClass(filelist, MethodClassDIC, classmethodpairs, path, maxMount=5):
    InheritanceAnalysis.MakeTreeFromPath(filelist, libraryDic)
    AllDic=libraryDic
    for cp in filelist:
        print("cp: ", cp)
        p = subprocess.Popen("java -jar RemoveComment.jar " + cp, shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, cwd=path)   # path与cp相差文件名
        p.communicate()
        generateMutantsForOneClass(cp, MethodClassDIC, classmethodpairs, AllDic,maxMount)







#m=1
#methodname, MethodClassDIC, classmethodpairs, param_num, currentclass, AllDic, tp= "toUpper",LibMethodClassDIC,libraryclassmethodpairs,1,"",libraryDic,set(["ASCII"])

#v=findfeasibleByType(methodname, MethodClassDIC, classmethodpairs, param_num, currentclass, AllDic, tp)


