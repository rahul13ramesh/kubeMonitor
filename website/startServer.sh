pip install --user Flask==1.0.2
pip install --user Flask-Mobility==0.1.1
pip install --user gunicorn==19.9.0
pip install --user urllib3
pip install --user request
pip install --user requests
pip install --user portalocker
nohup gunicorn --bind 0.0.0.0:6277 myApp:app --workers 8  > web.log & 


