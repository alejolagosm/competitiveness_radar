import dash_bootstrap_components as dbc
from dash import html
from app import app
from dash.dependencies import Input, Output, State

#Navbar component for the pages
navbar = dbc.Navbar(
            dbc.Row([
                dbc.Col(dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),sm=12,md=1),
                dbc.Col([
                    dbc.Collapse([
                        html.Img(src=app.get_asset_url('logo_procolombia.png'), height="40px"),
                        html.Img(src=app.get_asset_url('logo_fabricas.png'), height="40px"),
                        html.Img(src=app.get_asset_url('logo.svg'), height="40px"),
                        dbc.Nav([
                            dbc.NavItem(dbc.NavLink("Radar", href="/apps/radar")),
                            dbc.NavItem(dbc.NavLink("Modelo", href="/apps/model")),
                            dbc.NavItem(dbc.NavLink("Créditos", href="/apps/disclaimer")),
                            ],),
                        ],
                        id="navbar-collapse",
                        is_open=False,
                        navbar=True,
                        style={"justify-content":"space-around","align-items":"center"},
                    )], sm = 12, md=10, style={"text-align":"center"},
                ),     
                ],
                style={"width":"90%"}
            ),
    color="#141138",
    dark=True
)

#Function to make the responsive menu in small screens
@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open