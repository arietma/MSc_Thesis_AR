# Spatial preprocessing
First, the scripts in the subfolder ```preparation``` should be run. Then, the scripts in the current repository ```02_spatial_preprocessing```. These scripts use the functions in the subfolder ```functions_spatpreproc```. After this, the scripts in ```reclassify_and_clean_datasets``` finalize preprocessing of the data.

### Subfolder: ```preparation```
The ```read_modis``` script adds all downloaded MODIS files to one large .tiff file for NDVI values, and one for EVI values.

The ```structure_OWASIS_files``` script ensures that the OWASIS files are organized in the correct folders for running the scripts in ```02_spatial_preprocessing```.

### Subfolder: ```functions_spatpreproc```
These functions are used by the scripts in ```02_spatial_preprocessing```.

The function ```importMaps``` imports all maps with the spatial and spatiotemporal variables.

The functions ```find_ndvi_for_twr``` and ```find_ndvi_for_air``` identify the closest and second to closest MODIS files relative to each tower and airborne measurement.

The functions ```find_OWASIS_for_twr``` and ```find_OWASIS_for_air``` identify the closest OWASIS file in time for each tower and airborne measurement.

```calc_ndvi_in_fp``` calculates the linearly interpolated weighted average of NDVI or EVI in the footprint, and ```calc_spat_temp_data_in_fp``` calculates the weighted average of the OWASIS variables in the footprint.

```calc_ruimt_data_in_fp``` calculate the values for all spatial variables in the footprint, for the land use classes, soil classes, peat depth and ahn (DEM) variables.

### Scripts in the current repository ```02_spatial_preprocessing```
First, ```fp_twr_spattemp_hpc``` and ```fp_air_spattemp_hpc``` should be run, which calculate the weighted averages of the NDVI/EVI and OWASIS variables in the tower and airborne footprints. Note that these scripts are written to be run in a HPC cluster. 

After running these scripts, ```datasets_sortrows``` should be run to verify if all rows are calculated, and to sort the rows of the datasets.

These sorted datasets are the input data for ```fp_twr_ruimtdata_hpc``` and ```fp_air_ruimtdata_hpc```. These two scripts calculate the contribution of land use and soil classes to the tower and airborne footprints, and the weighted averages of peat depth and ahn. 

Again, after running these scripts, ```datasets_sortrows``` should be run to sort the rows.

### Subfolder: ```reclassify_and_clean_datasets```
First, the ```reclassify_LGN``` script reclassifies the land use classes.

Next, the ```relcassify_soil``` script reclassifies the soil classes. After running these scripts, the datasets are preprocessed and reclassified. 

In the following scripts, the datasets are cleaned. ```clean_tower_data``` and ```clean_airborne_data``` clean the respective datasets. 

```merge_airborne_tower``` merges the final tower and airborne datasets into one merged dataset, ensuring a correct datetime format, and also creating two subsets of the merged dataset: SepJan and FebAug, with SepJan containing all observations from September - January and FebAug all observations from February - August.
