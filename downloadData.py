import urllib.request
import os, sys


os.chdir(os.path.dirname(sys.argv[0]))

url_confirmed = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
url_deaths = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"
url_recovered = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv"

urllib.request.urlretrieve(url_confirmed, './data/corona_time_series_confirmed.csv')
urllib.request.urlretrieve(url_deaths, './data/corona_time_series_deaths.csv')
urllib.request.urlretrieve(url_recovered, './data/corona_time_series_recovered.csv')