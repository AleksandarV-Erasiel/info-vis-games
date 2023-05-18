import dash
from dash import dcc
from dash import html
from dash import Input, Output
import plotly.express as px
import pandas as pd
import plotly.graph_objs as go
import plotly.io as pio
from plotly.subplots import make_subplots

# TODO: allow the user to choose year after/before/during (optional) 

# df = pd.read_csv("90_accuracy_dataset.csv")
df = pd.read_csv("without_1995_games.csv")

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

    # Group the DataFrame by game name and sum the sales
    grouped = df.groupby('Name')[['NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales', 'Global_Sales']].sum()

    # Sort the groups by the sum of their sales in descending order and get the top 10
    top_10 = grouped.sort_values('Global_Sales', ascending=False).head(10)

    # Return the top 10 as a list of tuples containing the game name and its total sales
    return list(top_10.index)

def get_data_from_best_selling(df, best_selling):
    # create an empty DataFrame to hold the top games sales data
    top_sales_df = pd.DataFrame(columns=df.columns)

    # loop through each game name in top_games
    for game_name in best_selling:
        # filter rows in df that match the current game name
        game_rows = df[df['Name'] == game_name]
        # append the filtered rows to top_sales_df
        top_sales_df = top_sales_df.append(game_rows, ignore_index=True)
        

    return top_sales_df

# Make the life easier
def get_sales(df, region, genre=None, platform=None, year=None):
    # Filter rows based on specified criteria
    filters = {'Genre': genre, 'Platform': platform, 'Year': year}
    for column, value in filters.items():
        if value and value != 'all':
            df = df.loc[df[column] == value]

    # Calculate sales for specified region
    sales_column = region + '_Sales'
    sales = df[sales_column].sum()

    return sales


def filter_data(df, region="NA_Sales", genre="Action", platform=None, year=None):
    # Filter data based on user input
    if genre != "all":
        filtered_df = df[df["Genre"] == genre]
    else:
        filtered_df = df
    
    if year is not None:
        filtered_df = filtered_df[filtered_df["Year"] == year]
    
    if platform and platform != "all":
        filtered_df = filtered_df[filtered_df["Platform"] == platform]
    
    # Keep only necessary columns
    columns_to_keep = ['Rank', 'Name', 'Platform', 'Year', 'Genre', 'Publisher', 'NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales', 'Global_Sales', 'name', 'Release date', 'Estimated owners', 'Peak CCU', 'Required age', 'Price', 'DLC count', 'About the game', 'Supported languages', 'Full audio languages', 'Reviews', 'Header image', 'Website', 'Support url', 'Support email', 'Windows', 'Mac', 'Linux', 'Metacritic score', 'Metacritic url', 'User score', 'Positive', 'Negative', 'Score rank', 'Achievements', 'Recommendations', 'Notes', 'Average playtime forever', 'Average playtime two weeks', 'Median playtime forever', 'Median playtime two weeks', 'Developers', 'Publishers', 'Categories', 'Genres', 'Tags', 'Screenshots', 'Movies']
    filtered_df = filtered_df[columns_to_keep]
    
    # Filter by region
    filtered_df = filtered_df[filtered_df[region] > 0]
    
    return filtered_df

# TODO: understand why it doesn't work when I'm putting it immediatly in the layout
platform_options = [{"label": "All Platforms", "value": "all"}] + \
    [{"label": platform, "value": platform} for platform in df["Platform"].unique()]

app = dash.Dash(__name__)

