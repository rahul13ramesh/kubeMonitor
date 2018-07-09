# Note: all paths referenced here are relative to the Docker container.
#
# Add the Nvidia drivers to the path
export PATH="/usr/local/nvidia/bin:$PATH"
export LD_LIBRARY_PATH="/usr/local/nvidia/lib:$LD_LIBRARY_PATH"
source /tools/config.sh
# Tools config for CUDA, Anaconda installed in the common /tools directory
cd /tools/kubernetes/monitor
source /scratch/scratch1/rahul/virtualEnvs/monitor/bin/activate

python3 -u slaveController.py  &> outSlave
