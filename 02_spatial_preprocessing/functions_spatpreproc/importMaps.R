# -----------------------------------
# author: lvdpoel
# edited by: arietma

# function to import maps from ruimtelijke data veenweiden
# input: tif/asc files for maps and classes documents
# output: object with all maps and classes stored
# requires library(raster), library(foreign) and library(randomcoloR)

# Edits by arietma:
# - Omitted reclassification of LGN/Bodemkaart, as this is done at a later stage
# in reclassify_soil.py and reclassify_LGN.py since the data was available in a 
# different format. Also omitted legend as the map should be reclassified first
# - Added loading in Veendikte and ahn

# -----------------------------------


# importMaps
importMaps <- function(path) {
  
  maps <- NULL
  
  ## Read in
  ## LGN2020
  LGNpath <- paste0(path, '/Landgebruik_LGN2020')
  dataMaps <- rast(paste0(LGNpath , '/LGN2020.tif'))
  classes <- read.csv(paste0(LGNpath, '/LGN2020_legend.csv'))
  LGN2020 <- NULL
  LGN2020$classes <- classes
  LGN2020$raster <- dataMaps
  maps$LGN2020 <- LGN2020
  


  # load Veendikte map
  Veenpath <- paste0(path, '/Veendikte')
  dataMaps <- rast(paste0(Veenpath , '/Veendikte_2014_cm_Fryslan.tif'))
  dataMaps[dataMaps >50000] <- NA
  classes <- read.dbf(paste0(Veenpath, '/Veendikte_2014_cm_Fryslan.tif.vat.dbf'))
  colors <- distinctColorPalette(length(classes[,1]))
  classes <- cbind(classes, colors)
  rm(colors)
  Veendikte <- NULL
  Veendikte$classes <- classes # value en count als columns
  Veendikte$raster <- dataMaps
  maps$Veendikte <- Veendikte
  
   
  
  ## Bodemkaart 
  Bodempath <- paste0(path, '/Bodemkaart')
  dataMaps <- rast(paste0(Bodempath , '/Bodemkaart_5m.tif'))
  classes <- read.dbf(paste0(Bodempath, '/Bodemkaart_5m.tif.vat.dbf'))
  Bodemkaart <- NULL
  Bodemkaart$classes <- classes
  Bodemkaart$raster <- dataMaps
  Bodemkaart$classes$code <- Bodemkaart$classes$Value 
  maps$Bodemkaart <- Bodemkaart
  
  
  
  ## Hoogtekaart
  Hoogtepath <- paste0(path, '/ahn25')
  dataMaps <- rast(paste0(Hoogtepath, '/ahn25.asc'))
  crs(dataMaps) <- "+init=epsg:28992"
  AHN <- NULL
  AHN$raster <- dataMaps
  maps$AHN <- AHN
  
  

  return(maps)
}


