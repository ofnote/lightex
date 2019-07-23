from typing import List
from jinja2 import Template, DebugUndefined
from dataclasses import dataclass, asdict, make_dataclass, field, replace
from easydict import EasyDict as ED
from .replace_utils import rreplace, is_dataclass_instance
from dacite import from_dict

def to_dict(dc):
    return ED(asdict(dc))

def render_command(expt):
    if not isinstance(expt, dict):
        expt = to_dict(expt)
    #print (expt)
    rendered = Template(expt.run.cmd, undefined=DebugUndefined).render(expt)
    return (rendered)
    
def flatten_dict(d):
    out = []
    for key, val in d.items():
        if isinstance(val, dict):
            val = [val]
        if isinstance(val, list):
            for subdict in val:
                deeper = flatten_dict(subdict).items()
                out.update({key + '_' + key2: val2 for key2, val2 in deeper})
        else:
            out[key] = val
    return out

def flatten_field (f: str, ld: List[dict]):
    out = []
    for el in ld:
        for fval in el[f]:
            tmp = el.copy()
            tmp.update({f: fval})
            out.append(tmp)
    return out

def unroll_top_fields (D: 'dataclass_instance', target_dclass: dataclass):
    assert is_dataclass_instance(D)
    d = asdict(D)
    to_flatten = []
    for f, val in d.items():
        if isinstance(val, list):
            to_flatten.append(f)

    out = [d]
    for f in to_flatten:
        out = flatten_field(f, out)

    out = [from_dict(target_dclass, o) for o in out]
    return out



def update_dataconfig_with_args(C: 'dataclass', args: 'namespace'):
    updates = {}
    kvs = vars(args)
    for k, v in kvs.items():
        if '.' in k and v is not None: #temp hack; need filtering criteria
            updates[k] = v
    return rreplace(C, updates)

def load_config(config_dir, config_name, update_args=None):
    import sys
    sys.path.append(config_dir)

    from pathlib import Path
    config_file = Path(config_dir) / 'lxconfig.py'
    if not config_file.is_file():
        raise ValueError(f'Unable to find file "lxconfig.py" in directory: {config_dir}.'
                        f'Please specify your experiment configs in "lxconfig.py" in {config_dir}.')
    
    try:
        import lxconfig as M
    except:
        raise ValueError('Unable to load experiment configs from file "lxconfig.py"')
        
    C = getattr(M, config_name)

    if update_args is not None:
        C = update_dataconfig_with_args(C, update_args)

    return C


def to_yaml (C):
    import yaml
    d = asdict(C)
    return yaml.dump(d)



'''

def load_config2(name, config_file):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, config_file)
    M = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(M)
    C = getattr(M, name)
    return C

    def update_field(o, k, v):
        path = k.split('.')
        for f in path[:-1]:
            assert hasattr(o, f)
            o = getattr(o, f)
        assert hasattr(o, path[-1])
        setattr(o, path[-1], v)

'''