app.layout = html.Div([
    # Options
    html.Div([
        html.Div([
            html.Label('Select Region:', style={'font-weight': 'bold'}),
            dcc.Dropdown(
                id="region-dropdown",
                options=[
                    {"label": "North America", "value": "NA_Sales"},
                    {"label": "Europe", "value": "EU_Sales"},
                    {"label": "Japan", "value": "JP_Sales"},
                    {"label": "Other", "value": "Other_Sales"},
                    {"label": "Global", "value": "Global_Sales"},
                ],
                value="Global_Sales",
                style={'width': '200px', 'margin-left': '10px', 'margin-right': '10px'}
            ),
        ], style={'display': 'inline-block', 'vertical-align': 'top', 'width': '25%'}),
        
        html.Div([
            html.Label('Select Genre:', style={'font-weight': 'bold'}),
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
                ],
                value="all",
                style={'width': '200px', 'margin-left': '10px', 'margin-right': '10px'}
            ),
        ], style={'display': 'inline-block', 'vertical-align': 'top', 'width': '25%'}),
        
        html.Div([
            html.Label('Filter by Platform:', style={'font-weight': 'bold'}),
            dcc.Dropdown(
                id="platform-dropdown",
                options=platform_options,
                value=None,
                placeholder="All",
                style={'width': '200px', 'margin-left': '10px', 'margin-right': '10px'}
            ),
        ], style={'display': 'inline-block', 'vertical-align': 'top', 'width': '25%'}),
        
        html.Div([
            html.Label('Filter by Year:', style={'font-weight': 'bold'}),
            dcc.Dropdown(
                id="year-dropdown",
                options = [{"label": year, "value": year} for year in sorted(df["Year"].unique(), reverse=True) if pd.notnull(year)],
                value=None,
                placeholder="All",
                style={'width': '200px', 'margin-left': '10px', 'margin-right': '10px'}
            ),
        ], style={'display': 'inline-block', 'vertical-align': 'top', 'width': '25%'}),
    ], style={'border': '1px solid black', 'border-radius': '25px', 'padding-top': '10px', 'padding-bottom': '10px', 'padding-left': '20px', 'padding-right': '20px', 'margin-bottom': '2px'}),
    
    # Yearly time table
    html.Div([
        html.Div([
            dcc.Graph(id="sales-year-evolution"),
        ], style={'display': 'inline-block', 'width': '75%', 'vertical-align': 'top'}),
        html.Div([
            dcc.Checklist(
                id='checkbox-sales-year-evolution-show-scatter',
                options=[
                    # {'label': 'North America Sales', 'value': 'NA_Sales_Line'},
                    {'label': html.Div('North America Sales', style={'color': 'Gold'}), 'value': 'NA_Sales_Line'},
                    {'label': html.Div('Europe Sale', style={'color': 'Red'}), 'value': 'EU_Sales_Line'},
                    {'label': html.Div('Japan Sales', style={'color': 'Green'}), 'value': 'JP_Sales_Line'},
                    {'label': html.Div('Other Sales', style={'color': 'blue'}), 'value': 'Other_Sales_Line'},
                ],
                value=['NA_Sales_Line', 'EU_Sales_Line', 'JP_Sales_Line', 'Other_Sales_Line'],
                labelStyle={"display": "flex", "align-items": "center"},
            ),
            
            # Graphs
            html.Div([
                html.Div([
                    dcc.Graph(id = 'map_chart', config={'displayModeBar': 'hover'})
                ], style={'display': 'inline-block', 'width': '100%'}),
            ], style={'padding-top': '2px'}),
            
        ], style={'display': 'inline-block', 'width': '25%', 'vertical-align': 'top', 'padding-top': '4px'})
    ], style={'border': '1px solid black', 'border-radius': '25px', 'padding-top': '10px', 'padding-bottom': '10px', 'padding-left': '20px', 'padding-right': '20px', 'margin-bottom': '2px'}),
    
    html.Div([
        # html.Div([
        #     dcc.Graph(id="top10-global-sales"),
        # ], style={'display': 'inline-block', 'width': '50%', 'margin-top': '20px'}),
        html.Div([
            dcc.Graph(id="top10-regional-sales"),
        ], style={'display': 'inline-block', 'width': '50%', 'margin-top': '20px'}),
        html.Div([
            dcc.Graph(id="top5-publisher-decomp"),
        ], style={'display': 'inline-block', 'width': '50%', 'margin-top': '20px'}),
    ], style={'border': '1px solid black', 'border-radius': '25px', 'padding-top': '10px', 'padding-bottom': '10px', 'padding-left': '20px', 'padding-right': '20px', 'margin-bottom': '2px'}),

    html.Div([
        html.Div([
            dcc.Graph(id="metascore-vs-sales"),
        ], style={'display': 'inline-block', 'width': '50%', 'margin-top': '20px'}),
        html.Div([
            html.Div([
                dcc.Graph(id="prices-year-evolution"),
            ]),
            dcc.Checklist(
                id='checkbox-game-price-evolution',
                options=[{'label': 'Show scatter details', 'value': 'scatter'}],
                value=['scatter'],
                labelStyle={'display': 'inline-block', 'margin-right': '10px'}
            ),
        ], style={'display': 'inline-block', 'width': '50%', 'margin-top': '20px'}),        
    ], style={'border': '1px solid black', 'border-radius': '25px', 'padding-top': '10px', 'padding-bottom': '10px', 'padding-left': '20px', 'padding-right': '20px', 'margin-bottom': '2px'}),
    
    html.Div([
        dcc.Graph(id="subplot-test")
    ], style={'border': '1px solid black', 'border-radius': '25px', 'padding-top': '10px', 'padding-bottom': '10px', 'padding-left': '20px', 'padding-right': '20px', 'margin-bottom': '2px'})


], style={'font-family': 'Arial, sans-serif', 'margin': 'auto', 'max-width': '100%', 'height': '100%', 'padding': '20px'})

