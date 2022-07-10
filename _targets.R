## Load your packages, e.g. library(targets).
source("./packages.R")

## Load your R files
lapply(list.files("./R", full.names = TRUE), source)

## fnmate setup
options(fnmate_searcher = "git_grep")
options(fnmate_quote_jump_regex = TRUE) 

## tar_plan supports drake-style targets and also tar_target()
tar_plan(

# target = function_to_ma____ke(arg), ## drake style

# tar_target(target2, function_to_make2(arg)) ## targets style

    # Track data files
    ## 'dec' means December, 'sep' means September
    ## 
    tar_files(dec_files, list.files("data/dec", full.names = TRUE)), 
    tar_files(sep_files, list.files("data/sep", full.names = TRUE)), 

    # Read and wrangle data files
    ## September data
    clean_sep_data = read_and_clean_data(
        data_target = sep_files, 
        month = "September"
    ), 
    ## December data
    clean_dec_data = read_and_clean_data(
        data_target = dec_files, 
        month = "December"
    ),

    # Wrangle and merge September and December data
    wrangled_full_data = wrangle_and_merge(
        clean_sep_data, 
        clean_dec_data
    ),

    # Plot accelerometer and magnetometer data
    plots_wrangled_full_data = plot_wrangled_full_data(
        wrangled_full_data
    ),

    # Chop data into segments
    chopped_data = chop_data(
        wrangled_full_data,
        behaviours, 
        segment_length
    )
 
)
# 