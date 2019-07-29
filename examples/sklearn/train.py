# The data set used in this example is from http://archive.ics.uci.edu/ml/datasets/Wine+Quality
# P. Cortez, A. Cerdeira, F. Almeida, T. Matos and J. Reis.
# Modeling wine preferences by data mining from physicochemical properties. In Decision Support Systems, Elsevier, 47(4):547-553, 2009.

# Obtained from mlflow repository

import os
import argparse
import warnings

import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.linear_model import ElasticNet
import joblib


def eval_metrics(actual, pred):
    rmse = np.sqrt(mean_squared_error(actual, pred))
    mae = mean_absolute_error(actual, pred)
    r2 = r2_score(actual, pred)
    return rmse, mae, r2

def do_train(alpha, l1_ratio, train_x, train_y, test_x, test_y):
    en = ElasticNet(alpha=alpha, l1_ratio=l1_ratio, random_state=42)
    en.fit(train_x, train_y)

    predicted_qualities = en.predict(test_x)

    rmse, mae, r2 = eval_metrics(test_y, predicted_qualities)

    print("Elasticnet model (alpha=%f, l1_ratio=%f):" % (alpha, l1_ratio))
    print("  RMSE: %s" % rmse)
    print("  MAE: %s" % mae)
    print("  R2: %s" % r2)

    return rmse, mae, r2, en

def mlflow_run (alpha, l1_ratio, train_x, train_y, test_x, test_y):
    from lightex.mulogger import MLFlowLogger, MultiLogger

    logger = MLFlowLogger('sk')

    mlflow = logger.mlflow
    print (f'tracking: {mlflow.tracking.get_tracking_uri()}')


    with mlflow.start_run():
        rmse, mae, r2, en = do_train(alpha, l1_ratio, train_x, train_y, test_x, test_y)

        mlflow.log_param("alpha", alpha)
        mlflow.log_param("l1_ratio", l1_ratio)
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("r2", r2)
        mlflow.log_metric("mae", mae)
        print (mlflow.get_artifact_uri())
        #mlflow.sklearn.log_model(en, "model")

def logger_run (alpha, l1_ratio, train_x, train_y, test_x, test_y, output_dir):
    from lightex.mulogger import MultiLogger

    logger = MultiLogger()

    logger.start_run()
    rmse, mae, r2, en = do_train(alpha, l1_ratio, train_x, train_y, test_x, test_y)

    logger.log('*', ltype='hpdict', value={'alpha': alpha, 'l1_ratio': l1_ratio})
    logger.log('*', ltype='scalardict', value={'mae': mae, 'rmse': rmse, 'r2': r2}, step=1)
    #logger.log('*', ltype='scalardict', value={'mae': mae, 'rmse': rmse, 'r2': r2+1}, step=2)

    joblib.dump(en, f'{output_dir}/model.joblib')
    logger.end_run()

if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    np.random.seed(40)

    parser = argparse.ArgumentParser()
    parser.add_argument('--data-dir', type=str, required=True)
    parser.add_argument('--output-dir', type=str, required=True)
    parser.add_argument('--alpha', required=True)
    parser.add_argument('--l1_ratio', required=True)

    args = parser.parse_args()

    # Read the wine-quality csv file (make sure you're running this from the root of MLflow!)
    wine_path = os.path.join(args.data_dir, "wine-quality.csv")
    data = pd.read_csv(wine_path)

    # Split the data into training and test sets. (0.75, 0.25) split.
    train, test = train_test_split(data)

    # The predicted column is "quality" which is a scalar from [3, 9]
    train_x = train.drop(["quality"], axis=1)
    test_x = test.drop(["quality"], axis=1)
    train_y = train[["quality"]]
    test_y = test[["quality"]]

    # alpha = float(args['alpha'])
    # l1_ratio = float(args['l1_ratio'])
    alpha = float(args.alpha)
    l1_ratio = float(args.l1_ratio)

    #do_train(alpha, l1_ratio, train_x, train_y, test_x, test_y)

    #mlflow_run (alpha, l1_ratio, train_x, train_y, test_x, test_y)
    logger_run (alpha, l1_ratio, train_x, train_y, test_x, test_y, args.output_dir)

        

