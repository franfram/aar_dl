#' .. content for \description{} (no empty lines) ..
#' This function chops the wrangled data into segments of `segment_length` seconds that include
#' the predefined 'behaviours'
#' 
#' .. content for \details{} ..
#'
#' @title Chop data into segments
#' @param wrangled_full_data
#' UPDATE WITH FOR LOOP CORRECTION
#' @param behaviours_key pass a vector with the letters to indicate which behaviours to include.
#'  options are A, B, C, D, E or F. 
#' @param seconds_per_segment pass an integer vector to indicate the length of the segments in seconds.
#'  options are 5 to 1. 
chop_data <- function(
  wrangled_full_data, 
  behaviours_key = c("A", "B", "C", "D", "E", "F"),
  seconds_per_segment = c(5, 4, 3, 2, 1)
) {
  

  # First define a function to chop the data into segments
  
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

    # Write condition to avoid problems with very small sheep-level datasets
    if (nrow(dataset) > nrow_per_segment) {

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
    } else {
      print("doin NOTIN")
    } 
  
  return(output)
    
  }

  # interactive target
  # behaviours_key  <- c('A', 'B', 'C')#c('A', 'B', 'C', 'D', 'E', 'F')
  # seconds_per_segment <- 5#c(5:1)
  
  # wrangled_full_data  <- tar_read(wrangled_full_data)
  # behaviours_key = c('A', 'B', 'C', 'D', 'E', 'F'), 
 



  # Start nested loop to iterate over behaviours and seconds_per_segment, chopping
  # data and storing it in each iteration 
  for (behaviours in behaviours_key) {#c("A")) {#behaviours_key) {
    for (seconds in seconds_per_segment){#5) {#seconds_per_segment){

      #Define behaviours to include in segments depending on the input of `behaviours` argument
      if (behaviours == "A") {
        behaviours_to_include <- c(
          'eating', 
          'resting',
          'vigilance'
        )
      } else if (behaviours == "B") {
        behaviours_to_include <- c(
          'eating', 
          'resting', 
          'vigilance', 
          'walk'
        )
      } else if (behaviours == "C") {
        behaviours_to_include <- c(
          'eating', 
          'resting', 
          'vigilance', 
          'walk', 
          'fast_walk'
        )
      } else if (behaviours == "D") {
        behaviours_to_include <- c(
          'eating', 
          'resting', 
          'vigilance', 
          'walk', 
          'fast_walk', 
          'search'
        )
      } else if (behaviours == "E") {
        behaviours_to_include <- c(
          'eating', 
          'resting', 
          'vigilance', 
          'walk', 
          'fast_walk', 
          'search', 
          'shake' 
        )
      } else if (behaviours == "F") {
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

      #split `wrangled_full_data` into sub-datasets containing a given behaviour (here we include all the behaviours present in the full dataset)
      behaviour_datasets <- wrangled_full_data %>%
        group_by(behaviours) %>%
        group_split()


      # Now we keep only the behaviours in `behaviours_to_include`
      kept_behaviours <- behaviour_datasets %>%
        keep(
          ~ unique(.x$behaviours) %in% behaviours_to_include
        )


      #return(kept_behaviours)

      # Daily Diaries frequency
      DD_Hz  <- 40


      # N of rows per segment
      nrow_per_segment <- DD_Hz * seconds# seconds_per_segment


      # Create directories. The parent folder is going to be 
      # named str_glue("python_", behaviours, "_", seconds, "s"). This folder will contain sub-folders 
      #  with names contained in `behaviours_to_include`. And then inside of each of 
      # these sub-folders, there will be folders named after the sheep number. Inside
      # of each of these sheep number folders, we will store the chopped data.
      for (i in seq_along(behaviours_to_include)) {
    
        # get sheep numbers of each behaviour sub-dataset
        sheep_identifier <- kept_behaviours[[i]]$sheep_number %>% unique
        
        for (j in seq_along(sheep_identifier)) { 
          
          # Define path of directores
          path_dirs <- here(
              "data", 
              str_glue("python_complete_", behaviours, "_", seconds, "s"),
              behaviours_to_include[[i]],# before behaviours_to_keep[[1]][[i]], 
              str_glue("sheep_", sheep_identifier[[j]])
            )
          # Create behaviour sub-folders and sheep_number 
          # sub-sub-folders and store file_path for writing csvs
          dir_create(path_dirs)
          
          # Print folder created
          print(
            str_glue(
              "Created the following directory: \n", 
              path_dirs, 
              "\n"
            )
          )
        }    
      }



          

      # Chop (dropping remaining rows) data into segments. 
      ## Inside each behaviours data set (kept_behaviours[[i]]) we will first group
      ## by `sheep_number` and then chop the data into segments.
      chopped_datasets <- map(
          .x = kept_behaviours,
          .f = ~{
            .x %>%
              group_by(sheep_number) %>%
              group_map(
                .f = ~{
                  # Write condition to avoid problems with very small sheep-level datasets
                  if (nrow(.x) >= nrow_per_segment) { 
                    chop(
                      .x,
                      nrow_per_segment = nrow_per_segment,
                      keep_remaining = FALSE
                      )
                  }
                }
              )
            }
          )
        ## Now `chopped_datasets` is a list of 3 levels of data. 
        ## The first level is the behaviours. The second level is
        ## the sheep number. The third level is the segments.

      
      
      
      
        # Store chopped data
        for (i in seq_along(behaviours_to_include)) {

          # Get sheep numbers of each behaviour sub-dataset
          sheep_identifier <- kept_behaviours[[i]]$sheep_number %>% unique

          for (j in seq_along(sheep_identifier)) {

            for (k in seq_along(chopped_datasets[[i]][[j]])) {

              # Store path where chopped data will be saved
              path_files = here(
                'data',
                str_glue('python_complete_', behaviours, '_', seconds, 's'),
                behaviours_to_include[[i]], # before behaviours_to_keep[[1]][[i]],
                str_glue('sheep_', sheep_identifier[[j]]),
                str_glue('segment_', k)
              )

              # write `chopped_data` segments to csv files
              write_csv(
                x = chopped_datasets[[i]][[j]][[k]],
                file = path_files
                )

              # Print where the data is being saved
              print(
                str_glue(
                  "Stored chopped data at: \n",
                  path_files,
                  "\n"
                )
              )

            }
          }
        }

        # Write test to check if all segments are of same length
        test = list()
        for (j in seq_along(chopped_datasets)) {
          for (k in seq_along(chopped_datasets[[j]])) {
            for (m in seq_along(chopped_datasets[[j]][[k]])) {

              test[m * j * k] <- print(nrow(chopped_datasets[[j]][[k]][[m]]))

            }
          }

          check  <- test %>% unlist() %>% unique()

          if (length(check) == 1) {
            print("All segments have the same number of rows")
          } else {
            print("Segments have different number of rows ")
          }

        }

      

    }
  }


# Chop (dropping remaining rows) data into segments. 
## Inside each behaviours data set (kept_behaviours[[i]]) we will first group
## by `sheep_number` and then chop the data into segments.
# chopped_datasets <- kept_behaviours %>%
#   map(
#     .x, 
#     .f = ~{ .x %>% 
#       group_by("sheep_number") %>% 
#       group_map(
#         .x, 
#         .f = ~ { 
#           chop(
#             .x,
#             nrow_per_segment = nrow_per_segment,
#             keep_remaining = FALSE
#           )
#         }, 
#         .keep = TRUE
#       )
#     }
#   )

  ## Now `chopped_datasets` is a list of 3 levels of data. 
  ## The first level is the behaviours. The second level is
  ## the sheep number. The third level is the segments.


  # Create directories. The parent folder is going to be 
  # named str_glue("python_", behaviours_key). This folder will contain sub-folders 
  #  with names contained in `behaviours_to_inclue`. And then inside of each of 
  # these sub-folders, there will be folders named after the sheep number. Inside
  # of each of these sheep number folders, we will store the chopped data.


  # for (i in seq_along(behaviours_to_include)) {

  #   sheep_identifier <- kept_behaviours[[1]]$sheep_number %>% unique
    
  #   for (j in seq_along(sheep_identifier)) { 

  #     # Create behaviour sub-folders and sheep_number 
  #     # sub-sub-folders and store file_path for writing csvs
  #     dir_create(
  #       here(
  #         "data", 
  #         str_glue("python_", behaviours_key),
  #         str_glue("b_", behaviours_to_include[[i]]),# before behaviours_to_keep[[1]][[i]], 
  #         str_glue("sheep_", sheep_identifier[[j]])
  #       )
  #     )

  #   }    
  # }



  # # store chopped data
  # for (i in seq_along(behaviours_to_keep[[1]])) {

  #   sheep_identifier <- kept_behaviours[[1]][[i]]$sheep_number %>% unique
    
  #   for (j in seq_along(sheep_identifier)) { 

  #     for (k in seq_along(chopped_datasets[[i]][[j]])) {
      
  #     # write `chopped_data` segments to csv files
  #     write_csv(
  #       file = here(
  #         "data", 
  #         "python_1", 
  #         str_glue("b_", i), # before behaviours_to_keep[[1]][[i]], 
  #         str_glue("sheep_", sheep_identifier[[j]]), 
  #         str_glue("segment_", k)
  #       ),
  #       x = chopped_datasets[[i]][[j]][[k]] 
  #     )

  #     }
  #   }
  # }











   #return(chopped_datasets)







}
