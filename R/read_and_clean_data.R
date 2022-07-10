#' .. content for \description{} (no empty lines) ..
#'
#' .. content for \details{} ..
#'
#' @title Read and wrangle september and december files. 
#' @param data_target target file to read, previously created with tar_files
#' @param month string indicating the month of the data to be wrangled. 
read_and_clean_data <- function(
  data_target, 
  month 
) {


  ## stopifnot

  # Add if statement to generalize the function to both September and December files. 

 if (month == "September") {

    vars_to_keep <- c(
      'file_name',
      'Acc_x',
      'Acc_y',
      'Acc_z', 
      'Mag_x',
      'Mag_y',
      'Mag_z',
      "Pitch.angle", 
      "Roll.angle", 
      'DateTime', 
      'Hours',
      'Minutes',
      'Seconds',
      'Event.no.',
      'Behaviours'
    )
  } else if (month == "December") {
  
    vars_to_keep <- c(
      'file_name',
      'Acc_x',
      'Acc_y',
      'Acc_z', 
      'Mag_x',
      'Mag_y',
      'Mag_z',
      "Pitch.angle", 
      "Roll.angle", 
      'DateTime', 
      'Hours',
      'Minutes',
      'Seconds',
      'Event.no.',
      'Behaviours'
    )
  }
  
  
   else {
    stop("Check that the month passed is correct")
  }



  # Read and clean data 
  clean_data <- data_target %>% 
    # Read files
    map(
      read_csv, 
      id = "file_name",
      col_types = cols()
    ) %>%
    # Select columns to keep
    map(
      ~ select(
        .x,
        any_of(vars_to_keep)
      )
    ) %>% 
    # Add sheep name column
    map(
      ~ add_column(
          .x, 
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
            )
          )
      )
    ) %>% 
    # Add Year variable
    map(
      ~ mutate(
          .x, 
          year = year(DateTime)
      )
    ) %>% 
    # Add Month variable
    map(
      ~ mutate(
          .x, 
          month = month(DateTime)
      )
    ) %>% 
    # Add Day variable
    map(
      ~ mutate(
          .x, 
          day = day(DateTime)
      )
    ) %>%
    # Remove DateTime var
    map(
      ~ select(
          .x,
          -'DateTime'
      )
    ) %>% 
    # Rename all vars to lower-case names to avoid problems
    map(
      ~ rename_all(
          .x, 
          tolower
      )
    ) %>% 
    # Some `second` variables are not numeric, so convert them 
    map(
      ~ mutate(
        .x, 
        seconds = as.double(seconds)
      )
    ) %>% 
    # Add column indicating video name
    map(
      ~ mutate(
          .x,
          video_name = str_extract(
            .x$file_name, 
            pattern = "video.."
          )
      )
    ) %>% 
    # Add column indicating video number
    map(
      ~ mutate(
          .x, 
          video_number = as.double(
            str_extract(
              .x$video_name, 
              pattern = "[0-9]+"
            ) 
          )  
      )
    ) %>% 
    # Bind rows to form a single tibble
    bind_rows #%>% 
    #suppressMessages()







  return(clean_data)

  
}
