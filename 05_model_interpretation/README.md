# Model interpretation

In the ```shap_analysis``` script, the SHAP package is used to calculate Shapley values of features in the final merged model. The script includes plotting options, and linear regression is calculated on the Shapley values explaining Air Exposed Peat Depth < 45 cm.

The ```shap_analysis_SepJan_FebAug``` script calculates the Shapley values of the features in the seasonal models - SepJan and FebAug models. Similar to the previous script, plotting options are provided.

Both ```shap_analysis``` and ```shap_analysis_SepJan_FebAug``` need to be run first before running ```shap_figures_modelcomp```. This script generates Shapley plots for all three models, allowing for model comparison.

Additionally, ```shap_analysis``` must be run before ```shap_analysis_bootstrap```. The ```shap_analysis_bootstrap``` calculates the uncertainty (bootstrap intervals) around the Shapley values for Air Exposed Peat Depth. It also computes the ‘zero crossings’ of Air Exposed Peat Depth and surface T, which refer to the feature value at which Shapley = 0 is crossed.

### Subfolder: ```simulations```
In the simulations folder, the simulation scripts are stored. 

The simulations that include PAR and Tsfc use the ```create_df``` function from ```prepare_data_for_simulations```. This function creates sub-dataframes based on several combinations of PAR and Tsfc, with Air Exposed Peat Depth ranging from 0 to 125 cm. 

The ```sim_bootstrap``` script then performs the CO<sub>2</sub> predictions using bootstrapped sampling of the merged dataset. This is done to display the bootstrap intervals around the simulations in ```sim_boot_make_bigplot```.

The ```sim_boot_make_bigplot``` script produces a figure showing the simulation results for every combination of PAR and Tsfc.

These scripts, with the addition of ```_EVI```, perform the same tasks for the simulations that include PAR and EVI. 
