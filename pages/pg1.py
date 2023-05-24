import dash
from dash import dcc, html, callback
from dash.dependencies import Output, Input
import plotly.express as px
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import pandas as pd


#importing the dataset
df = pd.read_csv('transformed_data.csv')

platform_options = [{"label": "All Platforms", "value": "all"}] + \
    [{"label": platform, "value": platform} for platform in df["Platform"].unique()]

global_sales_conversions = {
    "NA_Sales": "North America",
    "EU_Sales": "Europe",
    "JP_Sales": "Japan",
    "Other_Sales": "Other",
    "Global_Sales": "Global"
}


def format_number(number):
    if number >= 1000000000:
        return "{:.2f}B".format(number / 1000000000)
    elif number >= 1000000:
        return "{:.2f}M".format(number / 1000000)
    else:
        return str(number)


def get_top_10_best_selling_games(df):
    grouped = df.groupby('Name')[['NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales', 'Global_Sales']].sum()
    top_10 = grouped.sort_values('Global_Sales', ascending=False).head(10)
    return list(top_10.index)


def get_data_from_best_selling(df, best_selling):
    top_sales_df = pd.DataFrame(columns=df.columns)

    for game_name in best_selling:
        game_rows = df[df['Name'] == game_name]
        top_sales_df = pd.concat([top_sales_df, game_rows], ignore_index=True)

    return top_sales_df


def get_sales(df, region, genre=None, platform=None, year=None):
    filters = {'Genre': genre, 'Platform': platform, 'Year': year}
    for column, value in filters.items():
        if value and value != 'all':
            df = df.loc[df[column] == value]

    sales_column = region + '_Sales'
    sales = df[sales_column].mean()

    return sales


def filter_data(df, region="NA_Sales", genre="Action", platform=None, year=None):
    if genre != "all":
        filtered_df = df[df["Genre"] == genre]
    else:
        filtered_df = df

    if year is not None:
        filtered_df = filtered_df[filtered_df["Year"] == year]

    if platform and platform != "all":
        filtered_df = filtered_df[filtered_df["Platform"] == platform]

    columns_to_keep = ['Rank', 'Name', 'Platform', 'Year', 'Genre', 'Publisher', 'NA_Sales', 'EU_Sales', 'JP_Sales',
                       'Other_Sales', 'Global_Sales', 'name', 'Release date', 'Estimated owners', 'Peak CCU',
                       'Required age', 'Price', 'DLC count', 'About the game', 'Supported languages',
                       'Full audio languages', 'Reviews', 'Header image', 'Website', 'Support url', 'Support email',
                       'Windows', 'Mac', 'Linux', 'Metacritic score', 'Metacritic url', 'User score', 'Positive',
                       'Negative', 'Score rank', 'Achievements', 'Recommendations', 'Notes', 'Average playtime forever',
                       'Average playtime two weeks', 'Median playtime forever', 'Median playtime two weeks',
                       'Developers', 'Publishers', 'Categories', 'Genres', 'Tags', 'Screenshots', 'Movies']
    filtered_df = filtered_df[columns_to_keep]

    filtered_df = filtered_df[filtered_df[region] > 0]

    return filtered_df

####################################################################################################
#LAYOUT
####################################################################################################

dash.register_page(__name__, path='/', name = 'Sales Analysis')

