Anatomy of an Experiment Management Framework
=============================================

An experiment management framework consists of the following key components:

* `namedconf`: flexible configuration specification system
* `dispatcher`: job dispatcher (process-, docker- or kubernetes-based, single- and multi-node)
* `mulogger`: multi-logger (log parameters, metrics and models per experiment to multiple logging backends)
* `qviz`: log visualization and querying (compare experiments, preferably UI-based)
* `mon`: monitoring (status of jobs, preferably UI-based)

LightEx includes independent modules for each component — `namedconf`, `dispatcher`, `mulogger`, `qviz`; others coming soon.

### Design 

* The primary use case is to run multiple simultaneous experiments, distributed across constrained resources.
* Simple, Decoupled design: develop, update or replace one component, while other parts remain the same. Allows us to add new dispatchers or loggers, and allow user to choose among them.
* Avoid reinventing the wheel - use well-known / stable programming abstractions for each component: 
    - dataclass for configuration
    - docker / k8s for job management
    - mlflow / tensorboard for logging.
* A nimble, unified config management system for jobs, parameters and model architectures: 
    - a configuration taxonomy for ML experiments using Python 3's dataclasses
    - easy to modify, inherit, specify config defaults.

#### Design Challenges

- Record experiments, visualize, compare logs: use mlflow's tracking server and UI
- Configuration management: be language independent, yet overcome deficiencies of `yaml` and `json`.
    * support easy modification, inheritance of configs.
- Seamlessly create parallel jobs and do job management: dockerize, use k8s job management
- Avoid complexity of full-blown k8s deployment for small teams: 
    * use docker / microk8s for a single or few node setup (quick to get up and running) 
    * mount code and data paths into containers for quick dev cycles
- Storage virtualization: enable jobs running on any node to access data (use nfs, minio)
- reduced learning curve for the tool itself: modular code, small code base


