import os


def getNamespaces():
	x = os.popen('kubectl get pods --all-namespaces --show-all').read()

	dat = []
	ns = set()
	pods = []
	for l in x.split("\n"):
		l = l.strip().split()
		if len(l) > 0 and '-namespace' in l[0]:
			dat.append([l[0], l[1], l[3], l[5]])
			ns.add(l[0])
			pods.append((l[1], l[0]))
	ns = list(ns)
	return ns, dat, pods


def getNodes():
	x = os.popen('kubectl get nodes --no-headers').read()

	node = set()
	for l in x.split("\n"):
		l = l.strip().split()
		if len(l) > 0:
			if l[1] == "Ready" and l[0] != "master":
				node.add(l[0])
	node = list(node)
	return node

def getNodeInfo(nodes):
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
			if "Addresses:" in li:
				curList.append(nodeDesc[pos+1].strip().split()[1])
			if "Capacity:" in li:
				curList.append(nodeDesc[pos+1].strip().split()[1])
				curList.append(nodeDesc[pos+2].strip().split()[1])
				curList.append(nodeDesc[pos+3].strip().split()[1])
			if "Namespace" in li:
				tmpPos = pos + 2
				tmpLi = nodeDesc[tmpPos] 
				nodeJobs = []
				while "Allocated resources" not in tmpLi:
					tmpLi = tmpLi.split()
					if len(tmpLi) > 0  and "-namespace" in tmpLi[0]:
						nodeJobs.append(tmpLi)
					tmpPos += 1
					tmpLi = nodeDesc[tmpPos]
				curList.append(nodeJobs)
			if "Allocated resources" in li:
				curList.append(nodeDesc[pos+4])
			pos += 1
		nodeData.append(list(curList))
	return nodeData


def getPodInfo(pods):
	containers = []
	for po, ns in pods:
		cmd ='kubectl describe pods ' + po + ' --namespace ' + ns  + ' | grep "Container ID"' 
		podDesc = os.popen(cmd).read()
		cont = podDesc.strip().split("//")[1]
		containers.append((cont, (po, ns)))
	return containers


