pip install --user flask
pip install --user portalocker
cd slave
nohup python -u api.py > err.log  2>&1
cd ..

