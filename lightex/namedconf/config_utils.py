import sys
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

def argparse_to_command (args, add_placeholders=True, values_are_names=True):
    #print (vars(args))
    res = [sys.argv[0]]
    for k, v in vars(args).items():
        val = f'{k}' if values_are_names else f'{v}'
        if add_placeholders:
            val = '{{' + val + '}}'
        res.append(f'--{k} ' + val)
    return ' '.join(res)


def test_argparse_to_command ():
    import argparse
    parser = argparse.ArgumentParser(description='PyTorch ImageNet Training')
    parser.add_argument('data', metavar='DIR',
                        help='path to dataset')
    parser.add_argument('--output-dir', help='path to model output dir')

    parser.add_argument('-a', '--arch', metavar='ARCH', default='resnet18',
                        help='model architecture (default: resnet18)')
    parser.add_argument('-j', '--workers', default=4, type=int, metavar='N',
                        help='number of data loading workers (default: 4)')
    parser.add_argument('--epochs', default=90, type=int, metavar='N',
                        help='number of total epochs to run')
    parser.add_argument('--start-epoch', default=0, type=int, metavar='N',
                        help='manual epoch number (useful on restarts)')
    parser.add_argument('-b', '--batch-size', default=256, type=int,
                        metavar='N',
                        help='mini-batch size (default: 256), this is the total '
                             'batch size of all GPUs on the current node when '
                             'using Data Parallel or Distributed Data Parallel')
    parser.add_argument('--lr', '--learning-rate', default=0.1, type=float,
                        metavar='LR', help='initial learning rate', dest='lr')
    parser.add_argument('--momentum', default=0.9, type=float, metavar='M',
                        help='momentum')
    parser.add_argument('--wd', '--weight-decay', default=1e-4, type=float,
                        metavar='W', help='weight decay (default: 1e-4)',
                        dest='weight_decay')
    parser.add_argument('-p', '--print-freq', default=10, type=int,
                        metavar='N', help='print frequency (default: 10)')
    parser.add_argument('--resume', default='', type=str, metavar='PATH',
                        help='path to latest checkpoint (default: none)')
    parser.add_argument('-e', '--evaluate', dest='evaluate', action='store_true',
                        help='evaluate model on validation set')
    parser.add_argument('--pretrained', dest='pretrained', action='store_true',
                        help='use pre-trained model')
    parser.add_argument('--world-size', default=-1, type=int,
                        help='number of nodes for distributed training')
    parser.add_argument('--rank', default=-1, type=int,
                        help='node rank for distributed training')
    parser.add_argument('--dist-url', default='tcp://224.66.41.62:23456', type=str,
                        help='url used to set up distributed training')
    parser.add_argument('--dist-backend', default='nccl', type=str,
                        help='distributed backend')
    parser.add_argument('--seed', default=None, type=int,
                        help='seed for initializing training. ')
    parser.add_argument('--gpu', default=None, type=int,
                        help='GPU id to use.')
    parser.add_argument('--image_size', default=224, type=int,
                        help='image size')
    parser.add_argument('--multiprocessing-distributed', action='store_true',
                        help='Use multi-processing distributed training to launch '
                             'N processes per node, which has N GPUs. This is the '
                             'fastest way to use PyTorch for either single node or '
                             'multi node data parallel training')

    args = parser.parse_args()
    cmd = argparse_to_command(args)
    print ('command = ', cmd)

if __name__ == '__main__':
    test_argparse_to_command()

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


