from app import app

from dash import html, dcc
import dash_bootstrap_components as dbc
from apps import navbar

#---------------------------------------------------------------
#Page layout
layout = html.Div([
            navbar.navbar,
            #Title
            dbc.Row([
                dbc.Col([
                    html.H1("App desarrollada por el Equipo 235 de DS4A Cohorte 6", style={"textAlign":"center"})
                ], width=12)
            ]),
            html.Br(),
            #Carousel showing the team names
            dbc.Row([
                dbc.Col([
                    dbc.Carousel(
                        items=[
                            {"key": "1", "src": "/assets/Bibiana.svg", "header": "Bibiana Robles: Lideresa del grupo. Mágister en gestión de proyectos", 
                            "img_style":{"max-height":"500px","opacity":"0.8"}},
                            {"key": "2", "src": "/assets/Hugo.svg", "header":"Hugo Mercado: Back-end. Ingeniero mecánico",
                            "img_style":{"max-height":"500px","opacity":"0.8"}},
                            {"key": "3", "src": "/assets/Danny.svg", "header":"Danny Rivera: Modelación. Mágister en estadística",
                            "img_style":{"max-height":"500px","opacity":"0.8"}},
                            {"key": "4", "src": "/assets/David.svg", "header":"David Ortega: Análisis. Matemático",
                            "img_style":{"max-height":"500px","opacity":"0.8"}},
                            {"key": "5", "src": "/assets/Alex.svg", "header":"Alex Lavao: Analista de Datos. Ingeniero mecánico",
                            "img_style":{"max-height":"500px","opacity":"0.8"}},
                            {"key": "6", "src": "/assets/Alejo.svg", "header":"Alejandro Lagos: Encargado del Front-end. ", 
                            "img_style":{"max-height":"500px","opacity":"0.8"}},
                            {"key": "7", "src": "/assets/Kelly.svg", "header":"Kelly Duque: Documentación. Ingeniera industrial",
                            "img_style":{"max-height":"500px","opacity":"0.8"}},
                            {"key": "8", "src": "/assets/Daniel.svg", "header":"Daniel Rubiano: Documentación. Ingeniero industrial",
                            "img_style":{"max-height":"500px","opacity":"0.8"}},
                        ],
                        controls=True,
                        indicators=True,
                        interval=2000,
                        ride="carousel",
                       className="carousel-dark"
                    )
                ], width=8)
            ], justify="center"),
            #Contacto en linkedin
            html.Div([
                dcc.Markdown(
                    '''
                    ##### Contáctenos en ![](../assets/linkedin.svg)
                    [__Bibiana Robles__](https://www.linkedin.com/in/bibiana-robles-26b14317/) |
                    [__Danny Rivera__](https://www.linkedin.com/in/danny-rivera-0b506718a/) | 
                    [__Hugo Mercado__](http://www.linkedin.com/in/hugo-mercado06/) | 
                    [__Alejandro Lagos__](https://www.linkedin.com/in/alejandrolagos1/) |
                    [__David Ortega__](https://www.linkedin.com/in/david-alejandro-ortega-bonilla-27b5a9143) |
                    [__Alex Lavao__](www.linkedin.com/in/alex-andrey-lavao-pastrana-95388371) |
                    [__Daniel Rubiano__](https://www.linkedin.com/in/darubiano/) |
                    [__Kelly Duque__](https://www.linkedin.com/in/kelly-andrea-duque-moreno-5499ab93) |
                    '''
                    )],style={"font-size":"16px","align-text":"right"}),
            #Special thanks and disclaimer
            dbc.Row([
                html.H4("Agradecimientos especiales al equipo de Procolombia, y a los TA de DS4A Rodolfo Meza y Diana Rodríguez.",
                style={"textAlign":"center","marginTop":"20px"}),
                html.H6("Proyecto desarrollado únicamente con fines educativos"),
            ]),
          ], style={"background": "white","margin":"0","overflow-x": "hidden", "min-height":"100vh", "min-width":"100vw","textAlign":"center"}
        )

