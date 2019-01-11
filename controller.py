import portalocker
import re
import json
import os
import os.path
import time
import datetime
import requests

from masterHelper import getNamespaces, getNodes
from masterHelper import getNodeInfo, getPodInfo


def initiate():

    #  Get nodes, namespaces and pods
    dat, ns, pods = getNamespaces()
    nd = getNodes()

    #  Get info and pod containers, node CPU, pods request CPU/MEM
    nodeInf = getNodeInfo(nd)
    cont = getPodInfo(pods)

    integratedData = {}
    integratedData["nodes"] = {}
    integratedData["pods"] = {}
    integratedData["time"] = datetime.datetime.now(
    ).strftime("%I %M %S %p %D %Y")

    #  Iterate over Ready nodes
    for node in nodeInf:
        gpuMax = float(node[2])
        cpuMax = float(node[3])
        memMax = float(node[4][:-2]) / (1024 * 1024.0)

        reqInfo = node[6]
        reqInfo = reqInfo.strip().split()

        #  Get the number of requests
        if 'm' in reqInfo[2]:
            cpuNum = int(int(re.findall(r'\d+', reqInfo[2])[0])/1000)
        else:
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
                        "node": node[0],
                        "cpuReq": float(re.findall(r'\d+', j[4])[0]),
                        "cpuReqp": float(re.findall(r'\d+', j[5])[0]),
                        "memReq": float(re.findall(r'\d+', j[8])[0]),
                        "memReqp": float(re.findall(r'\d+', j[9])[0])
                    }

        curJson["jobs"] = curJsonJobs

        numNodes = len(nodeCont)

        dockSend = []
        for i in range(numNodes):
            dockSend.append(nodeCont[i][0])

        # If end-point works
        try:
            #  Send a post request
            sendData = {'numIds': numNodes, 'id': dockSend}
            sendUrl = "http://" + node[1] + ":6277/nodeInfo"
            sendFiles = [
                ('datas', ('datas', json.dumps(sendData), 'application/json'))]
            r = requests.post(sendUrl, files=sendFiles, timeout=60)
            jsonStr = str(r.content, 'utf-8')
            returnDat = json.loads(jsonStr)
        except:
            print(node[0] + " : Endpoint failing")
            continue

        nodeDat = returnDat["n"]
        procData = returnDat["p"]

        nodeI = dict(nodeDat)
        nodeI["maxCpu"] = curJson["maxCpu"]
        nodeI["maxMem"] = curJson["maxMem"]
        nodeI["reqCpu"] = curJson["reqCpu"]
        nodeI["reqCpuPer"] = curJson["reqCpuPer"]
        nodeI["reqMem"] = curJson["reqMem"]
        nodeI["reqMemPer"] = curJson["reqMemPer"]

        integratedData["nodes"][node[0]] = nodeI

        for jo in curJson["jobs"]:
            jov = curJson["jobs"][jo]

            if jov["namespace"] not in integratedData["pods"]:
                integratedData["pods"][jov["namespace"]] = []
            curjo = {
                "podname": jov["podname"],
                "node": jov["node"],
                "cpuReq": jov["cpuReq"],
                "cpuReqp": jov["cpuReqp"],
                "memReq": jov["memReq"],
                "memReqp": jov["memReqp"],
            }
            if jo in procData:
                curjo["gpuUsed"] = procData[jo]["gpuUsed"]
                curjo["gpuMem"] = procData[jo]["gpuMem"]
                curjo["cpuUtil"] = procData[jo]["cpuUtil"] * \
                    (1.0 / max(1, jov["cpuReq"]))
                curjo["memUtil"] = procData[jo]["memUtil"] * \
                    (100.0 / max(1, jov["memReqp"]))
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


wait_time = 60
while True:
    initiate()
    time.sleep(wait_time)