#lAYOUT SECTION
layout = dbc.Container([
    # dbc.Row([
    #     #This is to style the title of the dashboard
    #     dbc.Col(html.H1("Steam game data analysis",
    #                     className='text-center bg-light text-primary, mb-4'),
    #             width={"size": 6, "offset": 0})
    #
    #     ], justify='center', align="end"),              # justify = centre, start,end, between, around

    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id="genre-dropdown",
                options=[
                    {"label": "All Genre", "value": "all"},
                    {"label": "Action", "value": "Action"},
                    {"label": "Shooter", "value": "Shooter"},
                    {"label": "Role-Playing", "value": "Role-Playing"},
                    {"label": "Simulation", "value": "Simulation"},
                    {"label": "Adventure", "value": "Adventure"},
                    {"label": "Strategy", "value": "Strategy"},
                    {"label": "Racing", "value": "Racing"},
                    {"label": "Fighting", "value": "Fighting"},
                    {"label": "Sports", "value": "Sports"},
                    {"label": "Misc", "value": "Misc"},
                    {"label": "Platform", "value": "Platform"},
                    {"label": "Puzzle", "value": "Puzzle"},
                ], value='all')
        ], width={"size": 2, "order": 2}
        # xs=12, sm=12, md=12, lg=3, xl=3
        ),

        dbc.Col([
            dcc.Dropdown(
                id="platform-dropdown",
                options=platform_options,
                value="all",
                placeholder="All"
            )

        ], width={"size": 2, "order": 1, "offset": 1}
        # xs=12, sm=12, md=12, lg=3, xl=3
        ),


        dbc.Col([
            dcc.Dropdown(
                id="region-dropdown",
                options=[
                    {"label": "North America", "value": "NA_Sales"},
                    {"label": "Europe", "value": "EU_Sales"},
                    {"label": "Japan", "value": "JP_Sales"},
                    {"label": "Other", "value": "Other_Sales"},
                    {"label": "Global", "value": "Global_Sales"},
                ],
                value="Global_Sales")

        ], width={"size": 2, "order": 3, "offset": 1}
        # xs=12, sm=12, md=12, lg=3, xl=3
        ),

        dbc.Col([
            dcc.Dropdown(
                id="year-dropdown",
                options = [{"label": year, "value": year} for year in sorted(df["Year"].unique(), reverse=True) if pd.notnull(year)],
                value=None)

        ], width={"size": 2, "order": 4}

        ),

    ]),


    #This plots the graphs for the sales vs year
    dbc.Row([
        dbc.Col([
            dcc.Graph(id="sales-year-evolution")
        ], width={"size": 8})
    ], justify="center"),

    #This gives the title of the world map
    dbc.Row([
        dbc.Col(html.H1("Sales Map",
                        className='text-center bg-dark text-white'),
                        width={"size": 3}),
    ], justify="center", className="py-2 py-md-3 py-lg-3 py-xl-3"),

    #This gives the graph for the world map for viewing sales across regions
    dbc.Row([
        dbc.Col([
            dcc.Graph(id = 'map_chart', config={'displayModeBar': True, 'scrollZoom': True},
                      style={'padding-left':'2px'})

        ], width={"size": 8})
    ], justify="center"),

    #This is for the best selling games and metacritic score vs sales
    dbc.Row([
        dbc.Col([
            html.H1("Best Selling Games",
                    className='text-center bg-dark text-white'),

            dcc.Graph(id="top10-global-sales")
            ], width={"size": 5}),
        dbc.Col([
            html.H1("Metacritic score vs Global Sales",
                    className='text-center bg-dark text-white'),

            dcc.Graph(id="metascore-vs-sales")
            ], width={"size": 5}),

        ], justify="center", className="py-lg-3 py-xl-3"),


], fluid=True)

@callback(
    Output("sales-year-evolution", "figure"),
    [Input("region-dropdown", "value"),
     Input("genre-dropdown", "value"),
     Input("platform-dropdown", "value"),
     Input("year-dropdown", "value")]
)
def update_sales_year_evolution(region, genre, platform, year):
    filtered_data = filter_data(df, region, genre, platform, year)
    region_name = global_sales_conversions.get(region, region)

    # Filtered Data accordingly to the region
    filtered_data_NA = filter_data(df, "NA_Sales", genre, platform)
    filtered_data_EU = filter_data(df, "EU_Sales", genre, platform)
    filtered_data_JP = filter_data(df, "JP_Sales", genre, platform)
    filtered_data_Other = filter_data(df, "Other_Sales", genre, platform)

    sales_year_evolution_chart = px.scatter(filtered_data, x="Year", y="Price", title=f"Game sales timeline",
                                            hover_data=["Name", "Publisher", "Genre"])
    sales_year_evolution_chart.update_yaxes(title_text="Sales (in $)")
    # Mean game sales calculation
    mean_sales_NA = filtered_data_NA.groupby("Year")["NA_Sales"].mean().reset_index()
    mean_sales_EU = filtered_data_EU.groupby("Year")["EU_Sales"].mean().reset_index()
    mean_sales_JP = filtered_data_JP.groupby("Year")["JP_Sales"].mean().reset_index()
    mean_sales_Other = filtered_data_Other.groupby("Year")["Other_Sales"].mean().reset_index()

    sales_year_evolution_chart.add_scatter(x=mean_sales_NA["Year"], y=mean_sales_NA["NA_Sales"] * 10000000,
                                            mode="lines",
                                            name="North America", line=dict(color='gold'))
    sales_year_evolution_chart.add_scatter(x=mean_sales_EU["Year"], y=mean_sales_EU["EU_Sales"] * 10000000,
                                            mode="lines",
                                            name="Europe", line=dict(color='red'))
    sales_year_evolution_chart.add_scatter(x=mean_sales_JP["Year"], y=mean_sales_JP["JP_Sales"] * 10000000,
                                            mode="lines",
                                            name="Japan", line=dict(color='green'))
    sales_year_evolution_chart.add_scatter(x=mean_sales_Other["Year"], y=mean_sales_Other["Other_Sales"] * 10000000,
                                            mode="lines",
                                            name="Others", line=dict(color='blue'))

    region_names_to_keep = ["North America", "Europe", "Japan", "Others"]


    sales_year_evolution_chart.data = [trace for trace in sales_year_evolution_chart.data if
                                        trace.name in region_names_to_keep]

    sales_year_evolution_chart.update_layout(title_text = "Games sales timeline",
                                             title_x = 0.5)

    return sales_year_evolution_chart

