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

top5_games = None


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

dash.register_page(__name__, name='Reviews')


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

    #This is for the best selling games and top 5 publishers
    dbc.Row([
        dbc.Col([
            html.H1("Top 5 Publishers",
                    className='text-center bg-dark text-white'),

            dcc.Graph(id="top5-publisher-decomp")
            ], width={"size": 5}, align="center"),
    ], justify="center", className="py-lg-3 py-xl-3"),

    #This is for the metacritic score vs sales and games prices
    dbc.Row([
        dbc.Col([
            html.H1("Best Publisher Games - Positive VS Negative",
                    className='bg-dark text-white'),

            dcc.Graph(id="top5-games-reviews")
        ], width={"size": 5}),

        dbc.Col([
            html.H1("Best Publisher Games - Average playtime forever",
                    className='bg-dark text-white'),

            dcc.Graph(id="top5-max-playtime")
        ], width={"size": 5}),

    ], justify="center", className="py-lg-3 py-xl-3")

], fluid=True)

@callback(
    Output("top5-publisher-decomp", "figure"),
    [Input("region-dropdown", "value"),
     Input("genre-dropdown", "value"),
     Input("platform-dropdown", "value"),
     Input("year-dropdown", "value")]
)
def update_top5_publisher_decomp(region, genre, platform, year):
    filtered_data = filter_data(df, region, genre, platform, year)
    region_name = global_sales_conversions.get(region, region)

    # Update top 5 publishers by region figure
    top5_publishers = filtered_data.groupby("Publisher")[region].sum(numeric_only=True).sort_values(
        ascending=False).head(5)
    top5_games = filtered_data[filtered_data['Publisher'].isin(top5_publishers.index)]
    top5_games[region] = top5_games[region] * 10000000
    top5_publishers_chart = px.bar(top5_games, x="Publisher", y=region, hover_name="Name", title="Best Gaming Studios By Region",
                                   hover_data=["Publisher", "Year", "Platform", "Genre"])
    top5_publishers_chart.update_yaxes(title_text=f"{region_name} Sales (in $)")
    top5_publishers_chart.update_layout(
        title=f"Region: {region_name} (Decomposed)",
        yaxis_title="Total Sales (in $)",
        xaxis_title="Publisher",
        title_x = 0.5,
        # height=00  # Set the desired height value (in pixels)
    )

    return top5_publishers_chart

@callback(
    Output("top5-games-reviews", "figure"),
    [Input("region-dropdown", "value"),
     Input("genre-dropdown", "value"),
     Input("platform-dropdown", "value"),
     Input("year-dropdown", "value")]
)
def update_top5_games_reviews(region, genre, platform, year):
    filtered_data = filter_data(df, region, genre, platform, year)
    region_name = global_sales_conversions.get(region, region)

    # Update top 5 publishers by region figure
    top5_publishers = filtered_data.groupby("Publisher")[region].sum(numeric_only=True).sort_values(ascending=False).head(5)
    top5_games = filtered_data[filtered_data['Publisher'].isin(top5_publishers.index)]
    top5_games[region] = top5_games[region] * 10000000
    
    top5_games_positive = top5_games[top5_games["Positive"].notna()]
    top5_games_negative = top5_games[top5_games["Negative"].notna()]
    
    top5_games_reviews_chart = go.Figure()
    top5_games_reviews_chart.add_trace(go.Bar(x=top5_games_positive["Name"], y=top5_games_positive["Positive"], name="Positive", orientation="v", marker_color="green"))
    top5_games_reviews_chart.add_trace(go.Bar(x=top5_games_negative["Name"], y=top5_games_negative["Negative"], name="Negative", orientation="v", marker_color="red"))

    top5_games_reviews_chart.update_layout(barmode="overlay")
    top5_games_reviews_chart.update_layout(title_text="Positive VS Negative reviews for best publishers games")
    top5_games_reviews_chart.update_xaxes(title_text="Game Name")
    top5_games_reviews_chart.update_yaxes(title_text="Number of reviews")

    return top5_games_reviews_chart

@callback(
    Output("top5-max-playtime", "figure"),
    [Input("region-dropdown", "value"),
     Input("genre-dropdown", "value"),
     Input("platform-dropdown", "value"),
     Input("year-dropdown", "value")]
)
def update_top5_max_playtime(region, genre, platform, year):
    filtered_data = filter_data(df, region, genre, platform, year)
    region_name = global_sales_conversions.get(region, region)

    # Update top 5 publishers by region figure
    top5_publishers = filtered_data.groupby("Publisher")[region].sum(numeric_only=True).sort_values(ascending=False).head(5)
    top5_games = filtered_data[filtered_data['Publisher'].isin(top5_publishers.index)]
    top5_games[region] = top5_games[region] * 10000000
    
    top5_games_max_playtime = top5_games[top5_games["Average playtime forever"].notna()]
    
    top5_games_max_playtime_chart = px.bar(top5_games_max_playtime, x=top5_games_max_playtime["Name"], y=top5_games_max_playtime["Average playtime forever"])
    top5_games_max_playtime_chart.update_layout(title_text="Average playtime forever for best publishers games")
    top5_games_max_playtime_chart.update_xaxes(title_text="Game Name")
    top5_games_max_playtime_chart.update_yaxes(title_text="Number of hours")
    
    return top5_games_max_playtime_chart
