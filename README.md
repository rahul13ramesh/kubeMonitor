# Kube-Monitor

Master Setup
------------

* The controller or master node runsj

	git clone https://github.com/rahul13ramesh/kubeMonitor
	bash runCont.sh  # Periodically dumps data to aggregated.json
	nohup python -u controller2.py > /dev/null & 

	cd website
	bash startServer.sh
	
* The activated virtualenvironment contains dependencies listed in [requirements.txt](requirements.txt)

