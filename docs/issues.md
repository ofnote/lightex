

## TODO

[ ] User experience - watch all logs, debug failed pods

[ ] Give new job ids to each new process for an expt_name

[ ] Do project build via config; include docker push to registry

[ ] Abstract away volumeMounts for train job as well as mlflow. minio? ceph?

    - [ ] Abstractions for train job: volume mounts input_dir, output_dir -> NFS. train command. 

[ ] Better `make_job`

    - [X] in-memory creation of job

    - [ ] graceful failure - Let create_job validate the fields it needs before trying to create.
    
    - [ ] Option to auto-remove failed jobs on executing batch.py OR delete jobs of same name on start

    - [ ] scheduler: controlling how large num of jobs / experiments are created 


[ ] from one local machine -> 2 local machines (with minimal code changes)

[ ] from one AWS machine -> 2 AWS machines

[ ] Simplify going from argparse arguments to Run.cmd
    
    - [X] option to update config instance from command line

[?] runtime config via configMaps / secrets? how far can we go with command line gen of pod yamls?

[X] Single logging API (combines multiple backend loggers)

[X] Add a GPU based example

[X] a more compact yaml format for k8s -- dataclass

[X] What arguments to pass to train.py ? user should not have to parse config file.

[X] Spec for job resource in run (1gb mem)

[X] abstract command from k8sutils into config

[X] Expose input and output directories, image name from job.yaml.j2 as parameters

[X] a config format for different experiments and pipe it all the way to the yaml.j2 -- dataclass


## Design

- Model outputs -- mlflow: metadata store, artifact store 
 * right now, mapped to host volume path
 * initialization
    * backend/metadata store: hostpath or sql connection
    * artifact store: hostpath OR minio OR s3://, azure, gfs
    * so 2 modes: (a) both backend, artifact on hostpath (b) backend on sql, artifact on minio
 * experiments: specify a new path (both backend and artifact?) [dynamic - avoid this!]


* best way to import code into container while iterating? 
    - add code to container (manage container versions)
    - add code to container on-the-fly (through git)

- Difference between service.yaml and tracking.yaml? merge?
- Switch between filemount mode for *dev* vs 'minio' for deploy mode?

- how to access mlflow stored logs.files?
