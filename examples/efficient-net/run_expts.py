import sys
sys.path.append('../..')

from lightex.namedconf import load_config
from lightex import dispatch_expts
import argparse


def main(args):
    C = load_config(config_dir='.', config_name=args.config_name, update_args=args)

    #print (C.er.build)
    expts = C.get_experiments()
    dispatch_expts(expts, engine=args.engine, dry_run=args.d)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Batch scheduler')
    parser.add_argument('-d', '--dry-run', dest="d", action='store_true',
                        help="Print the rendered command that will be run")

    parser.add_argument('-c', '--config-name', type=str, required=True)
    parser.add_argument('-e', '--engine', type=str, default="process")

    # optional updates
    parser.add_argument('--image-pull-policy', type=str, choices=['Always', 'IfNotPresent'], 
                dest='er.build.image_pull_policy')

    args = parser.parse_args()
    main(args)