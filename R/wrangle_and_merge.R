#' .. content for \description{
#' Function to merge and wrangle cleaned datasets
#' } (no empty lines) ..
#'
#' .. content for \details{} ..
#'
#' @title Wrangle and merge cleaned datasets
#' @param clean_sep_data
#' @param clean_dec_data
wrangle_and_merge <- function(clean_sep_data, clean_dec_data) {

  clean_sep_data <- tar_read(clean_sep_data)
  clean_dec_data <- tar_read(clean_dec_data)

  # Remove rows that contain NAs in the columns specified
  vars_with_na <- c("mag_x", "mag_y", "mag_z", "roll.angle", "behaviours")  



  temp_sep  <- clean_sep_data %>% drop_na 
  temp_dec  <- clean_dec_data %>% drop_na


  # Merge datasets and then wrangle
  ## Merge
  wrangled_full_data <- bind_rows(temp_sep, temp_dec) %>% 
    ## Re-arrange columns
    select(
      'sheep_name', 
      'sheep_number', 
      'year', 
      'month', 
      'day', 
      'hours', 
      'minutes', 
      'seconds',
      'event.no.',
      'acc_x', 
      'acc_y',
      'acc_z', 
      'mag_x', 
      'mag_y',
      'mag_z', 
      'pitch.angle', 
      'roll.angle',
      'behaviours',
      'video_name', 
      'video_number',
      'file_name'
    ) %>% 
    ## Sort data
    arrange(
      sheep_number, 
      year, 
      month, 
      day, 
      hours, 
      minutes, 
      seconds,
      event.no.
    ) %>% 
    ## Rename behaviours with tidyverse style + correct duplicated ones  
    mutate(
      behaviours = recode(
        behaviours, 
        'Search' = 'search', 
        'Eating' = 'eating', 
        'Vigilance' = 'vigilance', 
        'Fast.walk' = 'fast_walk', 
        'Walk' = 'walk', 
        'Fast.Walk' = 'fast_walk', 
        'Scratch' = 'scratch', 
        'Eating.up' = 'eating',
        'Vigilance.down' = 'vigilance', 
        'Resting' = 'resting', 
        'Shake' = 'shake', 
        'Scracth' = 'scratch'
      )
    ) %>% 
    ## Create proper date-time variable
    mutate(
      #hours_minutes_seconds = make_datetime(hours, minutes, seconds)
      date_time = make_datetime(year, month, day, hours, minutes, seconds),
      hms = as_hms(date_time)
    )

  

  return(wrangled_full_data)

}
