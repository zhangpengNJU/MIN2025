import javalang
import os
import glob


def getFatherFromCode(code):
    tree = javalang.parse.parse(code)
    try:
        if tree.types[0].extends:
            w=tree.types[0].extends
            if type(w)==type([]):
                w=tree.types[0].extends[0]
        #print(tree.types[0].extends)
            return w.name
    except:
        return ""
    return ""

class TreeNode:
    def __init__(self, name, father=None, childrenlist=[]):
        self.name=name
        self.father=father
        self.childrenlist=childrenlist
    def setFather(self,father):
        self.father=father
    def getFather(self):
        return self.father.name
    def addChildren(self,child):
        self.childrenlist.append(child)
    def getChildren(self):
        return self.childrenlist




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



import GetAllMethodDIC


#这个函数对TreeDic进行修改，把filelist的所有继承树进行构建，TreeDIc【儿子】=fatherNode
def MakeTreeFromPath(filelist,TreeDic={}):
    for file in filelist:
      try:
        code = GetAllMethodDIC.readmethdpath(file)
        classname = file.split(".java")[0]
        if "/" in classname:
            classname = classname.split("/")[-1]
        elif "\\" in classname:
            classname = classname.split("\\")[-1]
        print(file)
        Fathername = getFatherFromCode(code)
        if classname not in TreeDic:
            classNode=TreeNode(classname)
            TreeDic[classname]=classNode
        if Fathername!='':
            if Fathername not in TreeDic:
                FatherNode=TreeNode(Fathername,None,[TreeDic[classname]])
                TreeDic[classname].setFather(FatherNode)
            else:
                FatherNode=TreeDic[Fathername]
                TreeDic[classname].setFather(FatherNode)
                FatherNode.addChildren(TreeDic[classname])
      except:
        print("FAILED"+file)
        continue



def MakeTreeFromOPath(LibPath,TreeDic = {}):
    dirlist, filelist = getAllClasses(LibPath, [], [])
    MakeTreeFromPath(filelist, TreeDic)
    return TreeDic


tree = javalang.parse.parse(
'''
package javalang.brewtab.com;import java.util.EventObject;
import java.awt.event.*;
import java.awt.peer.ComponentPeer;
import java.awt.peer.LightweightPeer;
import java.lang.reflect.Field;
import sun.awt.AWTAccessor;
import sun.util.logging.PlatformLogger;

import java.security.AccessControlContext;
import java.security.AccessController;
 public class ArrayStatement extends AbstractStatement {}
 ''')


m=1