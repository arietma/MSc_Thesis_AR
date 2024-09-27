#------------
# author: lvdpoel
# edited by: arietma, edited from: prepare_grhart_file.R
# 
# This script prepares the airborne-measurements file so it can be used
# with Kljun functions. Column names are changed and planetary boundary layer
# height is added as a column.
# 
# Input: raw airborne measurements file (.csv)
# Output: airborne measurement file, ready to use with Kljun (.csv)

# Edits by: arietma       SPECIFY THIS
# - Adjusted the script to the dataset used in the current thesis
# - Added two filters for avoiding errors in Kljun functions: 
# -     filter(ustar>=0.1) and filter(umean>0)
# - Also deleted airborne observations from first flight, since an earlier 
# (unused) version of spatial preprocessing gave strange OWASIS values for this
# flight, and e.g. height was negative
#------------

## Cleanup
rm(list = ls(all.names = TRUE))

library(tidyverse)

# working directory
setwd('C:/Users/ariet/Documents/Climate Studies/WSG Thesis/data')

# Get data
file_in = 'C:/Users/ariet/Documents/Climate Studies/WSG Thesis/data/output_processFryslanAll2.csv'
dataColnames <- read.csv(file_in, skip = 0, nrows = 1) # needs to be checked for new files
data <- read.csv(file_in, skip = 0) %>% data.frame() # same here
colnames(data) <- colnames(dataColnames)
df <- data.frame(data) 

## Rename columns
df <- df %>% 
  rename(
    zm = Alt, # Small mistake here, note to next user: use 'Height' instead of Alt (better values until 500m)
    umean = WindSpd,
    ol = L, # Monin Obukhov
    ustar = Ustar, # friction velocity, sheer stress of the air on surface roughness / mechanic instability
    wind_dir = WindDir, # wind direction relative to the north
    sigmav = stdLatWind # standard deviation of lateral velocity fluctuations [ms-1]
  )

## Calculate new variables
# Calculation planetary boundary layer height (PBLH) (h in calc_footprint_FFP_climatology)
latitude = data$Lat * (pi / 180)        # degrees -> radians
angular_velocity = 7.2921159 * 10^-5     # rad/s
coriolis_parameter = 2 * angular_velocity * sin(latitude)
c_n = 0.3  
PBLH = c_n * df$ustar / coriolis_parameter
df['h'] <- PBLH


# Omit na's of required variables for the ffp_clim function, and of CO2flx
vars_required <- c('CO2flx','h','sigmav','zm','umean','ol','ustar','wind_dir')
summary(df[,vars_required])

for (var in vars_required){
  rws <- !is.na(df[[var]])
  df <- df[rws,]
} 

# Apply filters to prevent errors in ffp_clim function
df <- df %>% filter(zm > 0)  %>% filter(zm < h) %>% filter(zm / ol >= -15.5) %>% 
  filter(ustar >= 0.1) %>% filter(umean > 0)

# Lastly, already omit observations from the first flight
# This is done since an earlier (unused) version of spatial preprocessing led to
# strange OWASIS values
df <- df %>% filter(OWASIS_Grondwaterstand_1 < 999)



# Save to csv
file_out = 'C:/Users/ariet/Documents/Climate Studies/WSG Thesis/data/airborne_morecols_0907.csv'
write.csv(df, file_out, row.names = FALSE)

