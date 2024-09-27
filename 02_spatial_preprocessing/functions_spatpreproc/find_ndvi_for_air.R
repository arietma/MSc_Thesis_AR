# -----------------------------------------------------
# author: lvdpoel
# edited by: arietma, original file name: find_owasis_for_fp.R (original file name)

# Function to find the correct MODIS (NDVI/EVI) files that are closest or second
# to closest in time compared to the airborne footprint measurement date
    
# Input: 
#    ndvi_all: raster with every layer a modis NDVI or EVI raster, 
#    rasterno: number of the footprint raster(.nc) 
# Output: 
#    ModfileNo: number of modisfile with the date closest to the measurement date, 
#    Modfile: the actual file,
#    ModfileNo2: number of modisfile with the date second closest to the measurement date,
#    Modfile2: the actual file of ModfileNo2
#    daydiff:the difference in days between ModFile and the measurement (for interpolation), 
#    daydiff2:the difference in days between ModFile2 and the measurement
    
# Important note: be sure to load in the correct airborne dataset in 'alldata', 
# and make sure that the Date column is in the correct format
    
# Requires library(terra) and library(stringr) 

# Edits by arietma:
# - Aligned the function to the dataset used in the current thesis
# - Added modfile(no)2 and daydiff(2), used later for interpolation
# - Small correction; earlier the yeardoy (of the airborne dataset/fp measurement)
#   and moddates were minimized. However, if yeardoy is early in a new year and
#   the closest moddate is late in the previous year, this does not work. 
# -------------------------------------------------------- 

find_ndvi_for_air <-
  function(rasterno, ndvi_all){  
    
    # Main data: all airborne measurements;   SPECIFY
    alldata <- read.csv('/lustre/backup/WUR/ESG/rietm018/thesis/airborne_morecols_0907.csv', header=T, row.names=1)
    #alldata <- read.csv('C:/Users/ariet/Documents/Climate Studies/WSG Thesis/data/airborne_morecols_0907.csv', header=T, row.names=1)
    
    # Get date from row in df
    fp_date <- as.Date(alldata$Date[rasterno], format = '%d-%m-%Y')
    
    # Get dates for MODIS files
    modyears <- names(ndvi_all) %>% substr(1,4)
    moddoys <- names(ndvi_all) %>% substr(5,7)
    moddates <- as.Date(paste0(modyears, '-', moddoys), format = "%Y-%j")
    
    # Calculate absolute differences (in days) between fp_date and moddates
    datediffs <- as.numeric(difftime(moddates, fp_date, units = 'days'))
    
    # Find which modfileno lies closest to the footprint measurement
    modfileno <- which(abs(datediffs) == min(abs((datediffs))))
    
    # If the fp_date lies exactly in between two modis maps (-8 and 8), select only one
    if (length(modfileno) == 2) {modfileno <- modfileno[1]}
    
    # Get the corresponding modfile
    modfile <- ndvi_all[[modfileno]]
    # How many days between fp_date and moddate, use later for interpolation
    daydiff <- datediffs[modfileno] 
    
    # For interpolation, also get modfileno and modfile with name second closest to fp_date
    modfileno2 <- which(abs(datediffs) == sort(abs(datediffs))[2])
    if (length(modfileno2) == 2) {modfileno2 <- modfileno2[2]}
    modfile2 <- ndvi_all[[modfileno2]]
    # How many days btwn fp_date and moddate2, use later for interpolation
    daydiff2 <- datediffs[modfileno2] 
    
    # Because the dates of modis are fixed every year, the following can occur: 
    # e.g. for 2022-01-10, the closest and second closest dates are 2012-12-27 
    # and 2022-01-09. These dates are both before 2022-01-10, and then interpolation 
    # is not possible (in calc_ndvi_in_fp.R). In these occurrences the third closest 
    # date is chosen for modfile2
    
    if (daydiff < 0 & daydiff2 < 0){
      modfileno2 <- which(abs(datediffs) == sort(abs(datediffs))[3])
      modfile2 <- ndvi_all[[modfileno2]]
      daydiff2 <- datediffs[modfileno2]
    }
    
    # This can also occur for a date late in the year
    if (daydiff > 0 & daydiff2 > 0){
      modfileno2 <- which(abs(datediffs) == sort(abs(datediffs))[3])
      modfile2 <- ndvi_all[[modfileno2]]
      daydiff2 <- datediffs[modfileno2]
    }
  
    
    
    return(list(ModfileNo=modfileno, Modfile=modfile, ModfileNo2=modfileno2, Modfile2=modfile2,
                DayDiff=daydiff, DayDiff2=daydiff2))
    
  }


