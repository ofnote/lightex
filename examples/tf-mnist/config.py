from dataclasses import dataclass, replace
from typing import List
import os

from pathlib import Path

from lightex.mulogger import MLFlowConfig, LoggerConfig
from lightex.config import ContainerDirs, HostStore, Storage, Build, Resources, Run

from lightex.namedconf import unroll_top_fields, to_dict, rreplace

'''
Named Config Definitions

Base definitions in lightex/config.py, lightex/mulogger/config.py

'''


@dataclass(frozen=True)
class HP:
    learning_rate: float = 0.001
    dropout: float = 0.9
    max_steps: int = 10


@dataclass(frozen=True)
class Experiment:
    er: Resources
    hp: HP
    run: Run


# Multi hyperparameter config
@dataclass(frozen=True)
class Config:
    er: Resources
    hp: HP
    run: Run

    def get_experiments (self):
        expts = [Experiment(er=self.er, hp=self.hp, run=self.run)]
        return expts[:1]


'''
Config Instances
'''

B1 = Build(image_url='tensorflow/tensorflow:latest-devel-gpu-py3', 
            build_steps=[]) #'docker build -t xx .'])

Ho1 = HostStore(working_dir='.', data_dir='./data')
S1 = Storage(host=Ho1)
Co1 = ContainerDirs()

Lm = MLFlowConfig(client_in_cluster=False, port=5000)
L = LoggerConfig(mlflow=Lm)
from lightex.mulogger.trains_logger import TrainsConfig
L.register_logger('trains', TrainsConfig())

R1 = Resources(build=B1, storage=S1, ctr=Co1, loggers=L)
H1 = HP()

Ru1 = Run(
    cmd="python tensorflow_mnist_with_summaries.py --data_dir {{run.data_dir}}\
        --max_steps {{hp.max_steps}}\
        --log_dir {{run.output_dir}}/logs\
        --save_path {{run.output_dir}}/models/model.ckpt",
    experiment_name="tf_mnist_summ",
    )

C1 = Config(er=R1, hp=H1, run=Ru1)



if __name__ == '__main__':
    [print (x) for x in C1.get_experiments()]




































