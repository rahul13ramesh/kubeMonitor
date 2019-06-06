pip install --user flask
pip install --user portalocker
cd slave
varc=($(ps -u iitm | grep python | wc -l))
if [ $varc -ge 1 ]; then
	nohup python -u api.py >err.log &
fi
cd ..
sleep 5
ps ax | grep api.py

