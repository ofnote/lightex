from dataclasses import dataclass, replace
from typing import List

from pathlib import Path

from lightex.mulogger import MLFlowConfig, LoggerConfig
from lightex.config_base import Container, StorageDirs, Build, Resources, Run
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
Co1 = Container(build=B1)

S1 = StorageDirs(working_dir='.', data_dir='./data')
L = LoggerConfig(mlflow=MLFlowConfig())
Re1 = Resources(storage=S1, ctr=Co1, loggers=L)

L = LoggerConfig(mlflow=MLFlowConfig())
#from lightex.mulogger.trains_logger import TrainsConfig
#L.register_logger('trains', TrainsConfig())

H1 = HP()

Ru1 = Run(
    cmd="python tensorflow_mnist_with_summaries.py --data_dir {{run.data_dir}}\
        --max_steps {{hp.max_steps}}\
        --log_dir {{run.output_dir}}/logs\
        --save_path {{run.output_dir}}/models/model.ckpt",
    experiment_name="tf_mnist_summ",
    )

C1 = Config(er=Re1, hp=H1, run=Ru1)



if __name__ == '__main__':
    [print (x) for x in C1.get_experiments()]




































