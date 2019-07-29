from dataclasses import dataclass
from typing import List
from . import AbstractLogger, get_experiment_name, get_project_name
from pathlib import Path


@dataclass
class WBConfig:
    #api_key: str = None #WANDB_API_KEY
    WANDB_DIR: str = './wandb' # WANDB_DIR
    mode: str = None #WANDB_MODE=dryrun to disable cloud sync
    WANDB_RUN_ID: str = None
    WANDB_RESUME: bool = False
    #WANDB_IGNORE_GLOBS

    def __post_init__(self):
        self.run_dir = Path(self.run_dir).resolve()


class WBLogger(AbstractLogger):
    name = 'wandb'

    def init_task_logger(self):
        self.task = self.trains.Task.init(project_name=self.project_name, task_name=self.experiment_name)
        self.logger = self.task.get_logger()

    def __init__(self, project_name=None, experiment_name=None, config=WBConfig()):
        import wandb
        self.wandb = wandb
        self.project_name = get_project_name(project_name)
        self.experiment_name = get_experiment_name(experiment_name)

        self.wandb.init(project=self.project_name, dir=config.WANDB_DIR, resume=config.WANDB_RESUME)

    def log_hparam(self, name, value): 
        self.wandb.config.update({name: value})

    def log_hparam_dict(self, args: dict):
        self.wandb.config.update(args)

    def log_scalar(self, name, value, step):
        self.wandb.log({name: value}, step=step)

    def log_scalar_dict(self, sc_dict, step):
        self.wandb.log(sc_dict, step=step)

    def log_1d(self, name, value, step, histogram):
        if histogram:
            value = self.wandb.Histogram(value)
        self.wandb.log({name: value}, step=step)

    def log_2d(self, name, value, step, histogram: bool=True):
        self.wandb.log({name: value}, step=step)

    def log_3d(self, name, value, step, scatter: bool):
        if not isinstance(value, (list,tuple)):
            value = [value]
        value = [self.wandb.Object3D(v) for v in value]
        self.wandb.log({name: value}, step=step)

    def log_image(self, name, img_matrix, step):
        self.wandb.log({
            name: [self.wandb.Image(img_matrix, caption=f'{name}')]
        }, step=step)

    def log_audio(self, name, audio_np, step):
        audio = self.wandb.Audio(audio_np, caption=f'{name}', sample_rate=32)
        self.wandb.log({name: [audio]}, step=step)


    def log_table(self, name, data, columns=["Input", "Output", "Expected"]):
        #data = [["I love my phone", "1", "1"],["My phone sucks", "0", "-1"]]
        #columns = ["Text", "Predicted Label", "True Label"]
        table = self.wandb.Table(data=data, columns=columns)
        self.wandb.log({name: table})

    def watch(self, model):
        self.wandb.watch(model)

    def save(self, files: str):
        self.wandb.save(files)
    def restore(self, files: str):
        self.wandb.restore(files)



