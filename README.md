### LightEx

`LightEx` is a lightweight experiment framework to create, monitor and record your machine learning experiments. Targeted towards individual data scientists, researchers, small teams and, in general, resource-constrained experimentation.

#### Yet another experiment framework?
Systematic experimentation tools are essential for a data scientist. Unfortunately, many existing tools (`kubeflow`, `mlflow`, `polyaxon`) are too monolithic, kubernetes-first, cloud-first, target very diverse audiences and hence spread too thin, and yet lack important dev-friendly features. Other tools cater only to a specific task , e.g., `tensorboard` only handles log recording and visualization. Also, contrasting different experiment frameworks is hard: there is no standardized expt-management architecture for machine learning and most open-source frameworks are undergoing a process of adhoc requirements discovery. 


Our USP:

* We study the [anatomy of a ML experimentation framework](docs/anatomy.md). Identify principal components: flexible configuration, job dispatcher, multi-logger, log visualization and querying, storage virtualization.
* This informs the modular design of `LightEx`: all the key components are included and integrated via a flexible configuration manager. By design, the components are *decoupled*, *swappable* and can be developed independently. Codebase is small, easily navigable (hopefully stays that way).
* We don't re-invent the wheel. To create experiments, 
  * the job dispatcher builds over the subprocess/docker/kubernetes ecosystem, 
  * we reuse existing loggers and visualizers (`mlflow` is our primary log tracker, support `tensorboard`and extensible via *plugins*), and 
  * employ python `dataclass` based flexible and *unified* configuration specification for jobs, parameters and model architectures. Config instances are *named* and can be *locally modified*.

`LightEx` setup cost is low for your existing projects:

- Add or update your logging code using `LightEx`'s `multi_logger` API. 
- Update config instances in `config_expts.py` (mainly, the hyperparameter class `HP` and run command template `cmd`). Your `argparse` based code requires no other changes.


#### Getting Started :  Adopting LightEx Incrementally

* `pip install lightex`

We start with the Level-0 user, who runs experiments adhoc style: little or no configuration organization and tracking, naive log viewing (terminal or unorganized files), logging to tensorboard sparingly. At this stage, it is hard to run organize, keep track of, record, reuse multiple experiments. Move to Level 1.

- Level 1 User
  - `lx init` in your project directory. Creates `config.py` and `run_expts.py`
  - setup a logger backend (default is `mlflow`). See [backend](backend/)
  - LightEx provides a small set of pre-defined, nested configuration classes (`config.py`) to serve the most common ML experimentation needs. Update the fields of `config.py` based on your project.
    - move your argparse parameters to dataclasses in `config.py`
    - reuse run, build, resources config pre-defined in lightex (most of these only require filling with right values — see [config](docs/config.md) and [examples](examples/))
    - define a *named* config instance variable (say, `C1`) in `config.py` for one/multiple experiments
  - `run_expts.py —config C1 —engine process` to execute experiments defined as `C1` 
    - No other changes to your source code
  - use [mlflow UI](http://localhost:5000) to view track your runs. Experiment logs are stored in separate run directories.
- Level 2 - Better Logging, Comparison of runs.
  - use [mulogger](mulogger/) to log to mlflow and tensorflow simultaneously. Example [here](examples/sklearn/train.py#).
  - add your own logger [plugins](plugins/) (see [trains](plugins/trains) example), which follow a common logger API.
  - compare and visualize logs [under dev]
- Level 3 - you want to encapsulate the run environment and dependencies, scalable deployment 
  - include `Dockerfile` for your project, with all dependencies. See [examples](examples/pytorch-mnist)
  - update `build` and `run` configs in `config.py`
    - code and data are mounted into container from host paths
  - `run_expts.py -c C1 -e process` to execute experiments using docker containers. No other changes required.
  - switch engine to process mode for debugging, docker for deployment.
- Level 4 - you have a multi-node setup or want to be cloud-ready or simply prefer k8s [Under development] 
  - start storage virtualization server (e.g., nfs), (micro)k8s cluster
  - update `config.py` (build points to registry)
  - `run_expts.py —config C1 —e swarm` or `run_expts.py —config C1 —e k8s`
- Level 5 - diverse distributed storage options (S3, ceph) [Planned]



### Dependencies, Directory Structure

Python > 3.6 (require `dataclasses`). 

### Design Challenges

* A lot of an expt manager is about setting up and propagating a giant web of configuration variables. 
  * No optimal choice here: `json`,`yaml`,`jsonnet`— all formats have issues. 
  * Using `dataclass`es, we can write complex config specs, with built-in inheritance and ability to do *local updates*. Tiny bit of a learning curve here, but we gain a lot of flexibility.
* Read more on challenges [here](docs/anatomy.md).


### References

* Loggers: [trains](https://github.com/allegroai/trains), [Trixi](https://github.com/MIC-DKFZ/trixi), [ml_logger](https://github.com/episodeyang/ml_logger)
* Motivating Dataclasses [intro](https://blog.jetbrains.com/pycharm/2018/04/python-37-introducing-data-class/), [how-different](https://stackoverflow.com/questions/47955263/what-are-data-classes-and-how-are-they-different-from-common-classes)
* Flexible configuration
  * in modeling: allennlp, gin, jiant.
  * in orchestration: [ksonnet](https://github.com/ksonnet), kubernetes-operator 



### Random Notes

* Seamlessly move between `subprocess`-based, `docker`-based and `k8s`-based dispatch of experiment jobs.
* We target resource-constrained computing environments, small teams of researchers and quick dev-cycles. Though, hoping that our modular design simplifies scaling experiments to large clusters also.
* You can use `lightex` for your data pipelines and end-to-end preprocess-train pipelines also. Add new parameter fields (`HP`) corresponding to your data transformations.
* Read more about design challenges and solution [here](docs/anatomy.md).
* Be careful overwriting fields of nested configs directly. May change a shared field for multiple configs. Better to use `frozen=True` in config definition and `dataclass.replace` explicitly.
* `docker` and `kubernetes` add overhead to your dev workflow, but are worth it if you want better reproducibility of experiments and multi-node scaling. Some notes [here](https://www.reddit.com/r/MachineLearning/comments/c5qr9z/n_using_kubernetes_for_machine_learning/es3rrpo?utm_source=share&utm_medium=web2x). LightEx makes it easy for small ML teams to gradually add complexity to their workflow and dev infrastructure.
* We would like to see how 'multi-node' we can get without making the code too complex.
* Python Feature request: have a separate python extension for `dataclass` files, and loading a dataclass instance from a `dataclass` file.



### Common Errors

* ERROR mlflow.utils.rest_utils: API request to http://localhost:5000/api/2.0/preview/mlflow/runs/create failed with code 500 != 200, retrying up to 0 more times. API response body: {"error_code": "RESOURCE_DOES_NOT_EXIST", "message": "Could not find experiment with ID 0"}
  * Create an mlflow experiment. `MultiLogger::__init`__ should take care of this.
* `alias drmae='docker rm $(docker ps -a -f status=exited -q)'` 

