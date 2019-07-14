Configuration Definitions
=========================

We use `dataclass`based definition of configuration. More like a *taxonomy* which can be locally modified and extended easily.

A typical configuration (for one or more experiments) is based on the following definitions:

```python
from dataclasses import dataclass
from lightex import K8Config, HostResources #pre-defined dataclasses

@dataclass
class Build: 
    image_url: str
    build_steps: List[str]
    image_pull_policy: str = "IfNotPresent"


@dataclass
class Run: #options specific to a given run, with some defaults
    cmd: str 										# python train.py --lr {{lr}}
    experiment_name: str 				# 'ex'
    run_name: str = ''					# 'ex-8'
    max_cpu: str = "500m"       # half a core
    max_memory: str ="2Gi"      # 2 GB Memory
    jobid: int = 0

@dataclass
class Resources: #all storage, container resources 
    build: Build
    k8: K8Config #docker container config
    host: HostResources

@dataclass
class HP: #all hyperparameters go here, can be nested
    batch_size: int = 4
    epochs: int = 10
    lr: float = 1e-3
    gpu_id: int = 0
    hidden_size: int = 512
    num_layers: int = 8
    # .. more

@dataclass 
class Experiment: #an experiment needs resources, specific hps, and run cmd options
    er: Resources
    hp: HP
    run: Run
```

The final config definition defines one or more experiments (here only one):

```python
@dataclass
class Config:
    er: Resources
    hp: HP
    run: Run

    def get_experiments(self): #required: generate a list of experiments to run
        expts = [Experiment(er=self.er, hp=self.hp, run=self.run)]
        return expts
```



### Configuration Instances

Now, create one or more instances of the `Config` class.

```python
B1 = Build(image_url='efnet:latest', 
            			build_steps=['docker build -t efnet:latest .', 
                    'docker push localhost:32000/efnet:latest'])

HO1 = HostResources(mlflow_dir=str(Path("/tmp/") / "mlflow-data"),
                    working_dir='.', 
                    data_dir='/data/imagenette-160/'
        )

R1 = Resources(build=B1, host=HO1, k8=K8Config())

H1 = HP(batch_size=16, epochs=1, gpu_id=0, model_name='efficientnet-b0')

RC1 = Run(
    cmd="python main.py {{er.k8.container_data_dir}} \
        -a {{hp.model_name}} --pretrained  -b {{hp.batch_size}} \
        -j 0  --epochs {{hp.epochs}} --gpu {{hp.gpu_id}}", 
    experiment_name="efnet0"
    )

C1 = Config(er=R1, hp=H1, run=RC1)
```

When dispatching experiments, we refer to config instances by name, e.g., `C1`. 

Now, we can quickly setup another related experiment configuration instance `C2`.

```python
from dataclasses import replace

H2 = replace(RC1, batch_size=8, epochs=2) 
C2 = Config(er=R1, hp=H1, run=RC1)
```





More examples under [this](../examples/) directory.

For now, `LightEx` assumes the dataclass structure of `Experiment` and nested fields. We will add more flexibility as new use cases arise. Conversion to `yaml` and`json` from a dataclass object is supported.