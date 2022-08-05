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
#' @param behaviours_key pass a vector with the letters to indicate which behaviours to include.
#'  options are A, B, C, D, E or F. 
#' @param seconds_per_segment pass an integer vector to indicate the length of the segments in seconds.
#'  options are 5 to 1.
#' @return
#' @author franfram
#' @export
split_train_validate_test <- function(validate_percentage = 0.2,
                                      test_percentage = 0.1
                                      behaviours_key = c("A", "B", "C", "D", "E", "F"), 
                                      seconds_per_segment = 5) {




  "this has to loop through seconds and behaviours"
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
  "TO DELETE"
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
    print("PASSING. Test, validate, and train sets are correctly distributed")
  } else {
    stop("FAILING. Test, validate, and train sets are NOT correctly distributed")
  }
  ## Now `sheeps_test` has length equal to the amount of behaviours, and contains the
  ## number of sheeps to be used for the test set. Same with `sheeps_validate` and `sheeps_train`.


  # Now we will randomly select `sheeps_*` the complete data directory.
  # We have to sample in a way that no sheep is selected twice.
  sheeps_test_selected <- list()
  sheeps_validate_selected <- list()
  sheeps_train_selected <- list()

  for (behav in seq_along(behaviour_names)) {
    sheeps_test_selected[[behav]] <- sheep_data_paths[[behav]][1:sheeps_test[[behav]]] %>% print
    sheeps_validate_selected[[behav]] <- sheep_data_paths[[behav]][(sheeps_test[[behav]] + 1):(sheeps_validate[[behav]] + sheeps_test[[behav]])] %>% print
    sheeps_train_selected[[behav]] <- sheep_data_paths[[behav]][(sheeps_validate[[behav]] + sheeps_test[[behav]] + 1):(sheep_data_names_count[[behav]] )] %>% print
  }

  # Now `sheeps_*_selected` has length equal to the amount of behaviours, and contains the
  # paths to the sheeps directories of each data-set. 

  # Test that `sheeps_*_selected` is correctly distributed
  for (behav in seq_along(behaviour_names)) {
    if (
      length(sheeps_test_selected[[behav]]) + length(sheeps_validate_selected[[behav]]) + length(sheeps_train_selected[[behav]]) == sheep_data_names_count[[behav]]
    ) {
      print(
        str_glue(
          "PASSING for {toupper(behaviour_names[[behav]])}. Test, validate, and train data paths are correctly distributed"))
    } else {
        stop(
          "FAILING for {toupper(behaviour_names[[behav]])}. Test, validate, and train data paths are NOT correctly distributed")
    }
  }
                                      

  # now we have to create the train, validate, and test directories, 
  # with the sheeps directories inside them. For that we could just
  # replace the word "complete" for "train", "validate", and "test" 
  # out of the `sheeps_*_selected` paths. 
  # After that, we will copy the files from the `complete` directory to the `train`, `validate`, and `test` directories.
  test_data_paths <- list()
  validate_data_paths <- list()
  train_data_paths <- list()
  for(behav in seq_along(behaviour_names)) {
    ## Get paths for test, validate, and train data directories
    test_data_paths[[behav]] <- str_replace_all(
      sheeps_test_selected[[behav]], c("complete" = "test")
    )
    validate_data_paths[[behav]] <- str_replace_all(
      sheeps_validate_selected[[behav]], c("complete" = "validate")
    )
    train_data_paths[[behav]] <- str_replace_all(
      sheeps_train_selected[[behav]], c("complete" = "train")
    )

    ## Create directories
    dir_create(test_data_paths[[behav]])
    dir_create(validate_data_paths[[behav]])
    dir_create(train_data_paths[[behav]])

    ## Copy files 
    ### Test
    dir_copy(
      path = sheeps_test_selected[[behav]], 
      new_path = test_data_paths[[behav]], 
      overwrite = TRUE
    )

    ### Validate
    dir_copy(
      path = sheeps_validate_selected[[behav]], 
      new_path = validate_data_paths[[behav]], 
      overwrite = TRUE
    )

    ### Train
    dir_copy(
      path = sheeps_train_selected[[behav]], 
      new_path = train_data_paths[[behav]], 
      overwrite = TRUE
    )
  }


  for (behav in seq_along(behaviour_names)) {
    ## Test set
    if (
     test_test <- dir_ls(
        path = test_data_paths[[behav]], 
        type = 'file',
        recurse = TRUE
        ) %>% length != 0
    ) {
      print(str_glue("PASSING for {toupper(behaviour_names[[behav]])}. Properly copied files to test directory"))
    } else {
      stop("FAILING for {toupper(behaviour_names[[behav]])}. Not properly copying test files")
    }

    if (
     test_validate <- dir_ls(
        path = validate_data_paths[[behav]], 
        type = 'file',
        recurse = TRUE
     ) %>% length != 0
    ) {
      print(str_glue("PASSING for {toupper(behaviour_names[[behav]])}. Properly copied files to validate directory"))
    } else {
      stop("FAILING for {toupper(behaviour_names[[behav]])}. Not properly copying validate files")
    }

    if (
     test_train <- dir_ls(
        path = train_data_paths[[behav]], 
        type = 'file',
        recurse = TRUE
        ) %>% length != 0 
    ) {
      print(str_glue("PASSING for {toupper(behaviour_names[[behav]])}. Properly copied files to train directory"))
    } else {
      stop("FAILING for {toupper(behaviour_names[[behav]])}. Not properly copying train files")
    }
  }
   
  



































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
