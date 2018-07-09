from masterHelper import getNodes
import os


def start():
    nodes = getNodes()

    for no in nodes():
        no = "erdos"
        os.system("sed 's/templateMachine/" + no + "/' jobslave.template >  jobslave.yaml")
        os.system("kubectl create -f jobslave.yaml")


def reset():
    nodes = getNodes()
    for no in nodes():
        os.system("kubectl delete pod " + no + "monitor")


reset()
start()




