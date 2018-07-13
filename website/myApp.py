from flask import Flask, render_template
import json
app = Flask(__name__)


@app.route('/')
def index():
    f = open("../mainDat/summary.json", "r")
    summ = json.load(f)
    f.close()
    return render_template("summary.html", data=summ['pods'])


@app.route('/node')
def node():
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
        gpuUsg[n] = int(float(nume) / denom * 100)
    return render_template("nodes.html", data=summ['pods'], nodeData=nd,
                           gpuUsg=gpuUsg, numGpus=numGpus, str=str,
                           sorted=sorted)


@app.route('/pod')
def pod():
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
                nume += gp['gpuMem'][str(gp)]
            count += 1
            pd[p][count]["avgGpuUsg"] = int(float(nume*100)/denom)

    return render_template("pods.html", data=pd, sorted=sorted, len=len,
                           int=int, str=str, nodeDat=nd)


if __name__ == '__main__':
    app.run(debug=True)
