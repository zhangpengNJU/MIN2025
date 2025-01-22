#第一步用他的命令checkout project
#./defects4j_checkout.py [-f] [proj_name]...
#其实脚本里关键就一句话：d = os.path.join(base, name, rev)    base = os.path.join('data', 'in')

import subprocess

import os


import pickle

# 1:pv示例：-p Lang -v 1f
def getfixversion(pv, workpath):
    base = os.path.join('data', 'in')
    name = pv.split("-")[1][2:-1]
    rev = pv.split("-v ")[1]
    cwdpath = os.path.join(base, name, rev)
    p = subprocess.Popen('defects4j checkout ' + pv + ' -w ' + cwdpath, shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, cwd=workpath)
    p.communicate()
    return cwdpath


import os
import subprocess
import shutil


def getfixversion(pv, workpath):
    # Parse project and version information
    name = pv.split("-")[1][2:-1]
    rev = pv.split("-v ")[1]
    # Build the target directory path
    base = os.path.join('data', 'in')
    cwdpath = os.path.join(base, name, rev)
    # Temporary checkout directory
    temp_dir = '/tmp/0929'
    # Perform checkout to temporary directory
    checkout_command = f'defects4j checkout {pv} -w {temp_dir}'
    p = subprocess.Popen(checkout_command, shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, cwd=workpath)
    stdout, stderr = p.communicate()
    # Check if there was an error during checkout
    if p.returncode != 0:
        print("Checkout failed:", stderr.decode())
        return None
    # Ensure the target directory exists
    if not os.path.exists(cwdpath):
        os.makedirs(cwdpath)
    # Move files from the temporary directory to the target directory
    for item in os.listdir(temp_dir):
        s = os.path.join(temp_dir, item)
        d = os.path.join(cwdpath, item)
        if os.path.isdir(s):
            shutil.move(s, d)
        else:
            shutil.copy2(s, d)
    # Optionally clean up the temporary directory
    shutil.rmtree(temp_dir)
    return cwdpath



# 2:修改config
'''
################## Paths #####################
# Path to output directory
output.path=data/out/Chart/1f/

# Path to the project directory
project.path=data/in/Chart/1f/

# Path to the src root directory
source.path=data/in/Chart/1f/source/

# Path to lib directory
library.path=spoonLibs/Chart/

# Path to libWrapper.so (generated post-build)
wrapper.library.file=dist/libWrapper.so

# Path to model directories (comma-separated)
model.paths=models/50len_ident_lit/

# Path to idioms.csv
idioms.file=models/idioms.csv

# (Optional) Path to list of input methods
#input.methods.file=data/methods.input

'''
#要改的包括：output.path in->out； project.path:cwdpath=data/in/Chart/1f/;source.path=cwdpath+（从cat defects4j.build.properties得到d4j.dir.src.classes=）source；library.path=spoonLibs/+项目名+/
#但是考虑到spoonlibslib里面只有6个项目，所以只在6个项目上进行实验。

# 2.1.获取代码位置：
def getclasssrc(cwdpath):
    p = subprocess.Popen('cat defects4j.build.properties', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         cwd=cwdpath)
    z = p.stdout.read()
    p.communicate()
    lis = z.decode().split('d4j.dir.src.classes=')
    c = lis[1]
    lis = c.split('d4j.dir.src.tests')
    classname = lis[0][:-1]
    # classname = “src/main/java”
    return classname




def modifyConfig(cwdpath):
    config_path = "config"  # 配置文件路径
    # 读取配置文件
    with open(config_path, 'r') as file:
        lines = file.readlines()
    # 修改特定行
    for i in range(len(lines)):
        if lines[i].startswith("project.path="):
            lines[i] = "project.path=" + cwdpath + "\n"
        elif lines[i].startswith("output.path="):
            lines[i] = "output.path=" + cwdpath.replace("/in/", "/out/") + "\n"
        elif lines[i].startswith("source.path=") :
            a=getclasssrc(cwdpath)
            lines[i] = "source.path="+cwdpath +"/"+a+ "/\n"
        elif lines[i].startswith("library.path="):
            lines[i] = "library.path=spoonLibs/"+cwdpath.split("/")[2]+"/\n"
    # 写回配置文件
    with open(config_path, 'w') as file:
        file.writelines(lines)




#3.变异体生成（记录下生成的数目和时间）。
import re
import time

def generate():
    start_time = time.time()  # 记录函数开始时间
    p = subprocess.Popen('java -jar DeepMutation.jar config', shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    end_time = time.time()  # 记录函数结束时间
    execution_time = end_time - start_time  # 计算执行耗时
    # 检查 stderr 中是否有特定信息
    mutants_remaining = None
    took_time = -1
    if stdout:
        # 获取 mutants_remaining
        matches = re.findall(r'There are (\d+) methods and (\d+) mutants remaining\.', stdout.decode('utf-8'))
        if matches:
            # 获取最后一次匹配结果
            mutants_remaining = int(matches[-1][1])
        # 获取 took_time
        match_took = re.search(r'Took (\d+\.\d+) seconds', stdout.decode('utf-8'))
        if match_took:
            took_time = float(match_took.group(1))
    # 检查 mutants_remaining 是否为 None，如果是，则赋予默认值 -1
    if mutants_remaining is None:
        mutants_remaining = -1
    return mutants_remaining, execution_time, took_time



#main()
project = [
['Math', 1, 106, []], ['Mockito', 1, 38, []],
           ['Time', 1, 27, [21]]]



result=[]
for i in range(0, 6):
    for j in range(project[i][1], project[i][2] + 1):
        #print("i:", i, "j:", j, "project[i][0]:", project[i][0], "project[i][1]:", project[i][1])
        if j not in project[i][3]:
            try:
                p = project[i][0]
                v = str(j)
                pv = "-p " + p + " -v " + v + "f"
                workpath = "/home/fl/Desktop/DeepMu/DeepMutation/dist"
                cwdpath = getfixversion(pv, workpath)
                modifyConfig(cwdpath)
                ans = generate()
                print(ans)
                result.append([pv, i, j, ans])
            except:
                print("i:", i, "j:", j, " error")
                continue


