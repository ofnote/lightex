Configuration Definitions
=========================

We use `dataclass`based definition of configuration. More like a *taxonomy* which can be locally modified and extended easily.

A typical configuration (for one or more experiments) is based on the following definitions:

```python
from dataclasses import dataclass

@dataclass
class Store: # a particular storage instance
    url: str = '.'     # access path
    stype: str = 'file' # storage type: file, nfs, s3, ...
      
@dataclass
class Build: 
    image_url: str
    build_steps: List[str]
    Dockerfile_path: str = None
    image_pull_policy: str = "IfNotPresent"

@dataclass
class Container:
    build: Build
    dirs: ContainerDirs = ContainerDirs()
      
@dataclass
class StorageDirs:
    working_dir: Store       #storage:input -- code lies here
    data_dir: Store           #storage:input -- data lies here
    output_dir: Store       #storage:output -- output artifacts go here

@dataclass
class Run: #options specific to a given run, with some defaults
    cmd: str 										# python train.py --lr {{lr}}
    experiment_name: str 				# 'ex'
    run_name: str = ''					# 'ex-8'
    max_cpu: str = "500m"       # half a core
    max_memory: str ="2Gi"      # 2 GB Memory
    ...													# more fields (see lightex/base_config.py)

@dataclass(frozen=True)
class Resources:
    storage: StorageDirs  # storage paths / urls
    loggers: LoggerConfig # config for multiple loggers
    ctr: Container = None # None if no container used

      
@dataclass
class HP: #all hyperparameters go here, can be nested
    batch_size: int = 4
    epochs: int = 10
    lr: float = 1e-3
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

Note: all dataclasses are defined to be `frozen` : `@dataclass(frozen=True)`


### Configuration Instances

Now, create one or more instances of the `Config` class.

```python
B1 = Build(image_url='efnet:latest', 
            			build_steps=['docker build -t efnet:latest .', 
                    'docker push localhost:32000/efnet:latest'])
Co1 = Container(build=B1)
S1 = StorageDirs(data_dir='/data/imagenette-160/') #defaults: working_dir and output_dir
L = LoggerConfig(names=['mlflow', 'trains'])
R1 = Resources(storage=S1, ctr=Co1, loggers=L) #or ctr=None

H1 = HP(batch_size=16, epochs=10, model_name='efficientnet-b1')

Ru1 = Run(
    cmd="python main.py --data-dir {{run.data_dir}} \
        -a {{hp.model_name}} --pretrained  -b {{hp.batch_size}} \
        -j 0  --epochs {{hp.epochs}} --gpu {{hp.gpu_id}}", 
    experiment_name="efnet0"
    )

C1 = Config(er=R1, hp=H1, run=Ru1)
```

When dispatching experiments, we refer to config instances by name, e.g., `C1`. 

Now, we can quickly setup another related experiment configuration instance `C2`.

```python
from dataclasses import replace

H2 = replace(H1, model_name='efficientnet-b2') # batch_size and epochs remain same
C2 = Config(er=R1, hp=H2, run=Ru1)
```





More examples under [this](../examples/) directory.

For now, `LightEx` assumes the dataclass structure of `Experiment` and `Config` but allow flexibility with fields of classes, e.g., `HP`. Conversion to `yaml` and`json` from a dataclass object is supported.