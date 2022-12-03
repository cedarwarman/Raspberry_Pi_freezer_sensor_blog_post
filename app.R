library(shiny)
library(lubridate)
library(googlesheets4)
library(plotly)
library(bslib)

# Functions ---------------------------------------------------------------
import_dataset <- function(sheet_id) {
  # Avoiding permissions (make sure sheet is public)
  gs4_deauth()
  df <- read_sheet(sheet_id)
  
  # Making a single column for date and time
  df$date_time <- ymd_hms(paste(df$date, df$time))
  # Changing the data column from a string to date type
  df$date <- ymd(df$date)
  
  return(df)
}

# This function will make a temperature plot
make_temp_plot <- function(input_df) {
  # Making plot
  output_plot <- plot_ly(
    data = input_df,
    x = ~date_time,
    y = as.numeric(input_df$temp_c),
    type = "scatter",
    mode= "markers",
    marker = list(size = 6, color = "magenta")
  )
  
  # Adding aesthetics
  # This is so clunky but it's how the docs say to do it :/
  hline <- function(y = 0, color = "cyan") {
    list(
      type = "line",
      x0 = 0,
      x1 = 1,
      xref = "paper",
      y0 = y,
      y1 = y,
      layer = "below",
      line = list(color = color,
                  dash = "dot",
                  width = 5)
    )
  }
  
  output_plot <- output_plot %>% layout(
    shapes = list(hline(-65)), 
    xaxis = list(title = list(text = "Date and time",
                              font = list(size = 24)),
                 showline = T,
                 showgrid = F,
                 linewidth = 1,
                 linecolor = "white",
                 tickfont = list(size = 15)),
    yaxis = list(title = list(text = "ºC",
                              font = list(size = 24),
                              standoff = 10),
                 showline = T,
                 zeroline = F,
                 showgrid = F,
                 linewidth = 1,
                 linecolor = "white",
                 tickfont = list(size = 15)),
    font = list(family = "Arial-BoldMT",
                color = "white"),
    paper_bgcolor = "#060606",
    plot_bgcolor = "#060606",
    showlegend = F
  )
  
  # Makes the y-axis a little nicer if there's no data that's super warm.
  if (max(input_df$temp_c) < 0) {
    output_plot <- output_plot %>% layout(
      yaxis = list(range = list(-90, 0))
    )
  }
  
  # Removing toolbar
  output_plot <- output_plot %>% config(displayModeBar = F) 
  
  return(output_plot)
}

ui <- bootstrapPage(
  theme  = bs_theme(version = 5,
                  bootswatch = 'cyborg'),
  tags$style(type='text/css',
             "h1 { font-size: calc(1.525rem + 1.5vw); }"), 
  tags$head(tags$link(rel = "shortcut icon", href = "favicon.ico")),

  div(class = "container-fluid",
      div(class = "row justify-content-center",
          align = "center",
          div(class = "col-xl-8",
              h1(strong("Freezer temperature")),
              plotlyOutput("freezer_plot", height = "50vh")
          )
      )
  )
)


server <- function(input, output, session) {
  # Importing the data
  freezer_data <- import_dataset("1KpIEUuMpRD8q3DDNNUeJ1BqSztl_nAzA8DWtdTHFnVY")
  
  # Making the plot
  output$freezer_plot <- renderPlotly(make_temp_plot(freezer_data))
}

shinyApp(ui, server)