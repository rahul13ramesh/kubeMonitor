from flask import Flask, render_template
import json
from flask_mobility import Mobility
from flask_mobility.decorators import mobile_template

app = Flask(__name__)
Mobility(app)


@app.route('/')
@mobile_template('{mobile/}summary.html')
def index(template):
    f = open("../mainDat/summary.json", "r")
    summ = json.load(f)
    f.close()
    return render_template(template, data=summ['pods'])


@app.route('/node')
@mobile_template('{mobile/}nodes.html')
def node(template):
    f = open("../mainDat/aggregated.json", "r")
    summ = json.load(f)
    f.close()
    nd = summ["nodes"]
    numGpus = {}
    gpuUsg = {}
    for n in nd:
        nume = 0
        denom = 0
        cnt = 0
        nd[n]["maxMem"] = str(int(float(nd[n]["maxMem"])))
        nd[n]["reqMem"] = str(int(float(nd[n]["reqMem"])))
        nd[n]["maxCpu"] = str(int(float(nd[n]["maxCpu"])))
        nd[n]["reqCpu"] = str(int(float(nd[n]["reqCpu"])))
        for l in range(int(nd[n]["totGpu"])):
            cnt += 1
            nume += nd[n]["gpu" + str(l)]["memUsed"]
            denom += nd[n]["gpu" + str(l)]["memTot"]
            nd[n]["gpu" + str(l)]["memTot"] = str(int(float(nd[n]["gpu" + str(l)]["memTot"])))
            nd[n]["gpu" + str(l)]["util"] = str(int(float(nd[n]["gpu" + str(l)]["util"])))
            nd[n]["gpu" + str(l)]["memUsed"] = str(int(float(nd[n]["gpu" + str(l)]["memUsed"])))
        numGpus[n] = cnt
        if denom == 0:
            gpuUsg[n] = 0
        else:
            gpuUsg[n] = int(float(nume) / denom * 100)
    return render_template(template, data=summ['pods'], nodeData=nd,
                           gpuUsg=gpuUsg, numGpus=numGpus, str=str,
                           sorted=sorted, len=len)


@app.route('/pod')
@mobile_template('{mobile/}pods.html')
def pod(template):
    f = open("../mainDat/aggregated.json", "r")
    summ = json.load(f)
    f.close()
    pd = summ['pods']
    nd = summ['nodes']

    for p in pd:
        count = 0
        for job in pd[p]:
            node = job['node']
            nume = 0
            denom = 0
            for gp in job['gpuUsed']:
                denom += nd[node]['gpu' + str(gp)]['memTot']
                nume += job['gpuMem'][str(gp)]
            if denom == 0:
                pd[p][count]["avgGpuUsg"] = 0
            else:
                pd[p][count]["avgGpuUsg"] = int(float(nume*100)/denom)
            count += 1

    return render_template(template, data=pd, sorted=sorted, len=len,
                           int=int, str=str, nodeDat=nd)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
