
from flask import Flask
from flask import request
import json
import logging
from slaveController import getNodeUsage, writeFile

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


@app.route('/nodeInfo', methods=['POST'])
def sendDat():
    """
    * A API endpoint that accepts POST requests
    * The POST request must contain list of dockerIDs
    * End point returns the node resource usage, and usage of individual pods
      running in node
    """
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
