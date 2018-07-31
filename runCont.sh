source /scratch/scratch1/rahul/virtualEnvs/monitor/bin/activate
nohup python -u controller.py > err.log &
nohup python -u controller2.py > /dev/null & 

