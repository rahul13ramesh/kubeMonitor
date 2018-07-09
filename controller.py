import portalocker
import re
import json
import os
import os.path
import time
import datetime

from masterHelper import getNamespaces, getNodes
from masterHelper import getNodeInfo, getPodInfo


def initiate():
    ns, dat, pods = getNamespaces()
    nd = getNodes()

    nodeInf = getNodeInfo(nd)
    cont = getPodInfo(pods)

    allDat = {}
    for node in nodeInf:
        gpuMax = float(node[2])
        cpuMax = float(node[3])
        memMax = float(node[4][:-2]) / (1024 * 1024.0)

        reqInfo = node[6]
        reqInfo = reqInfo.strip().split()

        cpuNum = float(reqInfo[2])
        cpuPerc = float(re.findall(r'\d+', reqInfo[3])[0])
        memNum = float(re.findall(r'\d+', reqInfo[4])[0])
        memPerc = float(re.findall(r'\d+', reqInfo[5])[0])

        curJson = {
            "maxGpu": gpuMax,
            "maxCpu": cpuMax,
            "maxMem": memMax,
            "reqCpu": cpuNum,
            "reqCpuPer": cpuPerc,
            "reqMem": memNum,
            "reqMemPer": memPerc,
        }

        jobs = node[5]

        nodeCont = []
        curJsonJobs = {}
        for j in jobs:
            for c in cont:
                if c[1][1] == j[0] and c[1][0] == j[1]:
                    nodeCont.append((c[0], j[0], j[1]))
                    curJsonJobs[c[0]] = {
                        "namespace": j[0],
                        "podname": j[1],
                        "cpuReq": float(re.findall(r'\d+', j[4])[0]),
                        "cpuReqp": float(re.findall(r'\d+', j[5])[0]),
                        "memReq": float(re.findall(r'\d+', j[8])[0]),
                        "memReqp": float(re.findall(r'\d+', j[9])[0])
                    }

        curJson["jobs"] = curJsonJobs

        numNodes = len(nodeCont)
        f = open("mainDat/" + node[0] + "dockerId.txt", "w")
        portalocker.lock(f, portalocker.LOCK_EX)
        f.write(str(numNodes) + "\n")
        for i in range(numNodes):
            f.write(nodeCont[i][0] + "\n")
        f.close()

        allDat[node[0]] = curJson

    f = open("mainDat/allInf.txt", "w")
    portalocker.lock(f, portalocker.LOCK_EX)
    json.dump(allDat, f, indent=4)
    f.close()


def integrate():

    integratedData = {}
    integratedData["nodes"] = {}
    integratedData["pods"] = {}
    integratedData["time"] = datetime.datetime.now(
    ).strftime("%I %M %S %p %D %Y")

    f = open("mainDat/allInf.txt", "r")
    portalocker.lock(f, portalocker.LOCK_EX)
    allDat = json.load(f)
    f.close()

    nodes = allDat.keys()

    for no in nodes:

        if os.path.isfile("nodeDat/" + no + "-node.json"):
            f = open("nodeDat/" + no + "-node.json", "r")
            portalocker.lock(f, portalocker.LOCK_EX)
            nodeDat = json.load(f)
            f.close()
        else:
            nodeDat = {
                "noData": 1
            }

        if os.path.isfile("nodeDat/" + no + "-proc.json"):
            f = open("nodeDat/" + no + "-proc.json", "r")
            portalocker.lock(f, portalocker.LOCK_EX)
            procData = json.load(f)
            f.close()
        else:
            procData = {
            }

        nodeI = dict(nodeDat)
        nodeI["maxCpu"] = allDat[no]["maxCpu"]
        nodeI["maxMem"] = allDat[no]["maxMem"]
        nodeI["reqCpu"] = allDat[no]["reqCpu"]
        nodeI["reqCpuPer"] = allDat[no]["reqCpuPer"]
        nodeI["reqMem"] = allDat[no]["reqMem"]
        nodeI["reqMemPer"] = allDat[no]["reqMemPer"]

        integratedData["nodes"][no] = nodeI

        for jo in allDat[no]["jobs"]:
            jov = allDat[no]["jobs"][jo]

            if jov["namespace"] not in integratedData["pods"]:
                integratedData["pods"][jov["namespace"]] = []
            curjo = {
                "node": jov["podname"],
                "cpuReq": jov["cpuReq"],
                "cpuReqp": jov["cpuReqp"],
                "memReq": jov["memReq"],
                "memReqp": jov["memReqp"],
            }
            if jo in procData:
                curjo["gpuUsed"] = procData[jo]["gpuUsed"]
                curjo["gpuMem"] = procData[jo]["gpuMem"]
                curjo["cpuUtil"] = procData[jo]["cpuUtil"] * \
                    (1.0 / jov["cpuReq"])
                curjo["memUtil"] = procData[jo]["memUtil"] * \
                    (100.0 / jov["memReqp"])
            else:
                curjo["gpuUsed"] = -404
                curjo["gpuMem"] = -404
                curjo["cpuUtil"] = -404
                curjo["memUtil"] = -404
                curjo["noData"] = 1

            integratedData["pods"][jov["namespace"]].append(curjo)

    f = open("mainDat/aggregated.json", "w")
    portalocker.lock(f, portalocker.LOCK_EX)
    json.dump(integratedData, f, indent=4)
    f.close()

    overviewDat = {"pods": []}
    ns, dat, pods = getNamespaces()

    for dpt in dat:
        tmpJ = {
            "namespace": dpt[0][:-10],
            "podName": dpt[1],
            "status": dpt[2],
            "time": dpt[3]}
        overviewDat["pods"].append(tmpJ)


wait_time = 120
while True:
    initiate()
    time.sleep(wait_time)
    integrate()
