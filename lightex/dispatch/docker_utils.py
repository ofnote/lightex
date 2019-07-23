from dataclasses import asdict
import docker
from .config_containers import DockerConfig
from ..namedconf import render_command, to_dict

def run_container (config, client=docker.from_env()):
    print (f'starting container: {config.name}')
    container = client.containers.run(**config.to_dict())
    return container

def show_logs (name, client=docker.from_env()):
    container = client.containers.get(name)
    for line in container.logs(stream=True):
        print (line.strip())

def create_mounts(mount_list): # TODO: expand this for other storage_type's
    res = []
    for m in mount_list:
        mnt = docker.types.Mount(type='bind', source=m.host_path+'/', target=m.mount_path)
        res.append(mnt)
    return res

def create_env (expt):
    er, run = expt.er, expt.run
    env = er.get_env(run)
    env = {name: value for name, value in env}
    return env

def create_job(expt, log_to_file=True):
    er = expt.er
    ctr = er.ctr
    run = expt.run

    run_cmd = f'mkdir -p {run.output_dir} && {render_command(expt)}'
    command = ['sh', '-c', f'\"{run_cmd}\"']

    mount_list = er.get_volume_mounts() #[{name, mount_path, host_path}]
    mounts = create_mounts(mount_list)
    #print (f'mounts: {mounts}')
    env = create_env(expt)
    network = run.get_network()


    D = DockerConfig(
            image=ctr.build.image_url,
            name=run.run_name,
            command=command,
            working_dir=ctr.working_dir,
            mounts=mounts,
            resources={'mem_limit': run.max_memory},
            auto_remove=(not run.persist),
            environment=env,
            network=network
        )
    #print (D.to_dict())
    
    container = run_container(D)

    if log_to_file:
        storage_out_dir = expt.er.storage.output_dir
        run_output_log_file = f'{storage_out_dir}/{run.run_name}.log'
        print (f'Logging output to {run_output_log_file}')

        with open(run_output_log_file, 'wb') as fp:
            for line in container.logs(stream=True):
                #print(line)
                fp.write(line)

    return container

def dispatch_expts_docker (expts):
    for expt in expts:
        create_job (expt)

def test():
    D_mlflow = DockerConfig(
            image="localhost:32000/mlflow-server", 
            name="mlflow-server",
            ports={5000: 5000},
            #volumes={"/tmp/mlflow-data": {'bind': '/mlflow-data', 'mode': 'rw'}},
            mounts=[create_mounts([{'host_path': '/tmp/mlflow-data', 'mount_path': '/mlflow-data'}])],
            command=[ "mlflow server", 
                "--backend-store-uri /mlflow-data --host 0.0.0.0", 
                 "--default-artifact-root /mlflow-data"]
         )

    #print (asdict(D_mlflow))
    container = run_container(D_mlflow)
    show_logs (container.name)

if __name__ == '__main__':
    test()
    