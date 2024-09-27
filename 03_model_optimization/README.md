# Model optimization
The model optimization first involves feature selection, and next, the hyperparameters of the XGBoost model are optimized.

An initial feature selection is made using ```corr_matrix```, ```corr_pearson```, and ```xgboost_feature_importance```. After this, Sequential Backward Floating Selection (SBFS) is the feature selection algorithm that is used.

```corr_matrix``` computes the Pearson correlation coefficient between all features, so correlated features can be avoided.

```corr_pearson``` calculates the Pearson correlation coefficient of all features with the CO<sub>2</sub> flux, so that the least correlating features do not move on to SBFS.

```xgboost_feature_importance``` calculates the feature importances embedded in XGboost, and the least important features do not move on to SBFS.

Next, SBFS is performed in ```sbfs_hpc``` in different iterations, each iteration including a different groundwater-related variable. ```sbfs_hpc``` also calculates the model metrics for every subset of features. 

These model metrics are analyzed in ```analyze_metrics_sbfs```. Based on this script, the number of features to be included in the final merged model is selected.

Based on the final feature selection, a manual feature selection is made for the two seasonal models, SepJan and FebAug. The model metrics are calculated in ```calc_metrics_SepJan_FebAug```, to help select the data fold that is used as a test set.

Lastly, the hyperparameters are tuned in ```hyperparam_tuning_hpc``` for the merged model and ```hyperparam_tuning_SepJan_FebAug_hpc``` for the seasonal models, both using GridSearchCV.
