# Kube-Monitor

Master Setup
------------

* The controller or master node runs:

		git clone https://github.com/rahul13ramesh/kubeMonitor
		bash runCont.sh  # Periodically dumps data to aggregated.json
		nohup python -u controller2.py > /dev/null & 

		cd website
		bash startServer.sh
	
* The activated virtualenvironment contains dependencies listed in [requirements.txt](requirements.txt)

* The worker nodes also have the same python dependencies. The worker is
  required to run:

		bash startSlave.sh

* In order to start the GUI frontend(from Master) run :
   
		cd website
		bash startServer.sh

* The basic setup involves an API endpoint in each worker, which returns details
  about the pods running in the respective node.
* The data is aggregate at the master an exposed to the users via a GUI.


* Some screenshots:

![Alt text](assets/mobile1.png?raw=true "Mobile Screenshot 1")
![Alt text](assets/desk1.png?raw=true "Desktop Screenshot 1")



