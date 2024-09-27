# ------------------------
# author: lvdpoel
# edited by: arietma, edited from: calc_spat_temp_data_in_fp.R

# This function calculates the linearly interpolated ndvi / evi values in a 
# footprint, and returns those as the weighted average value
#
# Input: 
#       fp:     footprint raster file, 
#       ndvi:   the ndvi/evi raster that is closest in time to the measurement, 
#       ndvi2:  the ndvi/evi raster that is second closest in time to the  
#               measurement (used in interpolation), 
#       daydiff:the difference in days between the ndvi/evi raster 'ndvi' and the 
#               measurement, 
#       daydiff2:the difference in days between the ndvi/evi raster 'ndvi2' and the 
#               measurement
#
# Output: ndvi_in_fp: raster of ndvi/evi 'ndvi' values in footprint,  fp: raster 
# of footprint, same shape as ndvi, ndvi_contr: contribution of ndvi/evi to footprint,
# which is linearly interpolated
#
# Requires library(terra) and library(pracma)

# Edits by arietma:
# Changed the script calc_spat_temp_data_in_fp.R to add linear interpolation, 
# so the addition of ndvi2, daydiff, daydiff2 as inputs, and the linear interpolation
# at the end of the script
# --------------------------

calc_ndvi_in_fp <- function(fp, ndvi, ndvi2, daydiff, daydiff2){
  
  fp <- terra::project(fp, crs(ndvi))
  fp[is.na(fp)] <- 0
  fp[fp<0] <- 0
  
  # crop modis file to fp file
  ndvi <- crop(ndvi,fp, snap='out')
  
  # make ndvi into vector of locations
  ndvi_locs <- as.polygons(ndvi, values = T, dissolve = F) 
  
  # sum fp values for those locations            
  fp_cellsize <- 35.92811
  ndvi_locs[["fp_value"]] <- extract(fp, ndvi_locs, fun= function(x) sum(x,na.rm=T))[[2]]*fp_cellsize/prod(res(ndvi))
  
  # footprint values in same raster shape as ndvi
  fp.ndvi_locs <- rasterize(ndvi_locs, ndvi, field="fp_value")
  fp.final <- fp.ndvi_locs * prod(res(fp.ndvi_locs))
  fp.final[fp.final < 0.01] <- 0 
  
  # calc ndvi per fp contribution
  ndvi_fp <- fp.final * ndvi
  ndvi_contr <- sum(as.data.frame(ndvi_fp)) /sum(as.data.frame(fp.final)) 
  
  # Repeat for ndvi2, which lies second closest to the date of the footprint
  # The same fp.final can be used as this is a raster of the fp in the shape of the ndvi
  ndvi2 <- crop(ndvi2, fp, snap='out')
  
  ndvi2_fp <- fp.final * ndvi2
  ndvi2_contr <- sum(as.data.frame(ndvi2_fp)) / sum(as.data.frame(fp.final))
  
  # Linear interpolation to find ndvi between closest and second closest date (on day = 0)
  # if else statement: if one of the calculated ndvi's is NA, ndvi_interp is NA as well
  if (is.na(ndvi_contr) | is.na(ndvi2_contr)) {
    ndvi_interp <- NA
  } else {
    ndvi_interp <- interp1(x = c(daydiff, daydiff2), y = c(ndvi_contr, ndvi2_contr), xi = 0, method = 'linear')
    # Warning 'Points in argument in 'x' unsorted' can be ignored, this is only
    # necessary for method = 'nearest'
  }
  
  return(list(ndvi_in_fp=ndvi_fp,fp=fp.final, ndvi_contr=ndvi_interp))}



