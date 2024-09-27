#------------------------------
# author: lvdpoel
# edited by: arietma, edited from: ffp_analysis.R

# This script calculates the footprints using Kljun footprint climatology functions.
#
# Input: tower measurements file, prepared using prepare_tower_data.R (.csv), and
# functions by Kljun et al. (2015) (.R)
# Output: for every tower measurement, a raster file with the contribution of 
# every m-2 to the flux (.nc)

# Edits by arietma:
# - Adjusted the code to the (tower) dataset and paths used in the current thesis
# - Adjusted variable 'domain' to 300, more relevant for tower measurements

#------------------------------

## Cleanup
rm(list = ls(all.names = TRUE))

## Libs
library(tidyverse)  
library(sp)
library(raster, exclude = 'select')
library(sf)  
library(ggplot2)
library(fields)
library(rgdal)
library(directlabels)
library(metR)
library(ncdf4)
library(dplyr)
library(stringr)
library(EBImage)

# Set working directory
setwd('C:/Users/ariet/Documents/Climate Studies/WSG Thesis')

# Load Kljun functions
sapply(list.files(path = "C:/Users/ariet/Documents/Climate Studies/WSG Thesis/Script/Edited_script_Laura/01_footprint modelling/functions_kljun", full.names = T), source)

# Load tower dataset data
filepath = "C:/Users/ariet/Documents/Climate Studies/WSG Thesis/data/tower/tower_0607.csv"
df <- read.csv(filepath, na='NA') %>% data.frame() 

#### Calculate fp's####
r <- seq(20, 80, 20) # contour percentages
domain <- c(-300, 300, -300, 300)



#### Run functions
fp_values_all <- list()
start <- Sys.time()



for (i in 1:nrow(df)){
  row <- slice(df, i) 
  
  
  # use Kljun's footprint function
  ffp_clim <- calc_footprint_FFP_climatology(zm = row$zm, z0 = NaN, umean = row$umean,
                                             h = row$h, ol = row$ol, sigmav = row$sigmav,
                                             ustar = row$ustar, wind_dir = row$wind_dir, 
                                             rslayer = 1, crop=0, r=r, fig=0, domain = domain)
  
  print(paste0('step ',i, '/', nrow(df)))
  
  # get contribution values and put them in raster
  fp_values <- ffp_clim$fclim_2d
  raster_m <- raster::raster(t(fp_values[,ncol(fp_values):1]),
                             xmn = domain[1],
                             xmx = domain[2],
                             ymn = domain[3],
                             ymx = domain[4],
                             crs = 28992)
  
  # Get measurement coordinates: lat lon point --> xy point (in rijksdriehoek coördinaten):
  lonlat <- c(df[i,]$Lon, df[i,]$Lat)
  lonlat_sf <- st_point(lonlat) %>% st_sfc(crs=4326)
  xy <- st_transform(lonlat_sf , crs=28992) %>% st_coordinates()
  
  # Shift raster so (0,0) becomes measurement x,y (rijksdriehoek coördinaten)
  raster_rd = shift(raster_m, dx=xy[1], dy=xy[2])
  
  # Reproject raster to have lat-lon
  raster_latlon = projectRaster(raster_rd, crs = 4326)
  
  #save raster as .nc file
  outfile <- paste0("C:/Users/ariet/Documents/Climate Studies/WSG Thesis/data/preprocessing/tower/ffp_output/fp_rasters_0607/",i,".nc")
  writeRaster(raster_latlon, outfile, overwrite=TRUE, format="CDF", varname="fp_value", varunit="-", 
              longname="test variable -- raster layer to netCDF", xname="lon", yname="lat")
  
}

end <- Sys.time()

print(end-start)
