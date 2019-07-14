from dataclasses import dataclass
from pathlib import Path
from typing import List

from .mulogger import LoggerConfig
from .dispatch.config_containers import VolumeMount


@dataclass
class ContainerDirs:
    working_dir: str = '/project'
    data_dir: str = '/data'
    output_dir: str = '/output'

    def __post_init__(self):
        self.mlflow_dir: str = f"{self.output_dir}/mlflow"

    def get_dirs(self):
        return self.working_dir, self.data_dir, self.output_dir


@dataclass
class HostStore:
    working_dir: str = '.' #storage:input -- code lies here
    data_dir: str = '.'  #storage:input -- data lies here
    output_dir: str = '/tmp/ltex'  #storage:output -- output artifacts go here

    def __post_init__(self):
        # convert relative paths to absolute paths
        self.working_dir = str(Path(self.working_dir).resolve())
        self.data_dir = str(Path(self.data_dir).resolve())
        self.output_dir = str(Path(self.output_dir).resolve())

    def get_dirs(self):
        return self.working_dir, self.data_dir, self.output_dir


@dataclass
class Storage:
    host: HostStore  

    def get_source_dirs(self, storage_type):
        if storage_type == 'host':
            return self.host.get_dirs()
        else:
            raise NotImplementedError(f'Storage type {storage_type} not supported yet.')

    def get_volume_mounts(self, ctr, storage_type):
        '''
        storage_type: depending on storage_type, get the source directories
        '''
        assert ctr is not None
        working_dir, data_dir, output_dir = self.get_source_dirs(storage_type)
        m1 = VolumeMount(name='input-project', mount_path=ctr.working_dir,
                            host_path=working_dir, storage_type=storage_type)
        m2 = VolumeMount(name='input-data', mount_path=ctr.data_dir,
                            host_path=data_dir, storage_type=storage_type)
        m3 = VolumeMount(name='output-storage', mount_path=ctr.output_dir,
                            host_path=output_dir, storage_type=storage_type)
        #m3 = VolumeMount(name='mlflow-data', mount_path=loggers.mlflow.data_dir_mount,
         #                    host_path=loggers.mlflow.data_dir)
        return [m1, m2, m3] 



@dataclass(frozen=True)
class Build: 
    image_url: str
    build_steps: List[str]
    image_pull_policy: str = "IfNotPresent"


@dataclass(frozen=True)
class Resources:
    #host: HostStore 
    storage: Storage
    loggers: LoggerConfig
    build: Build = None # None if no containers used
    ctr: ContainerDirs = None # None if no container used

    def get_env(self, run: 'Run'): 
        '''return a list of key-value tuples'''
        return self.loggers.get_env() \
                + [('LX_EXPERIMENT_NAME', run.experiment_name)] \
                + [('MLFLOW_EXPERIMENT_NAME', run.experiment_name)]


    def get_volume_mounts(self):
        return self.storage.get_volume_mounts(ctr=self.ctr, store_type='host')


@dataclass(frozen=True)
class Run: 
    cmd: str
    experiment_name: str
    engine: str = 'process' #process, docker, k8s


    # TODO: move all below to an engine sub-config
    max_cpu: str = "1024m"  # Maximum of half a core
    max_memory: str ="2g"    # Maximum of 2 GB Memory
    persist: bool = True # keep the container / pod around, don't delete
    network: str = 'host' #the network which container belongs to

    run_name: str = None #dynamically assigned run name by dispatcher
    data_dir: str = None # dynamically assigned, either = host.data_dir or ctr.data_dir
    output_dir: str = None #dynamically assigned output_dir by dispatcher
    output_log_file: str = None #dynamically assigned by dispatcher

    def get_network(self): return self.network


