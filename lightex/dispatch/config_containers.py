from dataclasses import asdict, astuple
from dataclasses import dataclass, field
from typing import List

from docker.types import Mount

@dataclass
class VolumeMount:
    name: str
    mount_path: str
    host_path: str
    storage_type: str

@dataclass
class DockerConfig:
    image: str
    name: str
    command: list
    ports: dict = field(default_factory=dict)
    #volumes: dict = field(default_factory=dict)
    mounts: List[Mount] = field(default_factory=list)

    resources: dict = field(default_factory=dict)
    environment: dict = field(default_factory=dict)
    network: str = 'host'
    
    working_dir: str = None
    detach: bool = True
    auto_remove: bool = True

    def __post_init__(self):
        self.command = ' '.join(self.command)
        for key, value in self.resources.items():
            setattr(self, key, value)

        print (f'dockerconfig: {self.command}')

    def to_dict(self):
        #d = copy(self)
        #res.pop('resources')
        res = {}
        for k, v in self.__dict__.items():
            if k == 'resources': continue
            #v = f
            #if k == 'mounts': v = f
            #else: v = asdict(f)
            res[k] = v

        #print (res)
        return res


