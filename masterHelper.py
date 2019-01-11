#!/usr/bin/env python3
"""
A collection of helper function used in master
"""
import os


def getNamespaces():
    """
    Get namespaces with active pods
    """
    x = os.popen('kubectl get pods --all-namespaces --show-all').read()

    dat = []
    ns = set()
    pods = []
    for l in x.split("\n"):
        li = l.strip().split()
        if len(li) > 0 and '-namespace' in li[0]:
            dat.append([li[0], li[1], li[3], li[5]])
            ns.add(li[0])
            pods.append((li[1], li[0]))
    ns = list(ns)
    return ns, dat, pods


def getNodes():
    """
    Get nodes which are in 'Ready' state
    """
    x = os.popen('kubectl get nodes --no-headers').read()

    node = set()
    for l in x.split("\n"):
        li = l.strip().split()
        if len(li) > 0:
            if li[1] == "Ready" and li[0] != "master":
                node.add(li[0])
    node = list(node)
    return node


def getNodeInfo(nodes):
    """
    For each node, get the requested CPU,Mem and GPU
    """
    nodeData = []
    for no in nodes:
        curList = []
        curList.append(no)
        nodeDesc = os.popen('kubectl describe nodes ' + no).read()
        nodeDesc = nodeDesc.split("\n")
        ln = len(nodeDesc)
        pos = 0
        while pos < ln:
            li = nodeDesc[pos]
            #  Get IP address
            if "Addresses:" in li:
                curList.append(nodeDesc[pos + 1].strip().split()[1])
            #  Get Max Capacity
            if "Capacity:" in li:
                tmpPos = pos
                li = nodeDesc[tmpPos]
                while "Allocatable" not in li:
                    if "nvidia-gpu" in li:
                        curList.append(li.strip().split()[1])
                    if "cpu" in li:
                        curList.append(li.strip().split()[1])
                    if "memory" in li:
                        curList.append(li.strip().split()[1])
                    tmpPos += 1
                    li = nodeDesc[tmpPos]
            #  Get namespaces with pods running on this node
            if "Namespace" in li:
                tmpPos = pos + 2
                tmpLi = nodeDesc[tmpPos]
                nodeJobs = []
                while "Allocated resources" not in tmpLi:
                    tmpLi = tmpLi.split()
                    if len(tmpLi) > 0 and "-namespace" in tmpLi[0]:
                        nodeJobs.append(tmpLi)
                    tmpPos += 1
                    tmpLi = nodeDesc[tmpPos]
                curList.append(nodeJobs)
            #  Get percentage of resources allocated(wrt total capacity of node)
            if "Allocated resources" in li:
                curList.append(nodeDesc[pos + 4])
            pos += 1
        nodeData.append(list(curList))
    return nodeData


def getPodInfo(pods):
    """
    Get request info for every pod
    """
    containers = []
    for po, ns in pods:
        cmd = 'kubectl describe pods ' + po + \
            ' --namespace ' + ns + ' | grep "Container ID"'
        podDesc = os.popen(cmd).read()
        if len(podDesc.strip().split("//")) >= 2:
            cont = podDesc.strip().split("//")[1]
            containers.append((cont, (po, ns)))
        else:
            continue
            #  Could run into here if pod just got killed when this function is
            #  called. Hence kubectl will return no info
            print(podDesc)
    return containers
