## library() calls go here
library(conflicted)
library(dotenv)
library(targets)
library(tarchetypes)
library(tidyverse)
library(here)
library(lubridate)
library(reactable)
library(paint)
library(plotly)
library(hms)
library(fs)
library(data.table)
library(pak)

## Conflicted setup
conflict_prefer("filter", "dplyr")


## Define environmental variables for faster interactive work
tm <- tar_make
tv <- tar_visnetwork
tr <- tar_read