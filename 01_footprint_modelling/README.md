# Footprint modelling
First, the ```loading_tower_data_calc_Tsfc``` script loads the raw tower data, calculates surface temperature and stores the tower site datasets to one large dataset containing all sites.

```prepare_tower_data``` and ```prepare_airborne_data``` prepare the tower and airborne datasets for using the functions by Kljun et al. (2015), by renaming columns and calculating the required variables.

```ffp_airborne``` and ```ffp_tower``` produce footprints for every observation for the airborne and tower dataset respectively. The footprints are stored as .nc files.

### Subfolder: ```functions_kljun```
The functions made by Kljun et al. (2015) ```calc_footprint_FFP``` and ```calc_footprint_FFP_climatology```, which are used in the ```ffp_airborne``` and ```ffp_tower``` scripts in the repository ```01_footprint_modelling```.

### Reference
Kljun, N., Calanca, P., Rotach, M. W., & Schmid, H. P. (2015). A simple two-dimensional parameterisation for Flux Footprint Prediction (FFP). *Geosci.* Model Dev., *8*(11), 3695- 3713. https://doi.org/10.5194/gmd-8-3695-2015
