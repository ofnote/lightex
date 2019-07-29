![experimental](https://img.shields.io/badge/stability-experimental-orange.svg)


## LightEx

`LightEx` is a lightweight experiment framework to create, monitor and record your machine learning experiments. Targeted towards individual data scientists, researchers, small teams and, in general, resource-constrained experimentation. Compatible with all machine-learning frameworks.

**Project Status:** Alpha

Unlike most experiment frameworks, `LightEx`sports a modular, and highly configurable design:

* **dispatcher**: run experiments using `process`,`docker` containers or `kubernetes` pods. Switch between modes seamlessly by minor changes to config.
* **mulogger**: log metrics and artifacts to multiple logger backends, using an *unified* API. Supports `mlflow`, `tensorboard` and `trains` — add new loggers easily as *plugins*.
* **namedconf**:  python `dataclass` based flexible and *unified* configuration specification for jobs, parameters and model architectures. Config instances are *named* and can be *locally modified*.
* **qviz**: query, compare and visualize your experiment results.

The run environment and parameters for your experiments are specified using a config file `lxconfig.py` in your project directory. Modify, inherit, and create new *named* config instances, on-the-fly, as you perform a series of experiments. 

Learn more about the **anatomy** of a ML experimentation framework [here](docs/anatomy.md).

#### Benefits

 Start with a basic `train` or `eval` project. In a few minutes,

* introduce systematic logging (multiple loggers) and visualization to your project
* go from running a single experiment to multiple parameterized experiments, e.g.,
  * multiple training runs over a set of hyper-parameters.
  * multiple `efficient-net` or `bert` train or eval runs.
  * a neural architecture search over multiple architectures in parallel.
    

### Installation

>  pip install -U lightex

### Quick Start

Assume we have an existing `train` project: run trainer with 

> `train.py --data-dir ./data —-lr 0.1 -—hidden_dim 512` 

In the main project directory, initialize `lightex` — this creates files `lxconfig.py` and `run_expts.py`.

> `lx—init`                               

The file `lxconfig.py` contains pre-defined `dataclass`es for specifying *named* experiment configs.

* The main (controller) class `Config`, contains three fields: `er` , `hp` and `run` (see below). 
* `Config` also includes a `get_experiments` function, which generates a list of experiment configs to be executed by the dispatcher. See [config.md](docs/config.md) for full description of the defined dataclasses.

```python

@dataclass
class Config:
    er: Resources 					#(Logger, Storage resources)
    hp: HP 							#(Hyper-parameters of model, training)
    run: Run 						#(Run-time config)

    def get_experiments(self): #required: generate a list of experiments to run
        expts = [Experiment(er=self.er, hp=self.hp, run=self.run)]
        return expts
```

Instantiate class `HP` with actual parameters, and class `Run` to mimic the command with placeholders.

```python
cmd="python train.py --data-dir {{run.data_dir}} --lr {{hp.lr}} --hidden_dim {{hp.hidden_dim}}" #placeholders refer to fields of Experiment instance
Ru1 = Run(cmd=cmd, experiment_name="find_hp")
H2 = HP(lr=1e-2, hidden_dim=512)

C1 = Config(er=R1, hp=H1, run=Ru1) #er defined elsewhere
```

Once config named `C1` is defined, run your experiments as follows:

> python run_expts.py -c C1

**That's it!** Now, your experiments, logs, metrics and models are organized and recorded systematically.

#### Modify Experiment Parameters, Experiment Groups

Modify configs from previous experiments quickly using `replace` and run new experiments. 

Example: Create a new `HP` instance and replace it in `C1` to create a new `Config`. Recursive replace also supported.

```python
H2 = HP(lr=1e-3, hidden_dim=1024)
C2 = replace(C1, hp=H2) #inherit er=R1 and run=Ru1
```

> python run_expts.py -c C2

To specify and run **experiment groups**, specify a set of `HP`s in a `HPGroup` (see [scripts/lxconfig.py](scripts/lxconfig.py)).

**Note**: Although LightEx pre-defines the dataclass hierarchy, it allows the developer plenty of flexibility in defining the individual fields of classes, in particular, the fields of the `HP` class. 

#### Adding Logging to your Code

Use the unified `MultiLogger` [API](lightex/mulogger) to log metrics and artifacts to multiple logger backends.

```python
from lightex.mulogger import MLFlowLogger, MultiLogger, PytorchTBLogger
logger = MultiLogger(['mlflow', 'trains'])
logger.start_run()
# log to trains only
logger.log('trains', ltype='hpdict', value={'alpha': alpha, 'l1_ratio': l1_ratio})
# log to mlflow only
logger.log('mlflow', ltype='scalardict', value={'mae': mae, 'rmse': rmse, 'r2': r2}, step=1)
# log to all
logger.log('*', ltype='scalardict', value={'mae': mae, 'rmse': rmse, 'r2': r2}, step=3)
# log scalars and tensors, if supported by the logger backend
logger.log('trains', ltype='1d', name='W1', value=Tensor(..), histogram=True, step=4)
logger.end_run()
```

Or, use one of the existing loggers' API directly.

```python
logger = MLFlowLogger()
mlflow = logger.mlflow
# call mlflow API

logger = PytorchTBLogger()
writer = logger.writer
#call tensorboard's API
```

**Note**: Except for changes in logging, no changes are required to your existing code!


#### Switch to Docker

Setting up the `lxconfig` instances pays off here! 

Now, add a `Dockerfile` to your project which builds the runtime environment with all the project dependencies. Update the `Build` instance inside `Resources` config. See [examples/sklearn](examples/sklearn), for example.

> python run_expts.py -c C2 -e docker

Both your code and data are mounted on the container (no copying involved) — minimal disruption in your dev cycle.

#### Advanced Features

More advanced features are in development stage.

**Modifying, Adding Loggers**

```python
Lm = MLFlowConfig(client_in_cluster=False, port=5000)
L = LoggerConfig(mlflow=Lm)
from lightex.mulogger.trains_logger import TrainsConfig
L.register_logger('trains', TrainsConfig())

R1 = Resources(build=..., storage=..., ctr=..., loggers=L)
```

More loggers and a better plugin system being developed.

**Running Experiments on multiple nodes / servers**

If you've setup a docker `swarm` or `kubernetes` cluster, few changes to the existing config instance allow changing the underlying experiment dispatcher.

We need to virtualize code (by adding to Dockerfile) and storage.

Create a shared NFS on your nodes. Switch storage config to the NFS partition. Setup scripts will be added.

**Setup Summary**

In summary, `LightEx` involves the following **one-time setup**:

- config values in `lxconfig.py`
- Setup backend logger servers (only the ones required). Instructions [here](backend/). (Optional)
- Update logging calls in your code to call `mulogger` API. (Optional)
- Dockerfile for your project, if you want to use containers for dispatch. (Optional)

While `LightEx` is quick to start with, it is advisable to spend some time understanding the [config schema](llightex/config_base.py).



### Dependencies

Python > 3.6 (require `dataclasses`, included during install). 



### Design Challenges

- A significant portion of experiment manager design is about setting up and propagating a giant web of configuration variables. 
  - No optimal choice here: `json`,`yaml`,`jsonnet`— all formats have issues. 
  - Using `dataclass`es, we can write complex config specs, with built-in inheritance and ability to do *local updates*. Tiny bit of a learning curve here, bound to python, but we gain a lot of flexibility.
- A unified `mulogger` API to abstract away the API of multiple logging backends.
- Designing multiple dispatchers with similar API, enabling containers and varying storage options.
- Read more on challenges [here](docs/anatomy.md).

### References

- ML Experiment Frameworks: [kubeflow](https://github.com/kubeflow/kubeflow), [mlflow](https://www.mlflow.org/docs/latest/index.html), [polyaxon](https://polyaxon.com/), ...
- Loggers: [sacred](https://sacred.readthedocs.io/en/latest/index.html), [trains](https://github.com/allegroai/trains), [Trixi](https://github.com/MIC-DKFZ/trixi), [ml_logger](https://github.com/episodeyang/ml_logger)
- Motivating Dataclasses [intro](https://blog.jetbrains.com/pycharm/2018/04/python-37-introducing-data-class/), [how-different](https://stackoverflow.com/questions/47955263/what-are-data-classes-and-how-are-they-different-from-common-classes)
- Flexible configuration
  - in modeling: allennlp, gin, jiant.
  - in orchestration: [ksonnet](https://github.com/ksonnet), kubernetes-operator 
- On the pains of ML experimentation
  - an article from [wandb](https://www.wandb.com/articles/iteratively-fine-tuning-neural-networks-with-weights-biases) 

Most current (July 2019 end) tools focus on the *logger* component and provide selective `qviz` components. `kubeflow` and `polyaxon` are tied to the (k8s) *dispatcher*. Every tool has its own version of config management — mostly *yaml* based, where config types are absent or have a non-nested config class. Config-specific languages have been also proposed (ksonnet, sonnet, gin).



### Yet another experiment framework?

Systematic experimentation tools are essential for a data scientist. Unfortunately, many existing tools (`kubeflow`, `mlflow`, `polyaxon`) are too monolithic, kubernetes-first, cloud-first, target very diverse audiences and hence spread too thin, and yet lack important dev-friendly features. `sacred` 's design is' tightly coupled and requires several `sacred`-specific changes to your main code (plan to add `sacred`logger as backend). Other tools cater only to a specific task , e.g., `tensorboard` only handles log recording and visualization. Also, contrasting different experiment frameworks is hard: there is no standardized expt-management architecture for machine learning and most open-source frameworks are undergoing a process of adhoc requirements discovery. 























