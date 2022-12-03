# Raspberry Pi DHT22 blog post
Code for a blog post about setting up a freezer temperature sensor on a Raspberry Pi.

```
├── LICENSE                             
├── README.md
├── app.R								# R Shiny app for vizualizing the freezer data
├── python
│   ├── freezer_alarm.py                # Sends emails when temps are high or sensor is down
│   ├── python_data
│   ├── read_freezer_thermocouple.py    # Reads temp, shows on display, updates Google sheet
│   └── trim_google_sheets.py           # Keeps Google sheets small
├── service
│   └── freezer.service                 # Automatically starts read_freezer_thermocouple.py
├── url
│   └── freezer_1.tsv                   # Stores URLs of Google sheets for freezer data
└── www
    └── favicon.ico                     # Cute icon for Shiny app
```
