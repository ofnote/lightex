from typing import List
import copy
from dataclasses import dataclass, asdict, make_dataclass, field, replace
from dataclasses import is_dataclass

def is_dataclass_instance(obj):
    return is_dataclass(obj) and not isinstance(obj, type)

#refs
#https://github.com/python/cpython/blob/master/Lib/dataclasses.py
#https://stackoverflow.com/questions/53376099/python-dataclass-from-dict

def replace_dict(d: dict, path: List[str], value):
    o = copy.deepcopy(d)
    for f in path[:-1]: o = o[f]
    o[path[-1]] = value
    return o

def replace_rec (C: 'dataclass|dict', path: List[str], value):
    is_class_inst = hasattr(C, '__class__') 
    is_dict = isinstance(C, dict)

    if is_dict and not is_class_inst:
        return replace_dict(C, path, value)
    else:
        is_dataclass_inst = is_dataclass_instance(C)
        
        if len(path) > 1:
            D = getattr(C, path[0])
            D_ = replace_rec(D, path[1:], value)
        else:
            D_ = value

        if is_dataclass_inst:
            return replace(C, **{path[0]: D_})
        elif is_class_inst:
            C_ = copy.copy(C)
            setattr(C_, path[0], D_)
            return C_
        else:
            print(C)
            raise ValueError(f'unknown object')


def rreplace(C: 'dataclass', updates: dict):
    '''
    replace multiple (nested) fields in C
''
    e.g., updates = {'run.cmd': c, 'loggers.mlflow.client_in_cluster' = value}
        OR loggers: {mlflow: {client_in_cluster}}

    TODO: make it more efficient. 
    -- when asdict(C) works. asdict(C) -> replace_dict -> dacite.from_dict(class, .)
    '''
    changes = {}

    C1 = C
    for nfield, value in updates.items():
        path = nfield.split('.')
        # if path has multi-fields, replace C directly
        if len(path) > 1:
            C1 = replace_rec(C1, path, value)
        # else replace C in a nested way -- collect changes to replace at end
        else:
            D = getattr(C1, nfield)
            if isinstance(value, dict): D1 = rreplace(D, value)
            else: D1 = value
            changes[nfield] = D1

    return replace(C1, **changes)





'''
# impossible to guess if access path contains only dataclass fields (not some value dict field)
# constraint access paths to only dataclass fields, then can handle this 
#(the final leaf value is not a dict)
{
    'er': {
        'loggers.mlflow.client_in_cluster': False,
        'loggers.mlflow.port': 30005
        },

    'run': {
        'cmd': "python train.py --data-dir {{er.host.data_dir}} --alpha {{hp.alpha}} \
                   --l1_ratio {{ hp.l1_ratio }}"   
    }
}
'''