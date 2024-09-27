find_owasis_for_twr <-
  
  function(alldata, rasterno, owasisdf){
    
    
    # -----------------------------------------------------
    # author: lvdpoel
    # edited by: arietma
    
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
    
    # main data: all tower measurements
    #alldata <- read.csv('C:/Users/ariet/Documents/Climate Studies/WSG Thesis/data/tower/tower_0607.csv', header=T, row.names='X')
    alldata <- read.csv('/lustre/backup/WUR/ESG/rietm018/thesis/tower_0607.csv', header=T, row.names='X')
    
    # get year and doy from row in df
    year <- str_trim(alldata[rasterno,]$Date) %>% substr(1,4)
    doy <- ceiling(alldata[rasterno,]$DOY) %>% str_pad(3, pad='0')
    yeardoy <- as.Date(paste0(year, '-', doy), format = "%Y-%j")
    
    datediffs <- as.numeric(difftime(owasisdates,yeardoy, units = 'days'))
    
    fileno <- which(abs(datediffs) == min(abs((datediffs))))                 
    file <- owasisdf[fileno,1]
    
    return(list(OwfileNo = fileno, Owfile = file))
  }



