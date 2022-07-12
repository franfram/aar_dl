#' .. content for \description{} (no empty lines) ..
#' This function chops the wrangled data into segments of `segment_length` seconds that include
#' the predefined 'behaviours'
#'  
#' 
#' .. content for \details{} ..
#'
#' @title Chop data into segments
#' @param wrangled_full_data
#' @param behaviours_key pass a string with a letter to indicate which behaviours to include.
#'  options are A, B, C, D, E or F. 
#' @param seconds_per_segment pass an integer to indicate the length of the segments in seconds.
#'  options are 5 to 1. 
chop_data <- function(wrangled_full_data, behaviours_key, seconds_per_segment) {

  # behaviours_key <- "A"
  # behaviours_key == "A"
  # seconds_per_segment <- 5

  # wrangled_full_data <- tar_read(wrangled_full_data)

  # Define behaviours to include in segments depending on the input of `behaviours` argument
  if (behaviours_key == "A") {
    behaviours_to_include <- c(
      'eating', 
      'resting',
      'vigilance'
    )
  } else if (behaviours_key == "B") {
    behaviours_to_include <- c(
      'eating', 
      'resting', 
      'vigilance', 
      'walk'
    )
  } else if (behaviours_key == "C") {
    behaviours_to_include <- c(
      'eating', 
      'resting', 
      'vigilance', 
      'walk', 
      'fast_walk'
    )
  } else if (behaviours_key == "D") {
    behaviours_to_include <- c(
      'eating', 
      'resting', 
      'vigilance', 
      'walk', 
      'fast_walk', 
      'search'
    )
  } else if (behaviours_key == "E") {
    behaviours_to_include <- c(
      'eating', 
      'resting', 
      'vigilance', 
      'walk', 
      'fast_walk', 
      'search', 
      'shake' 
    )
  } else if (behaviours_key == "F") {
    behaviours_to_include <- c(
      'eating', 
      'resting', 
      'vigilance', 
      'walk', 
      'fast_walk', 
      'search', 
      'shake', 
      'scratch'
    )
  }


  # split `wrangled_full_data` into sub-datasets containing a given behaviour (here we include all the behaviours present in the full dataset)
  behaviour_datasets <- wrangled_full_data %>% 
    group_by(behaviours) %>% 
    group_split()


  # Now we keep only the behaviours in `behaviours_to_include`
  kept_behaviours <- behaviour_datasets %>% 
    keep(
      ~ unique(.x$behaviours) %in% behaviours_to_include
    )


  # Daily Diaries frequency
  DD_Hz  <- 40


  # N of rows per segment
  nrow_per_segment <- DD_Hz * seconds_per_segment




  # Now define a function to chop the data into segments
  
  # @title "Chop" data into segments. 
  # @description Iteratively slice (chop) a dataset into segments (sub-datasets)
  #  of predefined length. 
  # @return `output` list containing each segment sub-dataset.  
  # @param dataset, dataset to be "chopped"
  # @param nrow_per_segment, predefined N of rows of each segment
  # @param keep_remaining, logical indicating if remaining rows of `dataset` are
  #   to be kept, in the case where the number of segments is not a whole number.
  #   If TRUE (default), the last segment will contain the remaining rows. If 
  #   FALSE, remaining rows will be dropped. 


  chop <- function(
    dataset, 
    nrow_per_segment, 
    keep_remaining = FALSE 
  ) {
    
    n_segments <- nrow(dataset) / nrow_per_segment
    n_segments_floor <- floor(n_segments)
    
    output <- list()   
    for (i in 1:n_segments_floor) {
      segment_head <- ((i - 1) * nrow_per_segment + 1)
      segment_tail <- (i * nrow_per_segment)
      
      output[[i]] <-  dataset %>%  
        slice(segment_head:segment_tail)
      
    }
    
    print(
      paste0(
        "chopped dataset into ", 
        n_segments_floor, 
        " segments"
      )
    )
    
    if (keep_remaining == TRUE) {
      output[[i + 1]] <- dataset %>% 
        slice(segment_tail:nrow(dataset))
      
      print(
        paste0(
          "Kept remaining rows inside an extra ", 
          nrow(output[[i + 1]]),
          " row segment"
        )
      )
    } 
    
  
  return(output)
    
  }

# Chop (dropping remaining rows) data into segments. 
## Inside each behaviours data set (kept_behaviours[[i]]) we will first group
## by `sheep_number` and then chop the data into segments.
chopped_datasets <- kept_behaviours %>%
  map(
    .x, 
    .f = ~{ .x %>% 
      group_by(sheep_number) %>% 
      group_map(
        .x, 
        .f = ~ { 
          chop(
            .x,
            nrow_per_segment = nrow_per_segment,
            keep_remaining = FALSE
          )
        }, 
        .keep = TRUE
      )
    }
  )

  ## Now `chopped_datasets` is a list of 3 levels of data. 
  ## The first level is the behaviours. The second level is
  ## the sheep number. The third level is the segments.

  return(chopped_datasets)







}
