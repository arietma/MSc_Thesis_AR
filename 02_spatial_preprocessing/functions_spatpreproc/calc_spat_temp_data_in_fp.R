# ------------------------
# author: lvdpoel
# edited by: arietma

# This function calculates the spatial temporal data values in a footprint, and 
# returns those in a raster format, and as the weighted average value. Use this
# script for calculating the contribution of the OWASIS variables to the footprint
#
# Spatial temporal data is not the same as 'ruimtelijke data veenweiden', because:
# 1. the resolution is coarser (250m)
# 2. there is a time component (daily for OWASIS)
# 3. there are no categorical variables, only continuous
#
# Input: fp: footprint raster file, spatdata: some spatial data raster (OWASIS)
#
# Output: spatdata_in_fp: raster of spatdata (OWASIS) values in footprint,  fp: 
# raster of footprint, spatdata_contr: contribution of spatdata (OWASIS) to footprint

# Requires library(terra)

# Edits by arietma:
# - None, other than removing ndvi from this introductory text. For evi/ndvi, 
# use calc_ndvi_fp.R instead. In this script the ndvi/evi values are linearly
# interpolated.
# --------------------------
calc_spatdata_in_fp <- function(fp, spatdata){
  
  fp <- terra::project(fp, crs(spatdata))
  fp[is.na(fp)] <- 0
  fp[fp<0] <- 0
  
  # crop owasis file to fp file
  spatdata <- crop(spatdata, fp, snap='out')
  
  # make spatdata into vector of locations
  spatdata_locs <- as.polygons(spatdata, values = T, dissolve = F)
  
  # sum fp values for those locations            
  fp_cellsize <- 35.92811
  spatdata_locs[["fp_value"]] <- terra::extract(fp, spatdata_locs, fun= function(x) sum(x,na.rm=T))[[2]]*fp_cellsize/ prod(res(spatdata))
  
  # footprint values in same raster shape as spatdata
  fp.spatdata_locs <- rasterize(spatdata_locs, spatdata, field="fp_value")
  fp.final <- fp.spatdata_locs * prod(res(fp.spatdata_locs))
  fp.final[fp.final < 0.01] <- 0
  
  # calc spatdata per fp contribution
  spatdata_fp <- fp.final * spatdata
  spatdata_contr <- sum(as.data.frame(spatdata_fp)) / sum(as.data.frame(fp.final)) # to make fp sum up to 100%
  
  return(list(spatdata_in_fp=spatdata_fp,fp=fp.final, spatdata_contr=spatdata_contr))}