@app.callback(
    [
        # Output("top10-global-sales", "figure"),
        Output("top10-regional-sales", "figure"),
        # Output("top5-publisher-full", "figure"),
        Output("top5-publisher-decomp", "figure"),
        Output("sales-year-evolution", "figure"),
        Output("metascore-vs-sales", "figure"),
        Output("prices-year-evolution", "figure"),
        Output("subplot-test", "figure"),
        Output('map_chart', 'figure'),
        # Output("map_analyze_chart", "figure")
    ],
    [
        Input("region-dropdown", "value"),
        Input("genre-dropdown", "value"),
        Input("platform-dropdown", "value"),
        Input("year-dropdown", "value"),
        Input("checkbox-sales-year-evolution-show-scatter", "value"),
        Input("checkbox-game-price-evolution", "value"),
    ]
)
def update_figures(region, genre, platform, year, checkbox_sales_year_evolution, checkbox_price_year_evolution): 
    if region is None:
        region = "NA_Sales"  # set default value
    if genre is None:
        genre = "Action"  # set default value
    region_name = global_sales_conversions.get(region, region)

    filtered_data_v2 = filter_data(df, region, genre, platform, year)
    NA_sales = get_sales(df, "NA", genre, platform, year)
    EU_sales = get_sales(df, "EU", genre, platform, year)
    JP_sales = get_sales(df, "JP", genre, platform, year)
    Other_sales = get_sales(df, "Other", genre, platform, year)
            
    # Group by name and sum the sales for the selected year
    grouped = filtered_data_v2.groupby("Name").sum(numeric_only=True)

    # Sort the groups by the selected region's sales, and select the top 10 games
    top10_games = grouped.sort_values(region, ascending=False).head(10)

    # Create the plot
    # fig1 = px.bar(top10_games, x=top10_games.index, y=region,
    #             hover_data=["Metacritic score", "Positive", "Negative", "Average playtime forever", "Median playtime forever"],
    #             title=f"Top 10 Games (Every platform combined) by {region_name} Sales for {genre} games in {year}")
    # fig1.update_yaxes(title_text="Sales (in $)")
    # fig1.update_traces(y=top10_games[region]*10000000)
    
    best_selling_games = get_top_10_best_selling_games(filtered_data_v2)
    best_selling_games_df = get_data_from_best_selling(filtered_data_v2, best_selling_games)
    
    # top10 = filtered_data_v2.sort_values(region, ascending=False).head(20)
    shortened_names = [name[:30] + "..." if len(name) > 30 else name for name in best_selling_games_df["Name"]]
    fig2 = px.bar(best_selling_games_df, x=shortened_names, y=region, hover_data=["Publisher", "Year", "Platform", "Genre"], color="Platform")
    fig2.update_yaxes(title_text=f"{region_name} Sales (in $)")
    fig2.update_xaxes(title_text="Game Name")
    fig2.update_traces(y=best_selling_games_df[region]* 10000000)
    fig2.update_layout(title=f"Best selling games in {region_name} for {genre} games")
    if platform != None :
        fig2.update_layout(title=f"Best selling games in {region_name} for {genre} games on {platform}")
    # fig2.update_yaxes(title_text="Regional Sales (in $ $)")

    # Update top 5 publishers by region figure
    
    # top5 = filtered_data_v2.groupby("Publisher")[region].sum(numeric_only=True).sort_values(ascending=False).head(5)
    # fig3 = px.bar(top5, x=top5.index, y=top5.values*10000000, title="Best Gaming Studios By Region")
    # fig3.update_traces(hovertemplate='%{x}: $%{y:.2s}')
    # fig3.update_yaxes(title_text=f"{region_name} Sales (in $)")
    # fig3.update_layout(title=f"Top 5 Publishers in {region_name}", yaxis_title="Total Sales", xaxis_title="Publisher")
    
    # Update top 5 publishers by region figure
    top5_publishers = filtered_data_v2.groupby("Publisher")[region].sum(numeric_only=True).sort_values(ascending=False).head(5)
    top5_games = filtered_data_v2[filtered_data_v2['Publisher'].isin(top5_publishers.index)]
    top5_games[region] = top5_games[region] * 10000000
    fig4 = px.bar(top5_games, x="Publisher", y=region, hover_name="Name", title="Best Gaming Studios By Region", hover_data=["Publisher", "Year", "Platform", "Genre"])
    fig4.update_yaxes(title_text=f"{region_name} Sales (in $)")
    fig4.update_layout(
        title=f"Top 5 Publishers in {region_name} (Decomposed)",
        yaxis_title="Total Sales (in $)",
        xaxis_title="Publisher",
        height=500  # Set the desired height value (in pixels)
    )

    filtered_data_metacritic = filtered_data_v2[filtered_data_v2["Metacritic score"] > 0]

    # Create the scatter plot
    fig6 = px.scatter(filtered_data_metacritic, x="Metacritic score", y=region,
                    hover_data=["Name", "Genre", "Publisher", "Year"],
                    title=f"Metacritic Score vs. Global Sales for {genre} games")
    fig6.update_xaxes(title_text="Metacritic Score")
    fig6.update_yaxes(title_text=f"{region_name} Sales (in $)")
    fig6.update_traces(y=filtered_data_metacritic[region]*10000000)
    
    ##################################
    
    # Mean game price calculation
    mean_prices = filtered_data_v2.groupby("Year")["Price"].mean().reset_index()
    
    fig7 = px.scatter(filtered_data_v2, x="Year", y="Price", title=f"Game sales for {genre} games on {platform} in {region_name}", hover_data=["Name", "Publisher", "Genre", "Platform"])
    fig7.update_yaxes(title_text="Price (in $)")
    fig7.add_scatter(x=mean_prices["Year"], y=mean_prices["Price"], mode="lines", name=f"{region_name}", showlegend = False, line=dict(color='red'))
    
    if 'scatter' in checkbox_price_year_evolution:
        pass
    else:
        fig7.data = [trace for trace in fig7.data if trace.name == f"{region}"]
        
        
    # Multiply values in the "region" column by a million
    filtered_data_subplot = filtered_data_v2
    filtered_data_subplot[region] *= 1000000
    
    # Create the scatter matrix graph with updated values and title
    fig = px.scatter_matrix(filtered_data_subplot, dimensions=["Metacritic score", region, "Price"])

    # Update the layout and axes matches
    fig.update_layout(
        xaxis={"matches": "y"},
        xaxis2={"matches": "y2"},
        xaxis3={"matches": "y3"},
        yaxis={"matches": "x"},
        yaxis2={"matches": "x2"},
        yaxis3={"matches": "x3"},
    )
        
    fig.update_traces(selected=dict(marker=dict(color='red')), unselected=dict(marker=dict(color='blue')))
    # fig.update_traces(hover_data=["Name", "Publisher", "Genre", "Platform", "Year"])
    
