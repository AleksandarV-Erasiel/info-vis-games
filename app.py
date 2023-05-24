import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.SPACELAB],
                meta_tags=[{'name': 'viewport','content': 'width=device-width, initial-scale=1.0'}

                           ])

sidebar = dbc.Nav(
            [
                dbc.NavLink(
                    [
                        html.Div(page["name"], className="ms-2"),
                    ],
                    href=page["path"],
                    active="exact",
                )
                for page in dash.page_registry.values()
            ],
            vertical=False,
            pills=True,
            className="bg-dark",
            fill=True,
)

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.Div("Python Multipage App with Dash",
                         style={'fontSize':50, 'textAlign':'center'}))
    ]),

    #html.Hr(),

    dbc.Row([
            dbc.Col(
                [
                    sidebar
                ], align="end", xs=2, sm=2, md=2, lg=2, xl=2, xxl=2),
            ], justify="start"
            ),

    html.Hr(),

    dbc.Row([
        dbc.Col(
            [
                dash.page_container
            ], xs=8, sm=8, md=10, lg=10, xl=10, xxl=10)
        ], justify='center')
], fluid=True)


if __name__ == "__main__":
    app.run_server(debug=True)
