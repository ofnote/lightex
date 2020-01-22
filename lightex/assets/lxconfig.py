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
    l1_ratio: float
    alpha: float

# hyperparameter group: unroll to multiple HPs
@dataclass(frozen=True)
class HPGroup:
    l1_ratio: List[int] 
    alpha: int

    def flatten(self):
        '''
        Unroll multi-HP config into a list of HP instances
        '''
        return unroll_top_fields(self, HP)

# the dispatcher takes in a list of experiment instances
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
        '''
        provide a list of experiment configs to the dispatcher
        '''
        hps = self.hpg.flatten()
        expts = [Experiment(er=self.er, hp=hp, run=self.run) for hp in hps]
        return expts


'''
Config Instances
'''

B1 = Build(image_url='pytorch_expt', 
            build_steps=['docker build -t pytorch_expt .'])
Co1 = Container(build=B1)

S1 = StorageDirs(data_dir='./data')
#L = LoggerConfig(names=['mlflow', 'trains'])

Lm = MLFlowConfig(port=5000)
L = LoggerConfig(mlflow=Lm)
R1 = Resources(storage=S1, ctr=Co1, loggers=L) #or ctr=None


# for k8 engine
# replace multiple attributes, recursively
R2 = rreplace (R1, {
                    'loggers.mlflow.client_in_cluster': True,
                    'loggers.mlflow.port': 30005,
                })


H1 = HPGroup(alpha=0.05, l1_ratio=[0.01, 0.015, 0.0015])

Ru1 = Run(
    cmd="python train.py --data-dir {{run.data_dir}} --output-dir {{run.output_dir}} --alpha {{hp.alpha}} \
                   --l1_ratio {{ hp.l1_ratio }}", #template refers to fields of Experiment instance
    experiment_name="find_hp",
    )

C1 = Config(er=R1, hpg=H1, run=Ru1)
C2 = replace(C1, er=R2) #for k8s

# run_expts.py -c C1 -e [process,docker,k8s]



if __name__ == '__main__':
    [print (x) for x in C1.get_experiments()]




































