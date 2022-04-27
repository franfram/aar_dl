#' .. content for \description{
#' Read all the files in file target and return a list of data frames with\
#'  the contents of the csv files. 
#' } (no empty lines) ..
#'
#' .. content for \details{} ..
#'
#' @title Read raw data
#' @param dec_files
#' @return `list` of data frames with each file's contents
#' @author franfram
#' @export
read_files <- function(file_target) {
  raw_data <- file_target %>% 
    map(
      read_csv, 
      id = "file_name", 
      col_types = cols()
    ) %>% 
    suppressMessages()

  return(raw_data)
}