@callback(
    Output('map_chart', 'figure'),
    [Input("region-dropdown", "value"),
     Input("genre-dropdown", "value"),
     Input("platform-dropdown", "value"),
     Input("year-dropdown", "value")]
)
def update_map_chart(region, genre, platform, year):
    NA_sales = get_sales(df, "NA", genre, platform, year)
    EU_sales = get_sales(df, "EU", genre, platform, year)
    JP_sales = get_sales(df, "JP", genre, platform, year)
    Other_sales = get_sales(df, "Other", genre, platform, year)
    world_map = {
        'data': [go.Scattermapbox(
            lat=
            [
                39.50,
                49.50,
                36.204824,
                20.593684
            ],
            lon=
            [
                -98.35,
                9.54,
                138.252924,
                78.96288
            ],
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=[
                    NA_sales * 1000,
                    EU_sales * 1000,
                    JP_sales * 1000,
                    Other_sales * 1000
                ],
                color='rgb(51, 141, 39)',
                colorscale='HSV',
                showscale=False,
                sizemode='area',
                opacity=0.7
            ),
            hoverinfo='text',
            hovertext=[
                "<b>North Amercia</b><br>" +
                "<b>Sales</b>: " + str(format_number(NA_sales * 10000000)) + "$<br>",
                "<b>Europe</b><br>" +
                "<b>Sales</b>: " + str(format_number(EU_sales * 10000000)) + "$<br>",
                "<b>Japan</b><br>" +
                "<b>Sales</b>: " + str(format_number(JP_sales * 10000000)) + "$<br>",
                "<b>Other countries</b><br>" +
                "<b>Sales</b>: " + str(format_number(Other_sales * 10000000)) + "$<br>"
            ]

        )],

        'layout': go.Layout(
            height=300,
            hovermode='x',
            paper_bgcolor='#010915',
            plot_bgcolor='#010915',
            margin=dict(r=0, l=0, b=0, t=0),
            mapbox=dict(
                accesstoken='pk.eyJ1IjoicXM2MjcyNTI3IiwiYSI6ImNraGRuYTF1azAxZmIycWs0cDB1NmY1ZjYifQ.I1VJ3KjeM-S613FLv3mtkw',
                center=go.layout.mapbox.Center(lat=46.8719, lon=6.5674),
                # style='open-street-map',
                zoom=1.2,
            ),
            autosize=True
        )
    }

    return world_map


@callback(
    Output("top10-global-sales", "figure"),
    [Input("region-dropdown", "value"),
     Input("genre-dropdown", "value"),
     Input("platform-dropdown", "value"),
     Input("year-dropdown", "value")]
)
def update_top10_global_sales(region, genre, platform, year):
    filtered_data = filter_data(df, region, genre, platform, year)
    region_name = global_sales_conversions.get(region, region)
    # Your code for updating the "top10-global-sales" figure
    best_selling_games = get_top_10_best_selling_games(filtered_data)
    best_selling_games_df = get_data_from_best_selling(filtered_data, best_selling_games)

    # top10 = filtered_data_v2.sort_values(region, ascending=False).head(20)
    shortened_names = [name[:30] + "..." if len(name) > 30 else name for name in best_selling_games_df["Name"]]
    top10_global_sales_chart = px.bar(best_selling_games_df, x=shortened_names, y=region,
                  hover_data=["Publisher", "Year", "Platform", "Genre"], color="Platform")
    top10_global_sales_chart.update_yaxes(title_text=f"{region_name} Sales (in $)")
    top10_global_sales_chart.update_xaxes(title_text="Game Name")
    top10_global_sales_chart.update_traces(y=best_selling_games_df[region] * 10000000)
    top10_global_sales_chart.update_layout(title=f"Best selling games in {region_name} for {genre} games")
    if platform != None:
        top10_global_sales_chart.update_layout(title=f"Region: {region_name}, Genre: {genre}, Platform: {platform}",
                                               title_x = 0.5)
    return top10_global_sales_chart

@callback(
    Output("metascore-vs-sales", "figure"),
    [Input("region-dropdown", "value"),
     Input("genre-dropdown", "value"),
     Input("platform-dropdown", "value"),
     Input("year-dropdown", "value")]
)
def update_metascore_vs_sales(region, genre, platform, year):
    filtered_data = filter_data(df, region, genre, platform, year)
    region_name = global_sales_conversions.get(region, region)
    filtered_data_metacritic = filtered_data[filtered_data["Metacritic score"] > 0]

    # Create the scatter plot
    metascore_vs_sales_chart = px.scatter(filtered_data_metacritic, x="Metacritic score", y=region,
                      hover_data=["Name", "Genre", "Publisher", "Year"],
                      # title=f"Metacritic Score vs. Global Sales for {genre} games"
                                          )
    metascore_vs_sales_chart.update_xaxes(title_text="Metacritic Score")
    metascore_vs_sales_chart.update_yaxes(title_text=f"{region_name} Sales (in $)")
    metascore_vs_sales_chart.update_traces(y=filtered_data_metacritic[region] * 10000000)
    # metascore_vs_sales_chart.update_layout(title_text = f"Metacritic Score vs. Global Sales for {genre} games",
    #                                        x_title = 0.5)


    return metascore_vs_sales_chart


