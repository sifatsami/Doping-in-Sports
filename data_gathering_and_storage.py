# Import libraries
from urllib.request import urlopen
from bs4 import BeautifulSoup
import json
import pandas as pd
import string
import time
import os

# Global folder variables for stroing the HTMLs

MAIN_HTML_FOLDER = "doping_htmls"
#generating the main_html_folder with os library if it does not exist
#if the folder doesn't exist and the creatinon successful
try:
    os.mkdir(MAIN_HTML_FOLDER)
    print(f"Directory '{MAIN_HTML_FOLDER}' created successfully.")
    #if the folder already exists
except FileExistsError:
    print(f"Directory '{MAIN_HTML_FOLDER}' already exists.")
    # if the user has no permisson creating the folder
except PermissionError:
    print(f"Permission denied: Unable to create '{MAIN_HTML_FOLDER}'.")
    #if something other error occures
except Exception as e:
    print(f"An error occurred: {e}")
   
PERSONAL_HTML_FOLDER = "personal_htmls"
#generating the personal_html_folder with os library
#if the folder doesn't exist and the creatinon successful
try:
    os.mkdir(PERSONAL_HTML_FOLDER)
    print(f"Directory '{PERSONAL_HTML_FOLDER}' created successfully.")
    #if the folder already exists
except FileExistsError:
    print(f"Directory '{PERSONAL_HTML_FOLDER}' already exists.")
    # if the user has no permisson creating the folder
except PermissionError:
    print(f"Permission denied: Unable to create '{PERSONAL_HTML_FOLDER}'.")
    #if something other error occures
except Exception as e:
    print(f"An error occurred: {e}")


# Fetching the uppercase alphabet from string library
UPPERCASE_ALPHABHET = string.ascii_uppercase

# Web scraping

# Fetch data and create the local html file
def fetch_htmls(url, html_folder):
    """Creating and saving HTML files by scraping the Wikipedia site corresponting the letter in the 
       uppercase alphabet.
    Args:
        url: the url to be scraped
        html_folder: the folder to save the created HTML file
    """
    # try and except necessary as some of the dopers has no wikipedia site
    try:
        # Create a new  separate html files for all our pages (A-Z) or persons and save it the corresponding folder
        file = open(f"{html_folder}/doping_{element}.html", "w", encoding="utf-8")
        # Fetch Data and Create html file
        html = urlopen(url).read().decode("utf-8")
        # write html file
        file.write(html)
        # close the file
        file.close()
    except Exception as e:
        print("There is no personal webpage.", e)

# Looping over the pages from A to Z
for letter in UPPERCASE_ALPHABHET:
    # Identify URLs, letter variable changing from loop to loop
    url = f"https://en.wikipedia.org/wiki/List_of_doping_cases_in_sport_({letter})"
    # in this case in the fetch_htmls function our element will be the letter
    element = letter
    # calling fetch_htmls function
    fetch_htmls(url, html_folder=MAIN_HTML_FOLDER)


# Extract data from the local html files
def scrape_htmls_by_rows(local_file, list_of_data):
    """Creating a list of dictionaries, each dictionary corresponding to a person, containing: name, 
    country, sport, substance and webpage.
    Args:
        local_file: the file to be parsed
        list_of_data: a list of dictionaries for each person
    Returns:
        list of updated dictionaries for each person
    """
    soup = BeautifulSoup(local_file, features ="html.parser")

    # find rows inside the html
    rows = soup.findAll(name = "tr")

    # iterating through rows, strating from index 1 because of the header
    for row in rows[1:]:
        #creating empty dictionary for every person
        person = {}
        # defining cells inside each row
        tds = row.find_all("td")
        # saving new elements of the dictionary by indexing into the cells of the row
        person["name"] = tds[0].text.strip()
        person["country"] = tds[1].text.strip()
        person["sport"] = tds[2].text.strip()
        # if statement for page A as there is an extra column in the table on page A
        if letter == "A":
            person["substance"] = tds[4].text.strip()
        else: 
            person["substance"] = tds[3].text.strip()
        # try and except for the href, as not all person has a wikipedia site 
        try:
            person["webpage"] = tds[0].a["href"]
        except Exception as e:
            person["webpage"] = ""
        # appending persons to the list we created
        list_of_data.append(person)
    # The function will return the list_of_persons
    return list_of_data

# creating empty list for storing our data, inside the list every person will have a dictionary
list_of_persons =[]
#looping files A to Z
for letter in UPPERCASE_ALPHABHET:
    # Open html file
    local_file = open(f"{MAIN_HTML_FOLDER}/doping_{letter}.html", "r", encoding="utf-8")
    # calling scrape_htmls_by_rows function
    scrape_htmls_by_rows(local_file, list_of_persons)

