# Import libraries
import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import numpy as np
from dash_holoniq_wordcloud import DashWordcloud


# Data Cleaning
df = pd.read_csv('doping_cases.csv')

df_copy = df.copy()

cleansed_data = []
# iterating on the rows of the df
for i,row in df_copy.iterrows():
    # put each row to a dict
    row_data = row.to_dict()
    # if the substance is NOT empty
    if not pd.isnull(row_data["substance"]):
        # while there is ( in the substance 
        while "(" in row_data["substance"]:
            # find the index of first (
            first_index = row_data["substance"].find("(")
            # find the index of first )
            second_index = row_data["substance"].find(")")
            # cut out the string from first ( to first )
            row_data["substance"] = (row_data["substance"][:first_index] + row_data["substance"][second_index+1:]).strip()
        # cut out the useles spaces after and before comas
        row_data["substance"] = row_data["substance"].strip().lower().replace(", ", ",").replace(" ,", ",")
    # append the data to cleanes_data list
    cleansed_data.append(row_data)
# saving the cleaned data to csv file
pd.DataFrame(cleansed_data).to_csv('doping_cases_clean.csv')


# Map Visualization

# prepare the dataframe for the mapvisualization
# read in csv as pandas dataframe
df = pd.read_csv('doping_cases_clean.csv')
# print(df)

# Make a copy of the DataFrame
df_copy = df.copy()

# Sum of occurances of each country and save it as a DataFrame
count_of_country= pd.Series(df_copy["country"]).value_counts().to_frame().reset_index()

# Merge the two DataFrames, to have a column with the count of each country
df_country = df_copy.merge( count_of_country,  left_on = "country", right_on = "country")

# creating figure for map visualization
fig_map = px.scatter_geo(df_country,
                     lat = "latitude",
                     lon= "longitude",
                     #colored by country
                     color="country",
                     hover_name="country",
                     labels={'country': 'Country',
                             'count': 'Count',
                             'latitude': 'Latitude',
                             'longitude': 'Longitude'},
                     hover_data={"country": False,
                                 "count": True,
                                 "latitude": True,
                                 "longitude": True},
                     # size of the circles are based on the occurance of the countries
                     size = "count",
                     projection= "natural earth",
                     width=700,
                     height=600,
                     color_discrete_sequence = ["#4B5945","#66785F","#4F6F52", "#739072","#91AC8F",
                                                "#86A789", "#B6C7AA","#B2C9AD","#D2E3C8","#A0937D", 
                                                "#A59D84", "#C1BAA1", "#E7D4B5", "#D7D3BF", "#F6E6CB", 
                                                "#ECEBDE", "#E5E1DA", "#F1F0E8", "#3C5B6F","#89A8B2", 
                                                "#B3C8CF", "#B3C8CF", "#BED7DC"],
                     template = "ggplot2",
                     )

#Wordcloud

# a filtered df to exclude where we don't have a substance
filtered_for_substances = df[pd.isnull(df["substance"]) == False]
# cleaning the sport column to have the sports in title form
filtered_for_substances["sport"] = df.sport.str.title()
# creating a list out of the sports, to use it at the Dropdown
sports = sorted(list(set(filtered_for_substances['sport'].values)))

count_of_substances= pd.Series(df_copy["substance"]).str.split(",").value_counts().to_frame().reset_index()

# global variable for the list of substances
SUBSTANCE_LIST = count_of_substances.values.tolist()


# Timeline

# preapre dataframe for timeline
# put the dates to datetime format
df["date_of_birth"] = pd.to_datetime(df["date_of_birth"], errors= "coerce")
# get the year and month
df["date_y_m"] = df["date_of_birth"].astype(str).str[:7]
df["date_y_m"] = pd.to_datetime(df["date_y_m"], errors= "coerce")
# get the year
df["year"] = df["date_of_birth"].astype(str).str[:4]

# group people by year and month
df["date_occurence"] = df.groupby("date_y_m").transform(lambda x: 1 + np.arange(len(x)))["date_of_birth"]

# filter out people without date of birth
FILTERED_FOR_DOB = df[pd.isnull(df["date_of_birth"]) == False]

# the min year in the year column
MIN_YEAR = FILTERED_FOR_DOB['year'].astype(int).min()
# the max year in the year column
MAX_YEAR = FILTERED_FOR_DOB['year'].astype(int).max()


# create timeline 
timeline = px.scatter(
    FILTERED_FOR_DOB,
    x = "date_of_birth",
    y = "date_occurence",
    labels = {
        "date_of_birth" : "Date of Birth",
        "date_occurence" : "Cardinality of the Date (Year and Month)"
    },
    color="name",
    hover_name= "name",
    hover_data={"date_of_birth": True,
                "date_occurence": False,
                "name": False},
    color_discrete_sequence = ["#4B5945","#66785F","#4F6F52", "#739072","#91AC8F","#86A789", 
                               "#B6C7AA","#B2C9AD","#D2E3C8","#A0937D", "#A59D84", "#C1BAA1", 
                               "#E7D4B5", "#D7D3BF", "#F6E6CB", "#ECEBDE", "#E5E1DA", "#F1F0E8",
                               "#3C5B6F","#89A8B2", "#B3C8CF", "#B3C8CF", "#BED7DC"],
    template = "ggplot2"
    )



