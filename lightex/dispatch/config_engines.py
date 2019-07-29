from dataclasses import asdict, astuple
from dataclasses import dataclass, field
from typing import List


@dataclass
class ProcessConfig:
    log_to_file: bool 
    async_exec: bool