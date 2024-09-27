#------------
# author: lvdpoel
# edited by: arietma, edited from: prepare_grhart_file.R
# 
# This script prepares the tower dataset so it can be used with Kljun functions. 
# Column names are changed,  planetary boundary layer height is calculated,
# some filters are applied to avoid errors in Kljun functions
# 
# Input: raw tower measurements file (.csv)
# Output: tower measurement file, ready to use with Kljun (.csv)

# Edits by: arietma
# - Adjusted the script to the dataset used in the current thesis
# - Added calculation of sigmav
# - Added two filters for avoiding errors in Kljun functions: 
# -     filter(ustar>=0.1) and filter(umean>0)

#------------


## Cleanup
rm(list = ls(all.names = TRUE))

library(tidyverse)

# working directory
setwd('C:/Users/ariet/Documents/Climate Studies/WSG Thesis/data/tower')
# Get data
file_in = 'C:/Users/ariet/Documents/Climate Studies/WSG Thesis/data/tower/tower_allcolumns_0607.csv'
dataColnames <- read.csv(file_in, skip = 0,nrows = 1) # needs to be checked for new files
data <- read.csv(file_in, skip = 0) %>% data.frame() # same here
colnames(data)<-colnames(dataColnames)
df <- data.frame(data) 

## Rename columns
# Give correct column names for Kljun script
df <- df %>% 
  rename(
    zm = sonic_height,
    umean = WINS,
    ol = L, # Monin Obukhov
    ustar = Ustar, # friction velocity, sheer stress of the air on surface roughness / mechanic instability
    wind_dir = WIND # wind direction relative to the north
  )

## Calculate new variables

# Calculate sigmav
# standard deviation of lateral velocity fluctuations [ms-1] should be used
df['sigmav']=sqrt(df['v_var'])


# Calculation planetary boundary layer height (PBLH) (h in calc_footprint_FFP_climatology)
latitude = data$Lat * (pi / 180)        # degrees -> radians
angular_velocity = 7.2921159 * 10^-5     # rad/s
coriolis_parameter = 2 * angular_velocity * sin(latitude)
c_n = 0.3  
PBLH = c_n * df$ustar / coriolis_parameter
df['h'] <- PBLH

# drop some columns
df <- subset(df, select = -c(PA_NOBV1, PA_NOBV2, PA_NOBV3,
                             PA_NOBV4, RAIN_NOBV1, RAIN_NOBV2, RAIN_NOBV3,
                             RAIN_NOBV4, WINS_NOBV1, WINS_NOBV2, WINS_NOBV3,
                             WINS_NOBV4, WIND_NOBV1, WIND_NOBV3, WIND_NOBV4,
                             SHF1_NOBV1, SHF1_NOBV2, VPD_NOBV1, VPD_NOBV2,
                             VPD_KNMI, WIND_f, Tair_f, PA_f, RH_f, RAIN_f, 
                             SWIN_f, LWIN_f, PAR_f, VPD_f, NEE_H, NEE_LE, 
                             Tdew_EP, Tdew_KNMI, canopy_height, F_CH4, ch4_var,
                             NEE_CH4, NEE_H2O, H2O_var,  WINS_EP, w_var, Tau,
                             TKE, NIR, RNIR, bowen_ratio, RH_EP, VPD_EP, PA, PA_EP, 
                             Tair_EP, ts_var, Tstar, SHF1, SHF2, Tsoil_1_005,
                             Tsoil_1_015, Tsoil_1_025, Tsoil_1_035, Tsoil_1_045,
                             Tsoil_1_055, Tsoil_1_065, Tsoil_1_075, Tsoil_1_085, 
                             Tsoil_1_095, Tsoil_1_105))

# Omit na's of required variables for the ffp_clim function, and of NEE_CO2
vars_required <- c('NEE_CO2','h','sigmav','zm','umean','ol','ustar','wind_dir')
summary(df[,vars_required])

for (var in vars_required){
  rws <- !is.na(df[[var]])
  df <- df[rws,]
} 

# Apply filters to prevent errors in ffp_clim function
df <- df %>% filter(zm > 0)  %>% filter(zm<h) %>% filter(zm/ol >= -15.5) %>% filter(ustar>=0.1) %>% filter(umean>0)

# Save to csv
file_out = 'C:/Users/ariet/Documents/Climate Studies/WSG Thesis/data/tower/tower_0607.csv'
write.csv(df, file_out, row.names = FALSE)
