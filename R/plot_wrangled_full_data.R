#' .. content for \description{} (no empty lines) ..
#'
#' .. content for \details{} ..
#'
#' @title Plot accelerometer data from wrangled_full_data
#' @param wrangled_full_data
plot_wrangled_full_data <- function(wrangled_full_data) {

  wrangled_full_data <- tar_read(wrangled_full_data)

  # Prepare data for plots
  ## Pivot longer for using color aesthetics with acc axis
  data_for_plots <- wrangled_full_data %>% 
    # Accelerometer values
    pivot_longer(
      c(
        'acc_x',
        'acc_y',
        'acc_z',
      ), 
      names_to = 'acc_axis', 
      values_to = 'acc_value'
    ) %>% 
    # Magnetometer values
    pivot_longer(
      c(
        'mag_x',
        'mag_y',
        'mag_z',
      ), 
      names_to = 'mag_axis', 
      values_to = 'mag_value'
    )

  # Params for plot with map2
  ## we will make plots with purrr, using sheep number and day as parameters. 
  ## we thus need a dataset with a combination of sheep_number and days. 
  plot_parameters <- wrangled_full_data %>% 
    count(sheep_number, day) %>% 
    select(-n)
    



  # plots showing Accelerometer values as a function of time. 
  plots_acc_per_sheep <- map2(
    .x = plot_parameters$sheep_number, 
    .y = plot_parameters$day, 
    .f = ~{
      data_for_plots %>% 
        filter(sheep_number == .x) %>% 
        filter(day == .y) %>% 
        ggplot() + 
        geom_line(
          aes(
            x = hms, 
            y = acc_value, 
            color = acc_axis
          )
        ) +
        scale_color_viridis_d(
          alpha = 0.6#,
          #option = "plasma"
        ) +
  #      scale_color_brewer() +
        labs(
          title = paste0("Sheep number: ", .x, "   | Day: ", .y)
        ) +
        theme_minimal()
    } 
  )

  plotlys_acc_per_sheep <- map(plots_acc_per_sheep, ggplotly)

  return(
    plots_acc_per_sheep
  )


}


