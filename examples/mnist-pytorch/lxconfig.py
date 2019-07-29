from dataclasses import dataclass, replace
from typing import List
import os

from dacite import from_dict
from pathlib import Path

from lightex.mulogger import MLFlowConfig, LoggerConfig
from lightex.config_base import *

from lightex.namedconf import to_dict, rreplace

'''
Config Type Definitions
'''

@dataclass
class HP:
    batch_size: int = 64 
    test_batch_size: int = 1000 
    epochs: int = 1
    lr: float = 0.01 
    momentum: float = 0.5 
    enable_cuda: str = "True" 
    seed: int = 5 
    log_interval: int = 100 



@dataclass 
class Experiment:
    er: Resources
    hp: HP
    run: Run


@dataclass
class Config:
    er: Resources
    hp: HP
    run: Run

    def get_experiments(self):
        expts = [Experiment(er=self.er, hp=self.hp, run=self.run)]
        return expts



'''
Config Instances
'''


B1 = Build(image_url='ptlex:latest', 
            build_steps=['docker build -t ptlex:latest .'])

Co1 = Container(build=B1)
S1 = StorageDirs(working_dir='.', data_dir='./data')

L = LoggerConfig(mlflow=MLFlowConfig())

Re1 = Resources(storage=S1, ctr=Co1, loggers=L)



H1 = HP()

Ru1 = Run(
    cmd="python mnist_tensorboard_artifact.py \
            --data-dir {{run.data_dir}} \
            --batch-size {{hp.batch_size}} \
            --test-batch-size {{hp.test_batch_size}} \
            --epochs {{hp.epochs}} \
            --lr {{hp.lr}} \
            --momentum {{hp.momentum}} \
            --enable-cuda {{hp.enable_cuda}} \
            --seed {{hp.seed}} \
            --log-interval {{hp.log_interval}}",

    experiment_name="pt0",
    max_cpu="512m"
    )

# Docker config
C1 = Config(er=Re1, hp=H1, run=Ru1)

# process config
'''
Re2 = rreplace(Re1, {
                'loggers': {'mlflow': {
                        'client_in_cluster': False, 'port': 5000
                    }}
            })
C2 = Config(er=Re2, hp=H1, run=Ru1)

'''


if __name__ == '__main__':
    [print (x) for x in get_experiments(R1, H1)]




