# Set hovertemplate for each trace
    hovertemplate = "Metacritic score: %{x}<br>" + region + \
                    "Name: %{text[0]}<br>Publisher: %{text[1]}<br>Genre: %{text[2]}<br>Year: %{text[3]}"
    for trace in fig.data:
        trace.hovertemplate = hovertemplate
        trace.text = filtered_data_subplot[["Name", "Publisher", "Genre", "Year"]]
    
    # Filtered Data accordingly to the region
    filtered_data_NA = filter_data(df, "NA_Sales", genre, platform)
    filtered_data_EU = filter_data(df, "EU_Sales", genre, platform)
    filtered_data_JP = filter_data(df, "JP_Sales", genre, platform)
    filtered_data_Other = filter_data(df, "Other_Sales", genre, platform)
    
    fig5 = px.scatter(filtered_data_v2, x="Year", y="Price", title=f"Game sales timeline", hover_data=["Name", "Publisher", "Genre"])
    fig5.update_yaxes(title_text="Sales (in $)")
    # Mean game sales calculation
    mean_sales_NA = filtered_data_NA.groupby("Year")["NA_Sales"].mean().reset_index()
    mean_sales_EU = filtered_data_EU.groupby("Year")["EU_Sales"].mean().reset_index()
    mean_sales_JP = filtered_data_JP.groupby("Year")["JP_Sales"].mean().reset_index()
    mean_sales_Other = filtered_data_Other.groupby("Year")["Other_Sales"].mean().reset_index()
    
    if 'NA_Sales_Line' in checkbox_sales_year_evolution:
        fig5.add_scatter(x=mean_sales_NA["Year"], y=mean_sales_NA["NA_Sales"]*10000000, mode="lines", name=f"{region_name}", showlegend = False, line=dict(color='gold'))
    if 'EU_Sales_Line' in checkbox_sales_year_evolution:
        fig5.add_scatter(x=mean_sales_EU["Year"], y=mean_sales_EU["EU_Sales"]*10000000, mode="lines", name=f"{region_name}", showlegend = False, line=dict(color='red'))
    if 'JP_Sales_Line' in checkbox_sales_year_evolution:
        fig5.add_scatter(x=mean_sales_JP["Year"], y=mean_sales_JP["JP_Sales"]*10000000, mode="lines", name=f"{region_name}", showlegend = False, line=dict(color='green'))
    if 'Other_Sales_Line' in checkbox_sales_year_evolution:   
        fig5.add_scatter(x=mean_sales_Other["Year"], y=mean_sales_Other["Other_Sales"]*10000000, mode="lines", name=f"{region_name}", showlegend = False, line=dict(color='blue'))

    if 'scatter' in checkbox_sales_year_evolution:
        pass
    else:
        fig5.data = [trace for trace in fig5.data if trace.name == f"{region_name}"]
    
    world_map = {
        'data': [go.Scattermapbox(
            lat=
            [
                48.1667,
                54.5260,
                36.2048,
                44.0479
            ],
            lon=
            [
                -100.1667,
                15.2551,
                138.2529,
                100.6197
            ],
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=[
                    NA_sales*15,
                    EU_sales*15,
                    JP_sales*15,
                    Other_sales*15
                ],
                color='rgb(51, 141, 39)',
                colorscale='HSV',
                showscale=False,
                sizemode='area',
                opacity=0.7
            ),
            hoverinfo='text',
            hovertext= [
                "<b>North Amercia</b><br>" +
                "<b>Sales</b>: " + str(format_number(NA_sales*10000000)) + "$<br>",
                "<b>Europe</b><br>" +
                "<b>Sales</b>: " + str(format_number(EU_sales*10000000)) + "$<br>", 
                "<b>Japan</b><br>" +
                "<b>Sales</b>: " + str(format_number(JP_sales*10000000)) + "$<br>", 
                "<b>Other countries</b><br>" +
                "<b>Sales</b>: " + str(format_number(Other_sales*10000000)) + "$<br>"
            ]

        )],

        'layout': go.Layout(
            height=300,
            hovermode='x',
            paper_bgcolor='#010915',
            plot_bgcolor='#010915',
            margin=dict(r=0, l =0, b = 0, t = 0),
            mapbox=dict(
                accesstoken='pk.eyJ1IjoicXM2MjcyNTI3IiwiYSI6ImNraGRuYTF1azAxZmIycWs0cDB1NmY1ZjYifQ.I1VJ3KjeM-S613FLv3mtkw',
                center = go.layout.mapbox.Center(lat=40.8719, lon=6.5674),
                # style='open-street-map',
                zoom=0.0,
            ),
            autosize=True
        )
    }
    
    ##############################################################################################################
    
#this code defines the scattermapbox. more info can be seen here: https://plotly.com/python/scattermapbox/
    return fig2, fig4, fig5, fig6, fig7, fig, world_map

if __name__ == "__main__":
    app.run_server(debug=True)

