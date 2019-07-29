from jinja2 import Environment, FileSystemLoader
from os import path
from pathlib import Path
from dataclasses import replace
import uuid

from ..namedconf import render_command
from .k8sutils import dispatch_expts_k8s
from .docker_utils import dispatch_expts_docker
from .process_utils import dispatch_expts_process, ProcessConfig


def setup_run(engine, expt, run_id, seq_id, log_in_output_dir=False, debug=False):
    #print ('setup_run', expt.er.storage)
    if engine == 'process':
        ltex_out_dir = expt.er.storage.output_dir
        run_data_dir = expt.er.storage.data_dir
    else:
        ltex_out_dir = expt.er.ctr.output_dir
        run_data_dir = expt.er.ctr.data_dir


    jobid = f'{run_id}-{seq_id}' # run group id, sequence id in group
    ename = expt.run.experiment_name
    run_output_dir = f'{ltex_out_dir}/{ename}/{jobid}'
    if log_in_output_dir:
        run_output_log_file = f'{run_output_dir}/{jobid}.log'
    else:
        run_output_log_file = f'{ltex_out_dir}/{ename}/{jobid}.log'
    run_name = f'{ename}-{jobid}'

    R = replace(expt.run, run_name=run_name, data_dir=run_data_dir, 
                output_dir=run_output_dir, output_log_file=run_output_log_file)
    expt = replace(expt, run=R)

    if debug:
        print (f'updated run config to {R}')

    return expt



def dispatch_expts (expts, engine, dry_run=False, debug=False):
    if dry_run:
        print ("The following command will be run for one of experiments")
        print (render_command(expts[0]))
        return

    run_id = str(uuid.uuid4())[:3]
    expts = [setup_run (engine, expt, run_id, seq_id, debug=debug) for seq_id, expt in enumerate(expts)]

    if engine == 'process':
        P = ProcessConfig(log_to_file=True, async_exec=True) #TODO: add this to run
        dispatch_expts_process(expts, P)
    elif engine == 'docker':
        dispatch_expts_docker(expts)
    elif engine == 'k8s':
        dispatch_expts_k8s(expts)
    else:
        raise NotImplementedError(f'Unsupported dispatch engine {engine}')



