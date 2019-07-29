from dataclasses import dataclass, replace
from typing import List

from dacite import from_dict
from pathlib import Path

from lightex.mulogger import MLFlowConfig, LoggerConfig
from lightex.config_base import Container, StorageDirs, Build, Resources, Run
from lightex.namedconf import unroll_top_fields, to_dict, rreplace


@dataclass
class HP:
    batch_size: int 
    epochs: int 
    gpu_id: int
    model_name: str


@dataclass
class HPG:
    batch_size: int 
    epochs: int 
    gpu_id: int
    model_name: List[str]

    def enumerate(self):
        return unroll_top_fields(self, HP)
        '''
        for m in self.model_name:
            hp = HP(batch_size=self.batch_size, epochs=self.epochs, gpu_id=self.gpu_id,
                    model_name=m)
            yield hp
        '''

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

@dataclass
class MConfig:
    er: Resources
    hpg: HPG
    run: Run

    def get_experiments(self):
        expts = [Experiment(er=self.er, hp=hp, run=self.run) for hp in self.hpg.enumerate()]
        return expts

'''
Config Instances
'''

B1 = Build(image_url='efnet:latest', 
            build_steps=['docker build -t efnet:latest .'])


Co1 = Container(build=B1)
S1 = StorageDirs(working_dir='.', data_dir='/data/imagenette-160')


L = LoggerConfig(mlflow=MLFlowConfig())
Re1 = Resources(storage=S1, ctr=Co1, loggers=L)

H1 = HP(batch_size=32, epochs=1, gpu_id=0, model_name='efficientnet-b0')
HPG1 = HPG(batch_size=16, epochs=1, gpu_id=0, model_name=['efficientnet-b0', 'efficientnet-b1'])

# docker engine
Ru1 = Run(
    cmd="python main.py {{run.data_dir}} --output-dir {{run.output_dir}}\
        -a {{hp.model_name}} --pretrained  -b {{hp.batch_size}} \
        -j 0  --epochs {{hp.epochs}} --gpu {{hp.gpu_id}}", # --experiment_name {{er.run.experiment_name}}

    experiment_name="efnet0"
    )


C1 = Config(er=Re1, hp=H1, run=Ru1)
C2 = MConfig(er=Re1, hpg=HPG1, run=Ru1)






































