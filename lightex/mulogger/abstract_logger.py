import uuid
import os
from pathlib import Path

class AbstractLogger():
     #***THIS CLASS IS ABSTRACT AND MUST BE SUBCLASSED***

    name = 'alogger'

    def start_run(self, expt_id=None): raise NotImplementedError
    def end_run(self): raise NotImplementedError

    #log any scalar value
    def log_scalar(self, name, value, step):
        raise NotImplementedError

    # log a 1d vector. draw a histogram if `histogram` is True
    def log_1d(self, name, value, step, histogram: bool):
        raise NotImplementedError

    # log a 2d vector. draw a scatter-plot if `scatter` is True
    def log_2d(self, name, value, step, scatter: bool):
        raise NotImplementedError

    # log a 3d vector. draw a scatter-plot if `scatter` is True
    def log_3d(self, name, value, step, scatter: bool):
        raise NotImplementedError

    #log a hyper-parameter for the experiment
    def log_hparam(self, name, value):
        raise NotImplementedError

    # log artifacts, e.g., model files
    def log_artifacts(self, from_dir, artifact_path):
        '''
        :param from_dir: artifact originally stored in `from_dir` (temporarily)
        :param artifact_path: final location of artifact
        '''
        raise NotImplementedError

    def log_image(self, name, img: 'matrix', step):
        raise NotImplementedError

    def log_audio(self, name, audio, step):
        raise NotImplementedError
        

    def log_table(self, name, data, columns):
        raise NotImplementedError

    def save(self, files: str):
        raise NotImplementedError
    def restore(self, files: str):
        raise NotImplementedError




def get_experiment_name (experiment_name):
    #print (os.environ)
    if experiment_name is None:
        if 'LX_EXPERIMENT_NAME' in os.environ:
            experiment_name = os.environ['LX_EXPERIMENT_NAME'] 
        else:
            experiment_name = str(uuid.uuid4())[:8]
    return experiment_name

def get_project_name (project_name):
    if project_name is None:
        currdir = Path('.').resolve()
        project_name = currdir.parts[-1]
    return project_name






    