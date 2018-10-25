pip install --user requests
pip install --user request
pip install --user portalocker
pip install --user gunicorn==19.9.0
pip install --user Flask==1.0.2
pip install --user Flask-Mobility==0.1
pip install --user urllib3
nohup python -u controller.py > err.log &
nohup python -u controller2.py > /dev/null & 

