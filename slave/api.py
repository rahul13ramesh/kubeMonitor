
from flask import Flask
from flask import request
import json
from slaveController import getNodeUsage, writeFile

app = Flask(__name__)

@app.route('/nodeInfo', methods=['POST'])
def sendDat():
    posted_data = json.load(request.files['datas'])             
    numIds = posted_data['numIds']

    idList = []
    for i in range(numIds):
        idList.append(posted_data['id'][i])

    cpuMemDat, gpuUse, gpuDat, cpu, mem = getNodeUsage(idList)
    retdata = writeFile(cpuMemDat, gpuUse, gpuDat, cpu, mem, idList)
    
    return json.dumps(retdata, indent=4)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port='6277')
