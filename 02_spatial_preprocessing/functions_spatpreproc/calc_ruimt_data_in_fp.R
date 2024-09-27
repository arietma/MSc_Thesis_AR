#--------------------------------
# author: lvdpoel
# edited by: arietma
  
# Function to calculate contributions of 'ruimtelijke data veenweiden' maps. 
#
# Input: data: should be of type as provided by importMaps function, i.e. with 
# raster and for categorical data, classes.
# fpraster: raster of footprint to be calculated, cat: logical. If True: categorical data: function
# calculates contribution of every class. if False, for continuous data, function calculates average

# Output: dataframe with contributions, to be added to dataframe with measurements
  
# requires library(terra), library(stringr)
  
# Edits by arietma:
# - Omitted reclassification of LGN/Bodemkaart, as this is done at a later stage
# in reclassify_soil.py and reclassify_LGN.py since the data was available in a 
# different format. 
# - Based categorical contr. calculation on classes instead of legend. No legend
# was available, for this the maps had to be reclassified first
# - For AHN, no classes file was available (no dbf). As variable 'classes' is not
# used for the continuous contr. calculation, loading in the classes is moved to 
# cat = T.
#------------------------------------------

calc_ruimt_data_in_fp <- function(data=maps$LGN2020, fpraster=fp, cat=T){
  
  # get variables of data
  map <- data$raster
  qty <- names(map)
  
  # project fp to crs of map
  fp <- terra::project(fpraster, crs(map)) # duurt 4 sec
  fp[is.na(fp)] <- 0
  fp[fp<0] <- 0
  
  # crop map file to fp file size
  map.1 <- crop(map, fp, snap='out')
  
  # makes fp resolution equal to map.1 resolution
  fp.final <- resample(fp, map.1,method = "near")  
  
  # put cell-values in dataframe, for both footprint and map 
  fp.df <- as.data.frame(fp.final * prod(res(fp.final)), na.rm=F)
  map.df <- as.data.frame(as.matrix(map.1)[,1])
  df <- cbind(fp.df, map.df) %>% na.omit()
  colnames(df) <- c('fp', 'code')
  
  
  if(cat == T){ # for categorical data (Bodemkaart, LGN)
    classes <- data$classes
    contr_df <- data.frame(matrix(ncol = nrow(classes), nrow = 0)) 
    colnames(contr_df) <- classes$code
    
    # for every class, calculate summed contribution
    for(j in 1:nrow(classes)){
      code <- classes$code[j]
      perc_in_fp <- sum(df$fp[df$code == code])
      contr_df[1,j] <- perc_in_fp / sum(fp.df, na.rm = T) # to make entire fp equal to 100%
      
    }
      
  
  return(contr_df)
    

    
  } else{ # for continuous data (PeatD and ahn)
    df['x'] <- df$fp * df$code
    data_contr <- sum(df$x) / sum(fp.df, na.rm = T) # to make entire fp equal to 100%
    contr_df <- data.frame(qty = data_contr)
  }
  
  
  }

  