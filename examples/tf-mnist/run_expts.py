import sys
sys.path.append('../..')

from lightex.namedconf import load_config
from lightex import dispatch_expts
import argparse



def main(args):
    C = load_config(config_dir='.', config_name=args.config_name)
    expts = C.get_experiments()
    
    dispatch_expts(expts, engine=args.engine, dry_run=args.d)


#LEX_EXPERIMENT_NAME='out1' MLFLOW_TRACKING_URI='http://localhost:30005' 
#python train.py --data-dir . --alpha 0.05 --l1_ratio 0.01

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Experiments Runner')
    parser.add_argument('-d', '--dry-run', dest="d", action='store_true',
                        help="Print the rendered command that will be run")

    parser.add_argument('-c', '--config-name', type=str, required=True)
    parser.add_argument('-e', '--engine', type=str, default="process")

    args = parser.parse_args()
    main(args)