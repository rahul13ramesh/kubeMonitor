import os


def getMemUsage():
    """
    Get the nodes used/total memory
    """
    memOut = os.popen('free -g').read()
    x = memOut.split("\n")[1].split()
    memUsed, memTot = float(x[2]), float(x[1])

    return memUsed, memTot


def getCpuUsage():
    """
    Get the CPU's usage in node
    run -n 3 for top to get accurate usage(current usage)
    """
    cpuOut = os.popen("top -b -n 3 -d 1 | grep Cpu").read()
    cpuUsage = float(cpuOut.strip().split("\n")[2].split()[1])

    return float(cpuUsage)


def getGpuProc():
    """
    Get GPU details
    """
    gpuOut = os.popen("nvidia-smi").read()
    gpuOut = gpuOut.split("\n")

    
    if "not found" in gpuOut[0]:
        return []

    gpuDat = []
    procNum = 0

    #  Go to line with PID details
    for li in gpuOut:
        if "PID" in li:
            break
        procNum += 1

    ln = len(gpuOut)
    procNum += 2
    li = gpuOut[procNum]
    #  Iterate over all processes
    while ("-------------" not in li) and ("No running processes" not in li) and procNum < ln:

        li = li.split()
        #  If not a graphics process append GPU data
        if len(li) >= 6 and li[3].strip() != 'G':
            gpuDat.append([li[1], li[2], li[5]])
        procNum += 1
        li = gpuOut[procNum]

    return gpuDat


def getGpuUsage():
    """
    Query for gpu stats about node GPUs
    """
    gpuOut2 = os.popen(
        "nvidia-smi --query-gpu=utilization.gpu,memory.total,memory.used,gpu_name --format=csv").read()

    gpuUsageDat = []

    if "not found" in gpuOut2:
        return []

    gpuOut2 = gpuOut2.split("\n")
    for i in range(1, len(gpuOut2)):
        li = gpuOut2[i]
        li = li.split(", ")
        if len(li) != 4:
            break
        gpuUsageDat.append([li[3], li[0], li[1], li[2]])
    return gpuUsageDat

