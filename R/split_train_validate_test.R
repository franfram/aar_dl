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
  behaviour_names <- behaviour_directories %>% map(~ basename(.x)) %>% unname()

  print("behaviours used: ")
  print(behaviour_names %>% unlist)
  

  ## Get sheep dirs per behaviour
  sheep_data_paths <- map(
    .x = behaviour_names, 
    .f = ~ { 
      dir_ls(
        path = here("data", "python_complete_A_5s", .x), 
        type = 'dir' 
      )  %>% 
      as.character
    }
  ) %>% print

  # Get sheep names per behaviour
  sheep_data_names <- map(
    .x = behaviour_names, 
    .f = ~ { 
      dir_ls(
        path = here("data", "python_complete_A_5s", .x), 
        type = 'dir' 
      ) %>% 
      map(~ basename(.x)) %>%
      unname %>%
      unlist
    }
  ) %>% print
       

  # Count how many sheeps per behaviour
  sheep_data_names_count <- sheep_data_names %>% map(length) %>% unlist %>% print
      
  


  # Split those sheeps into train, validate, and test sets according to the
  # (approximate) percentages passed as arguments
  ## Interactive stuff
  validate_percentage = 0.2
  test_percentage = 0.1
  train_percentage = 1 - validate_percentage - test_percentage

  ## Define number of sheeps (for all behaviours) based on rounded-up validate and test percentages, 
  ## the rest goes to training
  ### Test set
  
  sheeps_test <- (test_percentage * sheep_data_names_count) %>% ceiling() %>% print

  ### Validate set
  sheeps_validate <- (validate_percentage * sheep_data_names_count) %>% ceiling() %>% print

  ### Train set
  sheeps_train <- (sheep_data_names_count - sheeps_test - sheeps_validate) %>% print


  ## Test that the test, validate, and train sets are correctly distributed
  if (unique(sheep_data_names_count == sheeps_test + sheeps_validate + sheeps_train)) {
    print("Test, validate, and train sets are correctly distributed")
  } else {
    print("FAIL. Test, validate, and train sets are NOT correctly distributed")
  }
  ## Now `sheeps_test` has length equal to the amount of behaviours, and contains the
  ## number of sheeps to be used for the test set. Same with `sheeps_validate` and `sheeps_train`.


  # Now we will randomly select `sheeps_*` the complete data directory.
  # We have to sample in a way that no sheep is selected twice.
  .x <- sheeps_test[[1]]
  .x <- 1
  .x <- 1:length(behaviour_names)

  j <- sheeps_test[[.x]]
  "still have to map this"
  sheeps_test_selected <- sheep_data_paths[[.x]][1:sheeps_test[[.x]]] %>% print
  sheeps_validate_selected <- sheep_data_paths[[.x]][(sheeps_test[[.x]] + 1):(sheeps_validate[[.x]] + sheeps_test[[.x]])] %>% print
  sheeps_train_selected <- sheep_data_paths[[.x]][(sheeps_validate[[.x]] + sheeps_test[[.x]] + 1):(sheep_data_names_count[[.x]] )] %>% print
  # Test for this crappy code?



  # now we have to create the train, validate, and test directories, 
  # with the sheeps directories inside them. For that we could just
  # replace the word "complete" for "train", "validate", and "test" 
  # out of the `sheeps_*_selected` paths.


  .x <- sheeps_test_selected[[1]]  

  "and have to map this"
  test_data_paths <- str_replace_all(sheeps_test_selected, c("complete" = "test"))







































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
