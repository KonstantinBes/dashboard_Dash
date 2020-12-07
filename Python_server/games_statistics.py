"""
Dashboard for game release statistics.
Based on plotly and dash libraries.

Sources:
https://leftjoin.ru/all/dashboard-python-1
https://dash.plotly.com
"""

import pandas as pd
import numpy as np
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html

from dash.dependencies import Input, Output
from plotly.graph_objects import Layout as lo

colorscales = px.colors.named_colorscales()

games_data = pd.read_csv('games.csv')

# clean data
games_data.dropna(inplace=True)
games_data.drop(
    games_data[games_data['Year_of_Release'] < 2000].index,
    axis='index',
    inplace=True)

years_available = list(np.sort(games_data['Year_of_Release'].unique()))
genres_available = list(games_data['Genre'].unique())
ratings_available = list(games_data['Rating'].unique())

# updating dataframe by conditions
def filter_df(from_year, till_year, selected_genres, selected_ratings):
    df = pd.DataFrame(games_data)

    selected_years = [y for y in range(int(from_year), int(till_year) + 1)]
    for year in years_available:
        if year in df['Year_of_Release'].unique():
            if year not in selected_years:
                df.drop(
                    df[df['Year_of_Release'].values == year].index,
                    inplace=True)
        elif year in selected_years:
            df = df.append(
                games_data[games_data['Year_of_Release'].values == year])

    for genre in genres_available:
        if genre in df['Genre'].unique():
            if genre not in selected_genres:
                df.drop(
                    df[df['Genre'].values == genre].index,
                    inplace=True)
        elif genre in selected_genres:
            df = df.append(
                games_data[games_data['Genre'].values == genre])

    for rating in ratings_available:
        if rating in df['Rating'].unique():
            if rating not in selected_ratings:
                df.drop(
                    df[df['Rating'].values == rating].index,
                    inplace=True)
        elif rating in selected_ratings:
            df = df.append(
                games_data[games_data['Rating'].values == rating])

    # count games sharing the same year of release and platform
    df['Games_released'] = df\
        .groupby(['Platform', 'Year_of_Release'])['Name']\
        .transform('nunique')

    return(df)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H3('Game release statistics'),

    html.Div(
        'Visualization of game releases by year, platform, genre, etc.'
        ),

    html.Div([
        html.Label('Choose genres:'),
        dcc.Dropdown(
            id='genre_filter',
            options=[{'label':i, 'value':i} for i in games_data['Genre'].unique()],
            value=genres_available[0:3],
            multi=True
            ),
        ],
        style = {'width': '54%', 'display': 'inline-block'}),

    html.Div([
        html.Label('Choose ratings:'),
        dcc.Dropdown(
            id='rating_filter',
            options=[{'label':i, 'value':i} for i in games_data['Rating'].unique()],
            value=ratings_available[0:3],
            multi = True
            ),
        ],
        style = {'width': '44%', 'display': 'inline-block'}),
        
    html.Div(id='games_number'),
        
    html.Div([
        dcc.Graph(id='area_plot'),
    ], style = {'width': '49%', 'display': 'inline-block'}),
    
    html.Div([
        dcc.Graph(id='scatter_plot'),
    ], style={'width': '49%', 'display': 'inline-block'}),

    html.Div([
        html.Label('Years since:'),
        dcc.Dropdown(
            id='start_year',
            value=min(years_available),
            ),
        ], style={'width': '24%', 'display': 'inline-block'}),
    html.Div([
        html.Label('Years until:'),
        dcc.Dropdown(
            id='end_year',
            options=[{'label':i, 'value':i} for i in years_available],
            value=max(years_available),
            ),
        ], style={'width': '24%', 'display': 'inline-block'}),
])

@app.callback(
    Output('start_year', 'options'),
    Input('end_year', 'value'))
def start_year_options(till_year):
        return [{'label':i, 'value':i} for i in years_available if i < till_year]
        
@app.callback(
    Output('end_year', 'options'),
    Input('start_year', 'value'))
def end_year_options(from_year):
        return [{'label': i, 'value': i} for i in years_available if i > from_year]

@app.callback(
    Output('games_number', 'children'),
    Input('start_year', 'value'),
    Input('end_year', 'value'),
    Input('genre_filter', 'value'),
    Input('rating_filter', 'value'))
def update_text(from_year, till_year, selected_genres, selected_ratings):
    df_1 = pd.DataFrame(filter_df(from_year, till_year, selected_genres, selected_ratings))
    games_num = 'Games selected: {}'.format(len(df_1))
    return games_num

@app.callback(
    Output('scatter_plot', 'figure'),
    Input('start_year', 'value'),
    Input('end_year', 'value'),
    Input('genre_filter', 'value'),
    Input('rating_filter', 'value'))
def update_scatter(from_year, till_year, selected_genres, selected_ratings):
    df_2 = pd.DataFrame(filter_df(from_year, till_year, selected_genres, selected_ratings))
    scatter_fig = px.scatter(
        df_2, x="User_Score", y="Critic_Score",
        size="Games_released", color="Genre", size_max=25)
    return scatter_fig

@app.callback(
    Output('area_plot', 'figure'),
    Input('start_year', 'value'),
    Input('end_year', 'value'),
    Input('genre_filter', 'value'),
    Input('rating_filter', 'value'))
def update_area_plot(from_year, till_year, selected_genres, selected_ratings):
    df_3 = pd.DataFrame(filter_df(from_year, till_year, selected_genres, selected_ratings))
    area_figure = px.area(
        df_3, x="Year_of_Release",
        y = "Games_released", color = "Platform")
    return area_figure

if __name__ == '__main__':
    app.run_server(debug=True)