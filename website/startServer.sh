source /scratch/scratch1/rahul/virtualEnvs/monitor/bin/activate
 nohup gunicorn --bind 0.0.0.0:6277 myApp:app --workers 8  > web.log & 