# Fecthing the date_of_birth from local personal html files
def fetch_date_of_birth(local_file, list_of_data):
    """Fetching the date of birth from the athlete's personal wikipedia site and saveing it to the 
    athlete's dictionary.
    Args:
        local_file: the file to be parsed
        list_of_data: a list of dictionaries for each person
    Returns:
        list of updated dictionaries with date of birth for each person
    """
    try:  
        soup = BeautifulSoup(local_file, features ="html.parser")
        # finding the data_of_birth in the html
        bday = soup.find("span", attrs ={"class": "bday"}).text.strip()
        #save data_of_birth to the dictionary
        person["date_of_birth"] = bday 
    except Exception as exc:
        person["date_of_birth"] = ""
    return list_of_data

# looping over our list_of_all to fecth htmls for all the persons
for i,person in enumerate(list_of_persons, start=1):
    # Presonal counter to see where we are at the process
    print(f"Personal counter: {i}/{len(list_of_persons)}")
    # out element will be the name of the person (this will be used in the fetch_htmls function)
    element = person["name"]
    # Identify URLs, as we are looping over the people in the list, the person['webpage'] will change from loop to loop
    personal_url = f"https://en.wikipedia.org{person['webpage']}"

    # calling fetch_htmls function to save the htmls of each person
    fetch_htmls(personal_url, PERSONAL_HTML_FOLDER)

    # open local personal html file
    local_file = open(f"{PERSONAL_HTML_FOLDER}/doping_{element}.html", "r", encoding="utf-8")
    # calling fetch_date_of_bith function to save the date_of_birth to the dictionary of each person
    fetch_date_of_birth(local_file, list_of_persons)

with open('list_of_persons_without_coordinates.json', 'w') as f:
    json.dump(list_of_persons, f, indent=4)


#Geocode

# defining the endpoint url
endpoint = "https://geocode.maps.co/search"
# Szimona's apikey for geocode
apikey = "673dd372ca8b1719133004lmu987ca9"

# creating a set for countries
unique_countries = set()
for person in list_of_persons:
    # add country to the set and replacing the " " with "_"
    unique_countries.add(person["country"].replace(" ", "_"))

# function for fetching coordinates
def fetch_coordinates(country_name, list_of_countries, list_of_unknown_countries):
    """Fetching the coordinates (lat and lon) using the Geocode API.

    Args:
        country_name: the name of the unique countries
        list_of_countries: list of dictionaries for each unique country with name, lat and lon
        list_of_unknown_countries: list of unidentifiable countries
    Returns:
        the updated lists
    """
    # creating empty dict for the country
    country_dict = {}
    # first key:value pair
    country_dict["name"] = country_name
    # try except necessary, bacause there are some countries which has no coordinates on the website
    try:
        # unique url with coutry and apikey
        url = f"{endpoint}?country={country_name}&api_key={apikey}"
        page = urlopen(url)
        content = page.read().decode("utf-8")
        contentjs = json.loads(content)
        # second key:value pair
        country_dict["longitude"] = contentjs[0]["lon"]
        # thirs key:value pair
        country_dict["latitude"] = contentjs[0]["lat"]
        # append the dict to the list of countries
        list_of_countries.append(country_dict)
        # sleep time as 1 request/sec is out limit
        time.sleep(1.5)
    except Exception as e:
        # if the country not found this message is printed out
        print(f"Country not found: {country}")
        # the country saved to a list_of_unknown_countries
        list_of_unknown_countries.append(country)
    # the two lists are returned
    return list_of_countries, list_of_unknown_countries


# creating the empty lists
list_of_countries = []
list_of_unknown_countries = []
# iterating through the unique_countries list, index starts at 1
for i,country in enumerate(list(unique_countries), start=1):
    # Coordinate counter to see where are we
    print(f"Coordinate counter: {i}/{len(unique_countries)}")
    # calling the fetch_coordinates function
    fetch_coordinates(country, list_of_countries,list_of_unknown_countries)

# save the list_of_countries to json for back-up
with open('list_of_countries.json', 'w') as f:
    json.dump(list_of_countries, f, indent=4)

# save the list_of_unknown_countries to json for back-up
with open('list_of_unknown_countries.json', 'w') as f:
    json.dump(list_of_unknown_countries, f, indent=4)

# open the list of countries
with open('list_of_countries.json', 'r') as f:
    list_of_countries = json.load(f)

# open list_of_persons
with open('list_of_persons_without_coordinates.json', 'r') as f:
    list_of_persons = json.load(f)

# saving the coorinates from the list_of_countries to our original list_of_persons
# iterating through the dicts inside the list_of_persons
for person in list_of_persons:
    for country in list_of_countries:
        # checking for country, if they are the same, saving the coordinates to the dict
        if person["country"] == country["name"]:
            person["longitude"] = country["longitude"]
            person["latitude"] = country["latitude"]

# saving the data into a json, just in case
with open('doping_cases.json', 'w') as f:
    json.dump(list_of_persons, f, indent=4)

# saving the data into a csv file
pd.DataFrame(list_of_persons).to_csv("doping_cases.csv", index=False)