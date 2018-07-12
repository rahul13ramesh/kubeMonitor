pip install --user flask
cd slave
nohup python -u api.py > err.log  2>&1
cd ..

