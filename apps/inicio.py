from app import app

from dash import html
import dash_bootstrap_components as dbc

#---------------------------------------------------------------
#Page layout
layout = html.Div([
            #Title
            dbc.Row([
                dbc.Col([
                    html.H1("Bienvenidos al radar de competitividad", style={"textAlign":"center"}),
                ], width=12)
            ]),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.Img(src=app.get_asset_url('logo_procolombia.png'), height="80px", id="imagenes-entrada"),
                    html.Img(src=app.get_asset_url('logo_fabricas.png'), height="80px", id="imagenes-entrada")
                ], width=12,style={"textAlign":"center"})
            ]),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.Img(src=app.get_asset_url('logo.svg'), height="150px", id="imagenes-entrada"),
                ], width=12,style={"textAlign":"center"})
            ]),
            html.Br(),
            dbc.Row([
                dbc.Col([dbc.Button("Llévame al radar 🐱‍👤", href="/apps/radar")],sm=12,md=4,style={"margin-bottom":"20px"}),
                dbc.Col([dbc.Button("Quiero ver el modelo 🐱‍👓", href="/apps/model")],sm=12,md=4,style={"margin-bottom":"20px"}),
                dbc.Col([dbc.Button("Quiénes hicieron esto 👩‍👩‍👧‍👧", href="/apps/disclaimer")],sm=12,md=4)
            ],style={"textAlign":"center","width":"90%","justify-content":"space-around",}
            ),
          ], style={"background": "#141138","color":"white","overflow-x": "hidden", "min-height":"100vh", "min-width":"100vw","textAlign":"center",         
                    "display":"flex","flex-direction":"column","justify-content":"center","align-items":"center","margin":"auto"}
        )

