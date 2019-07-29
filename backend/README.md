### Logger Backends

#### WandB

Run `wandb login` from your terminal to signup or authenticate your machine (we store your api key in ~/.netrc). You can also set the `WANDB_API_KEY` environment variable with a key from your [settings](https://app.wandb.ai/settings).



#### MLFlow

Start mlflow tracker:

*  With Docker
  * `docker-compose up --force-recreate -d mlflow` 
  * Modify `.env` file to change the default directories.

#### Trains

Install `trains-server` (backend) and `trains` (client) library:

##### Installing Backend

> git clone https://github.com/allegroai/trains-server
> Update docker daemon and systemctl settings (see [installation](https://github.com/allegroai/trains-server#installation))
>
> `sudo sysctl -w vm.max_map_count=262144`
>
> cd `backend/trains/` #use the `docker-compose.yaml` and `.env` here
> update `.env` with TRAINS data directory path (default is `/opt/trains`)
> create sub-directories (TODO: add instructions)
> `docker-compose up`

Access trains UI at `localhost:8080`

##### Install Trains Client

> `pip install -U trains`
>
> `trains-init` # create ~/trains.conf, ensure server points to localhost:8008, get keys from trains UI.
>
> `mv ~/trains.conf .` #trains.conf should be able to access this file during the run

Finally, in `lxconfig.py` for your project:

```python
trconf = TrainsConfig(config_file='./trains.conf')
L = LoggerConfig(trains=trconf)
```






### Monitoring Backends

* Docker Monitoring
  * Terminal: [dry](https://github.com/moncho/dry)
  * UI: [portainer](https://www.portainer.io/) , [swarmpit](https://github.com/swarmpit/swarmpit)



## Dispatchers



### Docker, Docker-Compose, Docker-Swarm

- Install `docker`

- Install `docker-compose` [link](https://docs.docker.com/compose/install/)

  

#### MicroK8s / Kubernetes

- Setup your k8s cluster
- Refer to [this](microk8s/microk8s.md) file for setting up mlflow.
  - tldr:` kubectl apply -f mlflow/`





###  