from ..mulogger.config import LoggerConfig, MLFlowConfig
from dataclasses import dataclass
from easydict import EasyDict as ED
import pandas as pd

class MLflowQViz:
    def __init__(self, config=MLFlowConfig()):
        import mlflow
        self.mlflow = mlflow
        self.client = mlflow.tracking.MlflowClient(config.uri())
        #from mlflow.entities import RunInfo, RunStatus

    def show_run_data (self, data):
        print (f'params: {data.params}')
        print (f'metrics: {data.metrics}')

    def show_runs(self, runs, meta_fields=['status', 'start_time', 'end_time', 'run_id']):
        df = pd.DataFrame([{fn: getattr(run.info, fn) for fn in meta_fields} for run in runs], columns=meta_fields)
        val = df['end_time'] - df['start_time']
        df.insert(0, 'run_time', val)
        #print (df)

        for run in runs:
            run_id = run.info.run_id
            print (f'** run {run_id}')
            print (df[df['run_id'] == run_id])

            self.show_run_data(run.data)


    def get_all_runs(self):
        expts = self.client.list_experiments()
        expts = [(expt.experiment_id, expt.name) for expt in expts if expt.lifecycle_stage == 'active']

        exptid2runs = {}
        for eid, name in expts:
            runinfos = self.client.list_run_infos(eid)
            runs = [self.client.get_run(ri.run_id) for ri in runinfos]
            exptid2runs[eid] = ED({'name': name, 'runs': runs})

        return exptid2runs

    def show_expt_runs(self):
        exptid2runs = self.get_all_runs()
        for eid, val in exptid2runs.items():
            print (f'\n==== {val.name} =====>')
            self.show_runs(val.runs)


def show_all_runs(config=LoggerConfig(loggers=['mlflow'])):
    mq = MLflowQViz(config.mlflow)
    mq.show_expt_runs()

if __name__ == '__main__':
    show_all_runs()
    