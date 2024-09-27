#------------
# author: lvdpoel
# edited by: arietma

# This script reads the downloaded modis files and stores them together in a 
# stacked raster # (.tiff extension), with the correct year + day of year as name.
# 
# Input: folder with all downloaded modis files (.hdf)
# Output: one file with all NDVI values (NDVI_all.tiff) and one file with all EVI
# values (EVI_all.tiff)

# Edits by arietma:
# Added loading and storing of EVI files
-------------------

  
## Cleanup
rm(list = ls(all.names = TRUE))

## Set working directory
setwd("C:/Users/ariet/Documents/Climate Studies/WSG Thesis/data/preprocessing/modis_0531")


## Libs
library(terra)
library(MODISTools)
library(MODIStsp)

folder <- "C:/Users/ariet/Documents/Climate Studies/WSG Thesis/data/preprocessing/modis_0531"
files <- list.files(folder, pattern= '.hdf')

####for NDVI####
start = Sys.time()

# empty raster
NDVI_all <- rast()
i=1
for(i in 1:length(files)){
  file <- files[i]
  
  # first layer is NDVI
  NDVI <- sds(file)[1]
  
  # add year + doy as name
  names(NDVI) <- substring(file, 10, 16) 
  
  # reproject to have lat lon
  NDVI_latlon <- project(NDVI, 'epsg:4326', method = 'near', mask=FALSE, align=FALSE, gdal=TRUE) # takes 12 seconds
  
  # NOT WORKING for first file:
  values(NDVI_latlon) <- values(NDVI_latlon) / 10^8 # to make them between 0 and 1. 
  
  
  # add new NDVI map to collection of NDVI maps
  NDVI_all <- c(NDVI_all, NDVI_latlon) # warning can be ignored, first raster is intentionally empty
  print(paste0(i,' / ', length(files), ' done!'))
}
end = Sys.time()
end-start


# save it all
outpath <- "C:/Users/ariet/Documents/Climate Studies/WSG Thesis/data/preprocessing/modis_0531/"
writeRaster(NDVI_all, filename=paste0(outpath, 'NDVI_all.tiff'), overwrite=FALSE)

####for EVI####
start = Sys.time()

# empty raster
EVI_all <- rast()
i=1
for(i in 1:length(files)){
  file <- files[i]
  
  # second layer is EVI
  EVI <- sds(file)[2]
  
  # add year + doy as name
  names(EVI) <- substring(file, 10, 16) 
  
  # reproject to have lat lon
  EVI_latlon <- project(EVI, 'epsg:4326', method = 'near', mask=FALSE, align=FALSE, gdal=TRUE) # takes 12 seconds
  
  values(EVI_latlon) <- values(EVI_latlon) / 10^8 # to make them between 0 and 1. 
  
  
  # add new EVI map to collection of EVI maps
  EVI_all <- c(EVI_all, EVI_latlon) # warning can be ignored, first raster is intentionally empty
  print(paste0(i,' / ', length(files), ' done!'))
}
end = Sys.time()
end-start


# save it all
outpath <- "C:/Users/ariet/Documents/Climate Studies/WSG Thesis/data/preprocessing/modis_0531/"
writeRaster(EVI_all, filename=paste0(outpath, 'EVI_all.tiff'), overwrite=FALSE)