#DASH
app = Dash()

# The layout of out DASH
app.layout = [
    # Main title
    html.H1(children='Doping in sports', 
            style={'color' : '#153448',
                   'fontSize': 40,
                   'textAlign': 'center'}),
    # First main div, row with map and wordcloud
    html.Div(
        className='row',
        children=[
            # Div for Map
            html.Div([
                # Map title
                html.H2(children='Map of Doping in Sports', 
                        style={'color' : '#3C5B6F',
                               'textAlign': 'center'}),
                # First graph - the map
                dcc.Graph(id='map', figure=fig_map)],
                # position of the map
                style={'width': '46%',
                       'float': 'left',
                       'display': 'inline-block',
                       'marginTop': '5px'}),
            # Div for Wordcloud
            html.Div([
                # Wordcloud title
                html.H2(children='Most Used Substances', 
                        style={'color' : '#3C5B6F',
                               'textAlign': 'center'}),
                # Dropdown
                dcc.Dropdown(sports,
                            id="sports_dropdown",
                            value = None,
                            placeholder="Select a sport"),
                html.Br(),
                # Wordcloud
                html.Div([
                    DashWordcloud(
                        id='word',
                        list=SUBSTANCE_LIST,
                        width=800, height=500,
                        gridSize=16,
                        color="#3C5B6F",
                        backgroundColor="#E5E1DA",
                        shuffle=False,
                        rotateRatio=0.5,
                        shrinkToFit=True,
                        shape='circle',
                        hover=True,
                        weightFactor = 20
                        )]
                )
            ],
            # position of the wordcloud
            style={'width': '53%',
                   'float': 'right',
                   'display': 'inline-block',
                   'marginTop': '5px'}
            )
        ]),
    html.Br(),    
    # Second main div, row with timeline
    html.Div(className='row', children=[
        html.Div([
        # Timeline title
        html.H2(children='Timeline of sportsmen', 
                style={'color' : '#3C5B6F',
                       'textAlign': 'center'}),
        # Timeline
        dcc.Graph(id='timeline', figure=timeline),
        #Year slider
        dcc.RangeSlider(
            min=MIN_YEAR-(MIN_YEAR%10) ,
            max=MAX_YEAR+(10-(MAX_YEAR%10)),
            step=10,
            value=[MIN_YEAR-(MIN_YEAR%10),
                   MAX_YEAR+(10-(MAX_YEAR%10))],
            marks={str(year): str(year) for year in range(
                MIN_YEAR-(MIN_YEAR%10), 
                MAX_YEAR+(10-(MAX_YEAR%10)+1),
                10)},
            id='year-slider')
        ],
        style={'width': '100%',
               'float': 'left',
               'display': 'inline-block',
               'marginTop': '5px'}),
        
        
    ])]

# Callback for sports_dropdown
@app.callback(
        # using the wordcloud's list as output
        Output('word', 'list'),
        # using the dropdown values as input
        Input('sports_dropdown', 'value')
        )

# update_word function for updating the wordcloud by the dropdown values
def update_word(value):
    """Filtering the wordcloud based on the sports_dropdown input value.

    Args:
        value: the value from the sports_dropdown

    Returns:
        list: the new, filtered substance list
    """
    # if all sports are deselected
    if value == None:
      list = SUBSTANCE_LIST
    # else - there is a sport selected
    else:
        # update the dataframe to include just that sport
        dff = filtered_for_substances[filtered_for_substances.sport==value]
        # get the counts for each substance
        count_of_substances= pd.Series(dff["substance"]).str.split(",").value_counts().to_frame().reset_index()
        # create a list with the counts
        substance_list = count_of_substances.values.tolist()
        list = substance_list
    return list

#Callback for slider
@app.callback(
        # using the wordcloud's list as output
        Output('timeline', 'figure'),
        # using the dropdown values as input
        Input('year-slider', 'value')
        )

def update_timeline(value):
    """Filtering the timeline based on the year_slider input value.

    Args:
        value: the value/ range from the year_slider

    Returns:
        timeline: the filtered, updated timeline
    """
    updated_dob = FILTERED_FOR_DOB[(value[0] <= FILTERED_FOR_DOB["year"].astype(int)) & (FILTERED_FOR_DOB["year"].astype(int) <= value[1])]
    timeline = px.scatter(
        updated_dob,
        x = "date_of_birth",
        # position all points on the same horizontal line
        y = "date_occurence",
        labels = {
            "date_of_birth" : "Date of Birth",
            "date_occurence" : "Cardinality of the Date (Year and Month)"
        },
        color="name",
        hover_name= "name",
        hover_data={"date_of_birth": True,
                    "date_occurence": False,
                    "name": False},
        color_discrete_sequence = ["#4B5945","#66785F","#4F6F52", "#739072","#91AC8F","#86A789", 
                                "#B6C7AA","#B2C9AD","#D2E3C8","#A0937D", "#A59D84", "#C1BAA1", 
                                "#E7D4B5", "#D7D3BF", "#F6E6CB", "#ECEBDE", "#E5E1DA", "#F1F0E8",
                                "#3C5B6F","#89A8B2", "#B3C8CF", "#B3C8CF", "#BED7DC"],
        template = "ggplot2"
        )
    return timeline


# running the dash app in debug mode
if __name__ == '__main__':
    app.run(debug=True)