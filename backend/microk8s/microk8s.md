### Basic Install

sudo apt install snap
sudo snap install microk8s --classic

###Enable DNS, GPU, Registry, Storage, Metrics on microk8s

microk8s.enable dns gpu registry storage metrics-server

### Enable Internet Access from within Cluster

`sudo iptables -P FORWARD ACCEPT`

More discussion [here](https://github.com/ubuntu/microk8s/issues/75).

### Setup 

Run `microk8s.config` to generate access credentials.

###Deploying the mlflow tracking server in microk8s

>  cd lightex/backend/mlflow

Build the mlflow-server docker container and push to microk8s' registry.

> docker build -t mlflow-server .
> docker tag mlflow-server localhost:32000/mlflow-server
> docker push localhost:32000/mlflow-server

OR

> docker build -t localhost:32000/mlflow-server .
> docker push localhost:32000/mlflow-server

Create kubernetes objects: the pod running mlflow tracker and a mlflow service for http access.

> microk8s.kubectl apply -f mlflow-service.yaml -f mlflow-tracking.yaml`


There are 2 components which are needed in kubernetes for getting a mlflow-tracking server.
1. A MLFlow tracking server StatefulSet (which retains the state even when the k8s cluster is restarted or the server restarts), which ensures a copy of the tracking server is always running in the k8s cluster
2. A service which exposes the mlflow tracking server with a static DNS endpoint for use within the cluster and a NodePort service which exposes the mlflow tracking server to the host machine

These 2 can be created by using the files **mlflow-service.yaml** and **mlflow-tracking.yaml**



Once these are created you can find the mlflow tracking server pod in the default namespace. The tracking server can be accessed at the port obtained from the following command at localhost
> microk8s.kubectl get svc mlflow-nodeport -ojsonpath='{.spec.ports[0].nodePort}'

# Training example
There is a sample training script in models/mlflow which can be started with the **batch.py** file. This requires the kubeconfig file to present in the same directory. This can be done by running 


Optionally this can also be saved at `~/.kube/config` which is the common location for storing the kube config file.

Once the batch.py file is run we can see pods created for the jobs we created in `batch.py`.

---

For accessing the cluster from a python script in microk8s it is necessary to get a few configuration properties from the cluster for the out of cluster config. The example for this is present in this [example](https://github.com/kubernetes-client/python/blob/master/examples/remote_cluster.py)

Another option is to use the kubeconfig file. This can be done by running 
> microk8s.config > kubeconfig

Now in the Python script we can use **config.load_kube_config(config_file='<path-to-kubeconfig>')** to load the kubrenetes configuration and interact with the kubernetes API server.

---


