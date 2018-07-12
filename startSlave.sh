pip install --user flask
cd slave
nohup python -u api.py 2 &>1 &> err.log
cd ..

