pip install --user flask
pip install --user portalocker
cd slave
nohup python -u api.py >err.log &
cd ..
sleep 5
ps ax | grep api.py

