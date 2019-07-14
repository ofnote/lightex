from kubernetes import client, config, utils
from ..namedconf import render_command, to_dict


def get_k8s_api ():
    config.load_kube_config()
    v1 = client.ApiClient()
    batchv1 = client.BatchV1Api(v1)
    return batchv1

def build_job (name, containers, volumes):
        # Pod Spec
    pod_spec = client.V1PodSpec(containers=containers, restart_policy="Never", volumes=volumes)
    pod_template_spec = client.V1PodTemplateSpec(spec=pod_spec)

    # Job Spec using the Pod Template spec
    job_spec = client.V1JobSpec(template=pod_template_spec)
    job_meta = client.V1ObjectMeta(name=name, namespace="default", labels={"app": "model-training"})
    job_body = client.V1Job(metadata=job_meta, spec=job_spec)
    return job_body

def create_volume(name, mount_path, host_path, storage_type):
    #print (f'{name}, {mount_path}, {host_path}')
    vmount = client.V1VolumeMount(name=name, mount_path=mount_path)
    host_path_src = client.V1HostPathVolumeSource(path=host_path)
    volume = client.V1Volume(name=name, host_path=host_path_src)
    return vmount, volume

def create_env (expt):
    er, run = expt.er, expt.run
    env = er.get_env(run)
    env = [client.V1EnvVar(name=name, value=value) for name, value in env]
    return env

def create_job (expt, batchv1):
    er = expt.er
    bu, ctr = er.build, er.ctr
    run = expt.run

    mount_tuples = er.get_volume_mounts()
    volume_mounts, volumes = [], []
    for m in mount_tuples:
        mnt, vol = create_volume(**to_dict(m))
        volume_mounts.append(mnt)
        volumes.append(vol)

    python_command = [render_command(expt)]
    resources = client.V1ResourceRequirements(requests={"cpu": run.max_cpu, "memory": run.max_memory})
    env = create_env(expt)

    test_container = client.V1Container(name="conda", 
                                        image=bu.image_url, image_pull_policy=bu.image_pull_policy, 
                                        command=["/bin/bash", "-c", "--"], args=python_command, 
                                        volume_mounts=volume_mounts, 
                                        working_dir=ctr.working_dir, 
                                        resources=resources,
                                        env=env)
    containers = [test_container]

    print (f'building job with name {run.run_name}')
    job_body = build_job(name=f'{run.run_name}', 
                                containers=containers, volumes=volumes)

    # Create job in namespace "default"
    batchv1.create_namespaced_job("default", job_body)



def dispatch_expts_k8s (expts):
    batchv1 = get_k8s_api()

    for expt in expts:
        create_job(expt, batchv1)

    print_job_stats(batchv1)


    
def print_job_stats(k8s_batch):
    # Print the status of Jobs in the default namespace
    for job in k8s_batch.list_namespaced_job("default").items:
        print ("Job: ", job.metadata.name, "Status: ", job.status)



'''
def create_mlflow_experiment(expt_name):
    config.load_kube_config()
    v1 = client.ApiClient()
    batchv1 = client.BatchV1Api(v1)
    python_command = ["python /opt/bin/create_mlflow_experiment.py --name {}".format(expt_name)]
    # TODO: hardcoding the create experiment docker image for now. Change to mlflow params
    test_container = client.V1Container(name="mlflow", image="localhost:32000/create_experiment", image_pull_policy="Always", 
                                        command=["/bin/bash", "-c", "--"], args=python_command)
    containers = [test_container]
    pod_spec = client.V1PodSpec(containers=containers, restart_policy="Never")
    pod_template_spec = client.V1PodTemplateSpec(spec=pod_spec)
    job_spec = client.V1JobSpec(template=pod_template_spec, ttl_seconds_after_finished=60)
    job_meta = client.V1ObjectMeta(name="create-experiment", namespace="default", labels={"app": "mflow"})
    job_body = client.V1Job(metadata=job_meta, spec=job_spec)

    # Create job in namespace "default"
    batchv1.create_namespaced_job(
        "default",
        job_body
    )
'''

if __name__ == "__main__":
    config.load_kube_config(config_file='~/.kube/config')
    v1 = client.ApiClient()
    batchv1 = client.BatchV1Api(v1)
    #create_mlflow_experiment("test2")


