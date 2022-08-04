#' .. content for \description{
#'  Split stored segments of data into train, validate, and test sets. 
#'  
#'  To avoid overfitting we need to split the complete data into train, validate, and test sets.
#'  We also need to carefully select how to split the data. 
#'  If segments of the same sheep are split into train, validate, and test sets, we will
#'  find correlation bias in those segments and thus information leakage. 
#'  So we need to select a random subset of segments from each sheep separately, but also 
#'  making sure we have sheeps with all behaviours in train, validate, and test sets.
#' 
#' 
#' } (no empty lines) ..
#'
#' .. content for \details{} ..
#'
#' @title
#' @param validate_percentage
#' @param test_percentage
#' @return
#' @author franfram
#' @export
split_train_validate_test <- function(validate_percentage = 0.2,
                                      test_percentage = 0.1) {
  # Get list of all the files within the complete data directory 
  complete_data_paths <- dir_ls(
    path = here("data", "python_complete_A_5s"),
    type = 'file',
    #glob = "*.csv",
    recurse = TRUE
  ) %>% 
  print()

  # Get list of behaviours directory names
  behaviour_directories <- dir_ls(
    path(here('data', 'python_complete_A_5s')),
    type = 'dir'
  ) %>% 
  map(as.character) %>%
  print

  # Get behaviours names
  behaviour_names <- behaviour_directories %>% map(~ basename(.x))

  # Get sheep names per behaviour

  

  behaviours <- c('eating', 'resting', 'vigilance')
  sheep_directories_per_behaviour <- behaviours %>% 
    map(
      ~ dir_ls(
         path = here('data', 'python_complete_A_5s', str_glue('b_', .x)),
         type = 'dir'
        )
    ) %>% 
    print()

  sheep_directories_per_behaviour[[1]]



  sheep_directories_per_behaviour %>% as.vector() %>% str
  test <- sheep_directories_per_behaviour %>% as.list %>% as.character() 
  test[[1]]
  basename(sheep_directories_per_behaviour)

  attributes(sheep_directories_per_behaviour) <- NULL


  str(sheep_directories_per_behaviuor)

          sheep_name = str_extract(
            .x$file_name,
            "ov.."
          )
      )
    ) %>% 
    # Add sheep number column 
    map(
      ~ add_column(
          .x, 
          sheep_number = as.double(
            str_extract(
              .x$sheep_name,
              "[0-9]+"

  




  # Go to the segment level of the `complete_data_paths` and randomly select
  # Go to a behaviour folder, then select randomly sheeps folders to allocate to the different sets. 
  
  # Gotta use reprex to get the sheep numbers inside each behavior folders
  # Then write a function to decide the percentage of sheeps to go to each set, 
  # for which we will need to round to the nearest integer of sheeps. 


  # a fractiono of the segments to go to the train, validation and test sets. 


  # Split into train, validate, and test sets






}
