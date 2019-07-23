from dataclasses import dataclass
from pathlib import Path
from typing import List

from .mulogger import LoggerConfig
from .dispatch.config_containers import VolumeMount


@dataclass
class Store:
    # a particular storage instance
    path: str = '.'     # access path
    stype: str = 'file' # storage type: file, nfs, s3, ...

    @property
    def url(self): 
        if self.stype == 'file': res = self.path
        else: raise NotImplementedError(f'{self.stype}') 
        return res
    @property
    def storage_type(self): return self.stype

    def __post_init__(self):
        if self.stype == 'file':
            self.path = str(Path(self.path).resolve())


@dataclass(init=False)
class StorageDirs:
    working: Store       #storage:input -- code lies here
    data: Store           #storage:input -- data lies here
    output: Store    #storage:output -- output artifacts go here

    def __init__(self, working_dir='.', data_dir='.', output_dir='/tmp/ltex'):
        self.working = Store(path=working_dir, stype='file')
        self.data = Store(path=data_dir, stype='file')
        self.output = Store(path=output_dir, stype='file')

    @property
    def working_dir(self): return self.working.url
    @property
    def data_dir(self): return self.data.url
    @property    
    def output_dir(self): return self.output.url
    
    def get_source_urls(self):
        return self.working_dir, self.data_dir, self.output_dir

    def get_stores(self):
        return self.working, self.data, self.output



@dataclass(frozen=True)
class Build: 
    image_url: str
    build_steps: List[str]
    Dockerfile_path: str = None
    image_pull_policy: str = "IfNotPresent"

@dataclass(frozen=True)
class Container:
    build: Build
    working_dir: str = '/project'
    data_dir: str = '/data'
    output_dir: str = '/output'

    def get_dirs(self):
        return self.working_dir, self.data_dir, self.output_dir

@dataclass(frozen=True)
class Resources:
    storage: StorageDirs
    loggers: LoggerConfig
    ctr: Container = None # None if no container used

    def get_env(self, run: 'Run'): 
        '''return a list of key-value tuples'''
        return self.loggers.get_env() \
                + [('LX_EXPERIMENT_NAME', run.experiment_name)] \
                + [('MLFLOW_EXPERIMENT_NAME', run.experiment_name)]


    def get_volume_mounts(self):
        assert self.ctr is not None

        working, data, output = self.storage.get_stores()
        ctrd = self.ctr
        m1 = VolumeMount(name='input-project', mount_path=ctrd.working_dir,
                            host_path=working.url, storage_type=working.storage_type)
        m2 = VolumeMount(name='input-data', mount_path=ctrd.data_dir,
                            host_path=data.url, storage_type=data.storage_type)
        m3 = VolumeMount(name='output-storage', mount_path=ctrd.output_dir,
                            host_path=output.url, storage_type=output.storage_type)
        return [m1, m2, m3] 

@dataclass(frozen=True)
class Run: 
    cmd: str
    experiment_name: str
    engine: str = 'process' #process, docker, k8s

    run_name: str = None #dynamically assigned run name by dispatcher
    data_dir: str = None # dynamically assigned, either = host.data_dir or ctr.data_dir
    output_dir: str = None #dynamically assigned output_dir by dispatcher
    output_log_file: str = None #dynamically assigned by dispatcher

    # TODO: move all below to an engine sub-config
    max_cpu: str = "1024m"  # Maximum of half a core
    max_memory: str ="2g"    # Maximum of 2 GB Memory
    persist: bool = True # keep the container / pod around, don't delete
    network: str = 'host' #the network which container belongs to
    def get_network(self): return self.network


