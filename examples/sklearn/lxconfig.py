from dataclasses import dataclass, replace
from typing import List
from pathlib import Path

from lightex.mulogger import MLFlowConfig, LoggerConfig
from lightex.config_base import *
from lightex.namedconf import unroll_top_fields, to_dict, rreplace

'''
Named Config Definitions

Base definitions in lightex/config_base.py, lightex/mulogger/config.py

'''


@dataclass(frozen=True)
class HP:
    l1_ratio: float
    alpha: float

# hyperparameter group: unroll to multiple HPs
@dataclass(frozen=True)
class HPGroup:
    l1_ratio: List[int] 
    alpha: int

    def flatten(self):
        return unroll_top_fields(self, HP)

@dataclass(frozen=True)
class Experiment:
    er: Resources
    hp: HP
    run: Run


# Multi hyperparameter config
@dataclass(frozen=True)
class Config:
    er: Resources
    hpg: HPGroup
    run: Run

    def get_experiments (self):
        hps = self.hpg.flatten()
        expts = [Experiment(er=self.er, hp=hp, run=self.run) for hp in hps]
        return expts[:1]


'''
Config Instances
'''

B1 = Build(image_url='sklearn', 
            build_steps=['docker build -t sklearn .'])


#from lightex.mulogger.trains_logger import TrainsConfig
# trconf = TrainsConfig(config_file='./trains.conf')
L = LoggerConfig(loggers=['mlflow']) #trains=trconf
#L = LoggerConfig(mlflow=MLFlowConfig()) #trains=trconf

Co1 = Container(build=B1)
S1 = StorageDirs(working_dir='.')

R1 = Resources(storage=S1, ctr=Co1, loggers=L) 

H1 = HPGroup(alpha=0.05, l1_ratio=[0.01, 0.015, 0.0015])

Ru1 = Run(
    cmd="python train.py --data-dir {{run.data_dir}} --output-dir {{run.output_dir}} --alpha {{hp.alpha}} \
                   --l1_ratio {{ hp.l1_ratio }}",
    experiment_name="m2test",
    )

C1 = Config(er=R1, hpg=H1, run=Ru1)


# for k8 engine
# replace multiple attributes, recursively
R2 = rreplace (R1, {
                    'loggers.mlflow.client_in_cluster': True,
                    'loggers.mlflow.port': 30005,
                })
C2 = replace(C1, er=R2) #for k8s



if __name__ == '__main__':
    [print (x) for x in C1.get_experiments()]




































