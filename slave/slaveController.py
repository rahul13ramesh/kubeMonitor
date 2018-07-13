import os
import shutil
import json
import time
import portalocker

from slaveHelper import getMemUsage, getCpuUsage
from slaveHelper import getGpuProc, getGpuUsage

gpuDat1 = None
gpuDat2 = None
machineName = os.popen("uname -n").read().strip()


def podUsage(containerId):
    global gpuDat1
    dockertxt = os.popen("ps ax | grep " + containerId).read()
    dockerId = 0
    for l in dockertxt.split("\n"):
        if "docker-containerd" in l:
            dockerId = l.split()[0]

    shellId = os.popen("pgrep -P " + dockerId).read()
    shellList = []
    for l in shellId.strip().split("\n"):
        shellList.append(l.strip())

    procList = []
    for s in shellList:
        proctxt = os.popen("pstree -p " + str(s) +
                           " | grep -o '([0-9]\+)' | grep -o '[0-9]\+'").read()
        for l in proctxt.strip().split("\n"):
            procList.append(l.strip())

    cpuUsage = 0
    memUsage = 0
    usedGpu = set()
    usedGpuMem = {}  # assumes machine has max 10 GPUs
    for pid in procList:
        pstxt = os.popen("ps -p " + pid + " -o pcpu,pmem").read()
        if len(pstxt.strip().split("\n")) >= 2:
            pstxt = pstxt.strip().split("\n")[1].strip().split()
            cpuUsage += float(pstxt[0])
            memUsage += float(pstxt[1])
            for d in gpuDat1:
                if pid == d[1]:
                    usedGpu.add(int(d[0]))
                    if int(d[0]) not in usedGpuMem:
                        usedGpuMem[int(d[0])] = 0
                    usedGpuMem[int(d[0])] += float(d[2].strip()[:-3])
    return cpuUsage, memUsage, list(usedGpu), usedGpuMem


def getNodeUsage(allCont):
    global gpuDat1
    global gpuDat2

    cpuMem = []

    cpuUsage = float(getCpuUsage())
    memUsage1, memTot = getMemUsage()
    gpuDat1 = getGpuProc()

    usedGpus = set()
    for dat in gpuDat1:
        usedGpus.add(int(dat[0]))

    gpuDat2 = getGpuUsage()

    for idc in allCont:
        cp, mem, gp, gpusage = podUsage(idc)
        cpuMem.append((cp, mem, gp, gpusage))

    return cpuMem, list(usedGpus), gpuDat2, cpuUsage, (memUsage1 / memTot)


def writeFile(cpuMem, gpus, gpuDat, cpu, mem, idList2):
    nodeDat = {}
    nodeDat["cpuUsage"] = float(cpu)
    nodeDat["memUsage"] = float(mem) * 100
    nodeDat["gpuUse"] = list(gpus)
    nodeDat["totGpu"] = len(gpuDat)

    for i in range(len(gpuDat)):
        gpuInfo = gpuDat[i]
        nodeDat["gpu" + str(i)] = {
            "name": gpuInfo[0],
            "util": float(gpuInfo[1].split()[0]),
            "memTot": float(gpuInfo[2].split()[0]),
            "memUsed": float(gpuInfo[3].split()[0])}

    procDat = {}
    for p, idL in zip(cpuMem, idList2):
        procDat[idL] = {
            "cpuUtil": p[0],
            "memUtil": p[1],
            "gpuUsed": p[2],
            "gpuMem": p[3]}

    masterDat = {"p": procDat, "n": nodeDat}
    return masterDat
