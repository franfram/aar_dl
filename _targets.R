## Load your packages, e.g. library(targets).
source("./packages.R")

## Load your R files
lapply(list.files("./R", full.names = TRUE), source)

## tar_plan supports drake-style targets and also tar_target()
tar_plan(

# target = function_to_ma____ke(arg), ## drake style

# tar_target(target2, function_to_make2(arg)) ## targets style

    # 'dec' means December
    tar_files(dec_files, list.files("data/dic", full.names = TRUE)), 
    # 'sep' means September
    tar_files(sep_files, list.files("data/sep", full.names = TRUE)), 

    raw_dec_data = read_files(file_target = dec_files), 

    raw_sep_data = read_files(file_target = sep_files)

)
