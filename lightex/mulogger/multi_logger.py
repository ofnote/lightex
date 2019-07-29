from dataclasses import dataclass
from typing import List
import os
from pathlib import Path
from easydict import EasyDict as ED
from .abstract_logger import AbstractLogger, get_experiment_name, get_project_name
from .config import MLFlowConfig, PytorchTBConfig, TermLogConfig, LoggerConfig



class MLFlowLogger(AbstractLogger):
    name = 'mlflow'

    def __init__(self, project_name=None, experiment_name=None, C: MLFlowConfig=None):
        import mlflow
        self.mlflow = mlflow
        uri = os.environ['MLFLOW_TRACKING_URI'] if C is None else C.uri()
        self.experiment_name = get_experiment_name(experiment_name)
        self.project_name = get_project_name(project_name)

        self.mlflow.set_tracking_uri(uri)
        self.mlflow.set_experiment(self.experiment_name)

    def start_run(self, expt_id=None): return self.mlflow.start_run(expt_id)
    def end_run(self): self.mlflow.end_run()

    #log any scalar value
    def log_scalar(self, name, value, step):
        self.mlflow.log_metric(name, value)

    #log hyper-parameter
    def log_hparam(self, name, value):
        self.mlflow.log_param(name, value)

    def log_artifacts(self, from_dir, artifact_path):
        self.mlflow.log_artifacts(from_dir, artifact_path=artifact_path)


class PytorchTBLogger(AbstractLogger):
    name = 'tb_pt'

    def __init__(self, C: PytorchTBConfig, project_name=None, experiment_name=None):
        from torch.utils.tensorboard import SummaryWriter
        self.writer = SummaryWriter(C.output_dir)
        self.project_name = get_project_name(project_name)
        self.experiment_name = get_experiment_name(experiment_name)

    def start_run(expt_id=None): pass
    def end_run(): pass

    def log_scalar(self, name, value, step):
        self.writer.add_scalar(name, value, step)

    def log_hparam(self, name, value):
        self.log_scalar(name, value, 0)

    def log_histogram(self, name, value, step):
        self.writer.add_histogram(name, value, step)

def get_conf(C, logger_name, default_class):
    if C is not None:
        conf = getattr(C, logger_name)
        if conf is not None:
            return conf
    else:
        return default_class()

def get_loggers(loggers):
    if loggers is not None:
        assert isinstance(loggers, list), "Provide a list of target loggers"
        return loggers
    loggers = os.environ['LX_LOGGERS'].split(',')
    #print('Declared Loggers: ', loggers)
    return loggers


class MultiLogger():
    name = 'multilogger'

    def __init__(self, loggers: List[str]=None, experiment_name=None, project_name=None, C: LoggerConfig=None):
        self.loggers = loggers
        self.experiment_name = get_experiment_name(experiment_name)
        self.project_name = get_project_name(project_name)
        self.name2logger = {}

        loggers = get_loggers(loggers)
        
        for l in loggers:
            if l == 'mlflow':
                mf_config = get_conf(C, l, MLFlowConfig)
                mlf = MLFlowLogger(self.project_name, self.experiment_name, mf_config)
                self.add_logger(l, mlf)
            elif l == 'tbpt':
                tb_config = get_conf(C, l, PytorchTBConfig)
                ptb = PytorchTBLogger(self.project_name, self.experiment_name, tb_config)
                self.add_logger(l, ptb)
            elif l == 'trains':
                from .trains_logger import TrainsLogger, TrainsConfig
                tr_conf = get_conf(C, l, TrainsConfig)
                tr = TrainsLogger(self.project_name, self.experiment_name, tr_conf)
                self.add_logger(l, tr)
            else:
                raise Exception(f'Unsupported logger name: {l}, Supported: {LoggerConfig._known_loggers}')

    def add_logger(self, name, logger_obj):
        #MultiLogger.register_logger(name, logger_obj.__class__.__name__)
        self.name2logger[name] = logger_obj

    def start_run(self, expt_id=None):
        for l, logger in self.name2logger.items(): logger.start_run(expt_id=expt_id)
    def end_run(self):
        for l, logger in self.name2logger.items(): logger.end_run()

    def get_loggers(self, logger_name):
        assert isinstance(logger_name, str)
        if logger_name == '*':
            res = list(self.name2logger.values())
        else:
            res = [self.name2logger[logger_name]]
        return res

    def _log(self, logger, ltype: str, **args):
        args = ED(args)

        if ltype == 'scalar':
            step = args.step if 'step' in args else 0
            logger.log_scalar(name=args.name, value=args.value, step=step)
        
        elif ltype == 'hp':
            logger.log_hparam(name=args.name, value=args.value)
        
        elif ltype == 'scalardict':
            step = args.step if 'step' in args else 0
            for k, v in args.value.items():
                logger.log_scalar(name=k, value=v, step=step)

        elif ltype == 'hpdict':
            for k, v in args.value.items():
                logger.log_hparam(name=k, value=v)
        
        elif ltype == 'img':
            step = args.step if 'step' in args else 0
            logger.log_image(name=args.name, img_matrix=args.img,step=step)

        elif ltype == '1d':
            histogram = args.histogram if 'histogram' in args else False
            logger.log_1d(name=args.name, value=args.value, histogram=histogram)
        elif ltype == '2d' or '3d':
            scatter = args.scatter if 'scatter' in args else False
            if ltype == '2d':
                logger.log_2d(name=args.name, value=args.value, scatter=scatter)
            else:
                logger.log_3d(name=args.name, value=args.value, scatter=scatter)

        else:
            print(f'log: unknown ltype = {ltype}')
            raise NotImplementedError

    def log(self, logger_name: str, ltype: str, **args):
        #print (f'args: {args}')
        loggers = self.get_loggers (logger_name)
        for logger in loggers:
            self._log(logger, ltype, **args)
        



class TerminalLogger(AbstractLogger): #placeholder for now, is this useful?
    name = 'fslogger'

    def __init__(self, project_name=None, experiment_name=None, C: TermLogConfig=TermLogConfig()):
        import logging
        self.experiment_name = get_experiment_name(experiment_name)
        #self.out_file = Path(C.output_dir_mount) / f'{self.experiment_name}.log'

        logging.basicConfig(#filename=self.out_file,
                            #filemode='a',
                            #format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=C.level)
        self.logger = logging.getLogger(self.experiment_name)
        self.logger.info('='*100)

    def log_text (self, s): self.logger.info(s)
    def print (self, s): self.log(s)






























