#------------
# author: arietma

# This script stores the OWASIS files in the correct folders for running
# fp_air_spattemp_hpc.R and fp_twr_spattemp_hpc.R

# Input: OWASIS files with all variables in 1 folder, different folders per year
# Output: organized OWASIS files, with for each OWASIS variable, a separate folder

#------------

# Specify the path to the folders in which the OWASIS files are currently saved
rm(list=ls())
folder_2021 <- "C:/Users/ariet/Documents/Climate Studies/WSG Thesis/data/preprocessing/friesland_2021"
folder_2022 <- "C:/Users/ariet/Documents/Climate Studies/WSG Thesis/data/preprocessing/friesland_2022"
folder_2023 <- "C:/Users/ariet/Documents/Climate Studies/WSG Thesis/data/preprocessing/friesland_2023"

# Get all files present in every folder
list.2021.files <- list.files(folder_2021, pattern = '.tif', full.names = TRUE)
list.2022.files <- list.files(folder_2022, pattern = '.tif', full.names = TRUE)
list.2023.files <- list.files(folder_2023, pattern = '.tif', full.names = TRUE)

# Specify new folder names and paths
ow.bb.folder <- "C:/Users/ariet/Documents/Climate Studies/WSG Thesis/data/preprocessing/owasis/complete_dataset/Beschikbare.Bodemberging/"
ow.gr.folder <- "C:/Users/ariet/Documents/Climate Studies/WSG Thesis/data/preprocessing/owasis/complete_dataset/Grondwaterstand/"

# Specify old folder name, new folder name and the list of files in the old folder
old_folder <- folder_2023 #ADJUST
new_folder <- ow.bb.folder #ADJUST
files <- list.2023.files #ADJUST

# Specify all files in the folder for Beschikbare Bodemberging or Grondwaterstand
files_to_move <- files[grep("Beschikbare.Bodemberging", files)] #ADJUST  
# gr.folder 'Grondwaterstand' and for bb.folder 'Beschikbare.Bodemberging'

# Move files to new folder
file.rename(files_to_move, file.path(new_folder, basename(files_to_move)))



