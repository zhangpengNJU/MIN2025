#用于分析class中引入了哪些java库
#要默认地import java.lang.*
import javalang
import os
import glob


LibDic={"java.applet":1,"java.awt":2,"java.beans":3,"java.io":4,"java.lang":5,"java.math":6,"java.net":7,"java.nio":8,"java.rmi":9,"java.security":10,"java.sql":11,"java.text":12,"java.time":13,"java.util":14,}
#返回所有的import的path string
def getImportsFromCode(code):
    tree = javalang.parse.parse(code)
    im=tree.imports
    imp=[]
    for i in im:
        imp.append(i.path)
    return imp


code='''
package javalang.brewtab.com;import java.util.EventObject;
import java.awt.event.*;
import java.awt.peer.ComponentPeer;
import java.awt.peer.LightweightPeer;
import sun.awt.AWTAccessor;
import sun.util.logging.PlatformLogger;

import java.security.AccessControlContext;
import java.security.AccessController;

import org.jfree.chart.ChartRenderingInfo;
import org.jfree.chart.LegendItem;
import org.jfree.chart.LegendItemCollection;
import org.jfree.chart.RenderingSource;
import org.jfree.chart.annotations.CategoryAnnotation;
import org.jfree.chart.axis.CategoryAxis;
import org.jfree.chart.axis.ValueAxis;
import org.jfree.chart.entity.CategoryItemEntity;
import org.jfree.chart.entity.EntityCollection;
import org.jfree.chart.event.RendererChangeEvent;
import org.jfree.chart.labels.CategoryItemLabelGenerator;
import org.jfree.chart.labels.CategorySeriesLabelGenerator;
import org.jfree.chart.labels.CategoryToolTipGenerator;
import org.jfree.chart.labels.ItemLabelPosition;

 public class ArrayStatement extends AbstractStatement {}
 '''

def isInLib(importpath):
    if not importpath.startswith("java."):
        return False
    #if "java.lang" in importpath:
    #    return True
    if "java."+importpath[5:].split(".")[0] in LibDic:
        return True
    return False

def getLibImportsFromCode(code):
    imp=getImportsFromCode(code)
    path=os.getcwd()+"/JDKparser/jdk-7fcf35286d52/src/share/classes/"
    #对于每一个元素，如果最后一个单词首字符大写，认为是一个类，可以直接导入，如果首字母小写，认为是一个文件夹，需要把其下全部.java文件导入。
    ans=[]
    for i in imp:
        if isInLib(i):
            last=i.split(".")[-1]
            if last[0].isupper():
                ans.append(i)
            else:
                path=path+i.replace(".","/")
                l = glob.glob(path + "/*.java")
                for li in l:
                    ans.append(i+"."+li[len(path)+1:-5])
    return ans


def getPKGImportsFromCode(code):
    imp = getImportsFromCode(code)
    ans = []
    for i in imp:
        if i.startswith("java"):
            continue
        if "*" not in i:
            ans.append(i)
    return ans



m=1


