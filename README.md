# MSc_Thesis_AR
Scripts of MSc Thesis by Anne Rietman: Understanding drivers behind CO<sub>2</sub> fluxes from fen meadows in Fryslân - Using Boosted Regression Trees to model Net Ecosystem Exchange from Dutch peatlands

Master Thesis Water Systems and Global Change Group in partial fulfillment of the degree of Master of Science in Climate Studies at Wageningen University, the Netherlands. 

Supervisors: dr. R.W.A. Hutjes and dr. B. Kruijt

### Datasets and scripts

The airborne and tower datasets used in these scripts were provided by the WUR and NOBV, with the airborne dataset's version dated 01-05-2023, and the tower dataset's version dated 12-05-2023.

The methodology and scripts are largely based on the MSc Thesis by L. van der Poel, published in Hutjes et al. (2023). These scripts can be publicly found here: https://github.com/lvdpoel/MSc_thesis. In my scripts, I have clearly documented the modifications I made and specified the original author of each script. 

The scripts are structured in the following folders, with in every folder, a README.md file:

1. ```01_footprint_modelling```: For every airborne and tower measurement, footprints are calculated based on the footprint model by Kljun et al. (2015). A footprint is the area where the CO<sub>2</sub> flux originates from.

2. ```02_spatial_preprocessing```: Each footprint is superimposed on each spatial map, and the values of the spatial variables corresponding to each footprint are calculated. Next, the airborne and tower datasets are cleaned and merged into the merged dataset. Two seasonal subsets of the merged dataset are also created, with SepJan including all observations from September to January, and FebAug all observations from FebAug. Note that all scripts ending with ```_hpc``` are run in a HPC cluster.

3. ```03_model_optimization```:  Feature selection and hyperparameter optimization are performed to optimize the merged model. The feature selection of the merged model guided the manual feature selection of the seasonal models, and hyperparameter optimization is performed for the seasonal models. Note that all scripts ending with ```_hpc``` are run in a HPC cluster.

4. ```04_model_evaluation```: The model metrics of the merged, SepJan and FebAug models are calculated.

5. ```05_model_interpretation```: The merged, SepJan and FebAug models are interpreted by Shapley analysis, and the merged model is additionally interpreted using two simulation series.

### Abstract
The artificially drained Dutch fen meadows account for a considerable share of the country’s CO<sub>2</sub> emissions. This study aimed to increase understanding of the drivers behind CO<sub>2</sub> emissions from fen meadows in one of the main Dutch peat areas, Fryslân, with a focus on the relationship between groundwater and CO<sub>2</sub> fluxes. Furthermore, the seasonality of this relationship and a recommended groundwater table depth were investigated. A Boosted Regression Tree was built with Net Ecosystem Exchange (NEE<sub>CO2</sub>) as a response variable, combining Eddy Covariance (EC) flux measurements from towers and an environmental research aircraft. The potential features included in this study were land use classes, soil classes, vegetation indices, meteorological variables and groundwater-table related variables. The model was optimized with feature selection and hyperparameter tuning, which resulted in an R<sup>2</sup> of 0.77. Shapley values and simulation series were used to analyze the results. In this study, Air Exposed Peat Depth (Exp_PeatD) represented groundwater, and a linear relationship was found for Exp_PeatD < 45 cm and NEE<sub>CO2</sub>. This corresponds to 4.22 tCO<sub>2</sub> ha<sup>-1</sup> yr<sup>-1</sup> emissions per 10 cm increased drainage, which lies within the range of current scientific estimates. Increasing drainage deeper than 60 cm was associated with saturation in emissions. Furthermore, seasonal models based on subsets of the data showed no large differences in the relationship between Air Exposed Peat Depth and NEE<sub>CO2</sub>, implying that the relationship does not depend on the time of the year. Lastly, also considering literature on CH<sub>4</sub> emissions, an Air Exposed Peat Depth of 20 - 38 cm is recommended to minimize greenhouse gas emissions. 

### References
Kljun, N., Calanca, P., Rotach, M. W., & Schmid, H. P. (2015). A simple two-dimensional parameterisation for Flux Footprint  Prediction (FFP). *Geosci.* Model Dev., *8*(11), 3695- 3713. https://doi.org/10.5194/gmd-8-3695-2015

Hutjes, R., Franssen, W., van der Poel, L., Bataille, L., Kruijt, B., Berghuis, H., Biermann, J., & Jans, W. (2023). *Chapter 10 NOBV year report 2022: Airborne measurements of regional carbon dioxide exchange of Dutch fen meadows.* Nationaal Onderzoeksprogramma Broeikasgassen Veenweiden. https://www.nobveenweiden.nl/wp-content/uploads/2023/06/10.-Hutjes_Airborne_FINAL.pdf 
