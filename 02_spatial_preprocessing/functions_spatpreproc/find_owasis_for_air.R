find_owasis_for_air <-
  
  function(alldata, rasterno, owasisdf){
    
    
    # -----------------------------------------------------
    # author: lvdpoel
    # edited by: arietma, original file name: find_owasis_for_fp.R (original file name)
    
    # Script to find correct owasis file number given a footprint raster number, based on the fp-measurement date.
    # Input: owasisdf: list with all owasis files, rasterno: number of the footprint raster.nc saved in folder
    # Output: OwfileNo: number of owasis file with correct date, Owfile: the actual file
    
    # Requires library(terra) and library(stringr) 
    
    # Edits by arietma:
    # - None other than specifying the dataset used in the current thesis
    # -------------------------------------------------------- 
    
    
    owasisyears <- owasisdf$yeardoy %>% substr(1,4)
    owasisdoys <- owasisdf$yeardoy %>% substr(5,7)
    owasisdates <- as.Date(paste0(owasisyears, '-', owasisdoys), format = "%Y-%j") 
    
    # main data: all airborne measurements
    alldata <- read.csv('/lustre/backup/WUR/ESG/rietm018/thesis/airborne_morecols_0907.csv', header=T, row.names=1)
    #alldata <- read.csv('C:/Users/ariet/Documents/Climate Studies/WSG Thesis/data/airborne_morecols_0907.csv', header=T, row.names=1)
    
    # get year and doy from row in df
    yeardoy <- as.Date(alldata$Date[rasterno], format = '%d-%m-%Y')
    
    datediffs <- as.numeric(difftime(owasisdates,yeardoy, units = 'days'))
    
    fileno <- which(abs(datediffs) == min(abs((datediffs))))                 
    file <- owasisdf[fileno,1]
    
    return(list(OwfileNo = fileno, Owfile = file))
  }



