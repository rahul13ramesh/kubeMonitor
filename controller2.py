import portalocker
import re
import json
import os
import os.path
import time
import datetime

from masterHelper import getNamespaces, getNodes


def getStat():
    """
    Get overview stats and dump to file
    """

    overviewDat = {"pods": []}
    #  Get namespaces, pod data and pods
    ns, dat, pods = getNamespaces()

    #  Write into json
    for dpt in dat:
        number = None
        numb = re.findall(r'\d+', dpt[3])
        if len(numb) >= 1:
                number = int(numb[0])
        if not(("Running" not in dpt[2]) and ("d" in dpt[3]) and (number is not None) and (number > 5)):
                tmpJ = {"namespace": dpt[0][:-10],
                    "podName": dpt[1],
                    "status": dpt[2],
                    "time": dpt[3]}
                overviewDat["pods"].append(tmpJ)
    #  Write json to file
    f = open("mainDat/summary.json", "w")
    portalocker.lock(f, portalocker.LOCK_EX)
    json.dump(overviewDat, f, indent=4)
    f.close()


wait_time = 30
while True:
    getStat()
    time.sleep(wait_time)
