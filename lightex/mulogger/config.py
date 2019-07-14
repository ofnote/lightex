from dataclasses import dataclass
from typing import List
from pathlib import Path
import logging
from easydict import EasyDict as ED

@dataclass
class TermLogConfig: #Terminal Logger
    level: int = logging.DEBUG


@dataclass
class MLFlowConfig:
    _class_: str = 'MLFlowLogger'
    client_in_cluster: bool = False #whether client accessing the tracking server is within cluster or external
    # external access
    host: str ="http://localhost"
    port: int = 5000
    node_port: int = 30005 # for kubernetes deployment, fixed 

    # if backend in k8s cluster, then 
    # if client outside, port = 30005
    # if client in k8s, port = 5000

    # URI for cluster-internal access
    cluster_uri: str = "http://mlflow.default.svc.cluster.local:5000" 
    output_path_suffix: str = '/mlflow-data'

    def __post_init__(self):
        self.external_uri = f'{self.host}:{self.port}'

    def uri(self):
        if self.client_in_cluster:
            return self.cluster_uri
        else:
            return self.external_uri

    def get_env(self):
        return [('MLFLOW_TRACKING_URI', self.uri())]
        

@dataclass
class PytorchTBConfig:
    _class_: str = 'PytorchTensorBoardLogger'

    output_path_suffix: str = '/tblogs'

    def get_env(self):
        return []

class LoggerConfig(ED):
    _known_loggers = {
        'mlflow': MLFlowConfig,
        'tb_pt': PytorchTBConfig
    }

    def __init__(self, mlflow: MLFlowConfig = None, ptb: PytorchTBConfig=None):
        self.mlflow = MLFlowConfig() if mlflow is None else mlflow
        self.ptb = PytorchTBConfig() if ptb is None else ptb

    def register_logger (self, name, conf):
        self[name] = conf
        LoggerConfig._known_loggers[name] = conf.__class__.__name__

    def get_env(self):
        res = []
        for name, config in self.items():
            #print (config.get_env())
            res.extend(config.get_env())
        #print (f'logger: get_env: {res}')
        return res


if __name__ == '__main__':
    L = LoggerConfig(mlflow=MLFlowConfig())
    from trains_logger import TrainsConfig
    t = TrainsConfig()

    L.register_logger('trains', t)
    print (L)
