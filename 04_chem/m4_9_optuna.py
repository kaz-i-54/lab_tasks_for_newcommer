import pandas as pd
import optuna
import lightgbm as lgb
from sklearn.model_selection import KFold, cross_val_predict, train_test_split
from functools import partial
from sklearn.model_selection import cross_val_predict

import sys
sys.path.append("./m4_6")
from regression import calc_rmse, prepare_dataset, calc_score


def objective(X, y, trial):

    # paramter_tuning using optuna
    bagging_freq = trial.suggest_int('bagging_freq', 1, 10),
    min_data_in_leaf = trial.suggest_int('min_data_in_leaf', 2, 100),
    max_depth = trial.suggest_int('max_depth', 1, 75),
    learning_rate = trial.suggest_loguniform('learning_rate', 0.001, 0.1),
    num_leaves = trial.suggest_int('num_leaves', 2, 1000),
    num_threads = trial.suggest_int('num_threads', 1, 10),
    min_sum_hessian_in_leaf = trial.suggest_int('min_sum_hessian_in_leaf', 1, 10),


    params = {
        "random_state": 42,
        "n_estimators": 10000,
        "bagging_freq": bagging_freq,
        "min_data_in_leaf": min_data_in_leaf,
        "max_depth": max_depth,
        "learning_rate": learning_rate,
        "num_leaves": num_leaves,
        # "num_threads": num_threads,
        "min_sum_hessian_in_leaf": min_sum_hessian_in_leaf,
        # "min_child_weight": min_child_weight,
        # "subsample": subsample,
        # "colsample_bytree": colsample_bytree,
    }
    model_opt = lgb.LGBMRegressor(**params)
    y_pred = cross_val_predict(model_opt, X, y, cv=4)
    return calc_rmse(y, y_pred)


if __name__ == '__main__':
    X, Y = prepare_dataset("data/pca_all_X.csv", "data/fukunishi_data.csv")
    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=2)
    study_rmse = optuna.create_study(direction='minimize')
    f = partial(objective, X_train, y_train)
    study_rmse.optimize(f, n_trials=10)
    print(study_rmse.best_params)

    # trial = study_rmse.best_trial

    f_model = lgb.LGBMRegressor(**study_rmse.best_params)
    f_model.fit(X_train, y_train)
    y_pred = f_model.predict(X_test)
    print(calc_score(y_test, y_pred))



"""
[0.49344532 0.55547484 0.55928286 0.57528997]
[0.78576624 0.78000558 0.7615122  0.73958869]
mean rmse: 0.54587
mean r2: 0.76672
"""