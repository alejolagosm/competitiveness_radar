import pandas as pd
import plotly.express as px
import pathlib
from app import app

import dash 
from dash import dcc
from dash import html
from dash import dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from apps import navbar
from apps import cluster

#---------------------------------------------------------------
# Data Loading
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("../data").resolve()
# Loading Country-level Data
df_paises = pd.read_csv(DATA_PATH.joinpath("df_indices_paises.csv"),sep=";")
rename_cat={'iso3':"iso3", 'nombre':"Nombre_pais",'epi':"Sostenibilidad/EPI", 
            'innovacion':"Innovación", 'competitividad':"Competitividad",'distancia':"Distancia"}
df_paises.rename(columns=rename_cat, inplace=True)
# Loading product-level Data
df_productos = pd.read_csv(DATA_PATH.joinpath('df_productos.csv'),dtype={'producto': str})
df_relaciones_productos = pd.read_csv(DATA_PATH.joinpath("relaciones_productos.csv"),sep=";")
df_relaciones_productos["label_productos"] = df_relaciones_productos["producto"] + "-" + df_relaciones_productos["desc_producto"]
lista_sectores = sorted(df_relaciones_productos["sector"].unique()) + ["Todos"]

#---------------------------------------------------------------
#Page layout
layout = html.Div([
        navbar.navbar,
        #Title
        dbc.Row([html.H1("Modelo de Clusterización", style={'textAlign':'center',"margin-top":"16px"}),html.Hr()],
                style={"max-width":"1200px","margin":"auto"}
                ),
        #Options to generate the model
        dbc.Row([
            html.Label(['Elija una opción para generar el modelo'],style={'font-weight': 'bold'}),
            dcc.RadioItems(
                id='radar_choice',
                options=[
                         {'label': 'V1: Empresario conservador', 'value': 'Competitividad'},
                         {'label': 'V2: Emprendedor arriesgado', 'value': 'Oportunidad'},
                ],
                value='Competitividad',
            ),
        ],style={'textAlign':'center',"margin-top":"10px"}),
        #Model inputs
        dbc.Row(html.P("Elija un producto para generar resultados. En el mapa, consulte los índices que generan los modelos",
                    style={'textAlign':'center',"margin-top":"16px"})
        ),
        dbc.Row([
                #The first column has all the product-related dropdowns, since this is the main input of the user
                dbc.Col([
                    html.Div([
                        html.H5("Elija un producto para realizar el modelo", style={'textAlign':'center'}),
                        html.Label("Filtre por sector", style={'fontSize':20, 'textAlign':'center'}),
                        dcc.Dropdown(
                            id='sec_cluster',
                            options=[{'label': s, 'value': s} for s in lista_sectores],
                            value="Todos",
                            clearable=False,

                        ),
                        html.Label("Filtre por subsector", style={'fontSize':20, 'textAlign':'center'}),
                        dcc.Dropdown(
                            id='subsec_cluster', 
                            options=[]
                        ),
                        html.Label("Seleccione un producto", style={'fontSize':25, 'textAlign':'center'}),
                        dcc.Dropdown(
                            id='producto_cluster',
                            options=[],
                            value='090111',
                            clearable=False,
                        ),
                    ]),
                    ], sm=12, lg = 6, align="center",style={'margin': 'auto'}
                ),
                #The second column is a visualization complementary map for the user to see the indexes that are used for the clusterization models
                dbc.Col([
                    html.Div([
                        html.Label(['Ver parámetro de entrada:'],style={'font-weight': 'bold', "text-align": "center"}),
                        dcc.Dropdown(id='input_index',
                            options=[], optionHeight=35, 
                            disabled=False, multi=False, 
                            searchable=True, search_value='', 
                            clearable=False, style={'width':"100%"},),
                        ]),
                        dbc.Spinner(children=[dcc.Graph(id='index_map', style={'display': 'grid', "place-content":"center"})], 
                                    size="lg", color="#B51F1F", type="border"
                                )
                    ], sm=12, lg = 6, align="center",style={'margin': 'auto'}
                )
            ],
            style={"max-width":"1200px","display":"flex","justify-content":"center", "margin":"auto", "textAlign":"center"}
        ),

        dbc.Row([html.H1("Resultados", style={'textAlign':'center'}), html.Hr()],
                style={"max-width":"1200px","margin":"auto"}
                ),
        #This is a summary of the model used
        dbc.Row(html.P(id="model-explanation", style={'textAlign':'center',"margin-top":"16px"})),
        #Main results of the model shown as an animated map
        dbc.Row(
            dbc.Spinner(children=[dcc.Graph(id="clusters_graph")], 
                        size="lg", color="#B51F1F", type="border"
                    ),
            style={"max-width":"1200px","margin":"auto","textAlign":"center","justify-content":"center", "align-items":"center",}
        ),
        #Radar plot that summarizes average scores for each index
        dbc.Row([
            html.H2("Radar promedio para cada clúster", style={'textAlign':'center'}),
            html.P("En general, los mejores clústers para exportar el producto tendrán los puntajes más altos en sus índices", style={'textAlign':'center'}),
            dbc.Spinner(children=[dcc.Graph(id="radar_clusters")], size="lg", color="#B51F1F", type="border"),
            ],
            style={"max-width":"1200px","margin":"auto","textAlign":"center","justify-content":"center", "align-items":"center",}
        ),
        #Summary table for the clustering model
        dbc.Row([
            html.H2("Tabla de resumen", style={'textAlign':'center'}),
            html.Div(id="results_tableCluster"),
            ],
            style={"max-width":"80%","overflow-x":"scroll", "margin":"auto", "textAlign":"center", "justify-content":"center", "align-items":"center",}
        ),
        dbc.Row([html.H1("Resumen por regiones", style={'textAlign':'center',"margin-top":"16px"}),html.Hr()],
                style={"max-width":"1200px","margin":"auto"}
                ),
        dbc.Row(html.P("Esta gráfica muestra como se dividen los países de cada región en cada cluster", style={'textAlign':'center',"margin-top":"16px"})),
        #The sankey graph relating the regions with the clusters
        dbc.Row([
            dcc.Graph(id="sankey_graph"),
            ],
            style={"max-width":"1200px","margin":"auto","textAlign":"center","justify-content":"center", "align-items":"center",}
        ),
        
  ], style={"background": "white","margin":"0", "min-height":"100vh",}
)

#---------------------------------------------------------------
#Callback Functions
# Populate the options of subsectors dropdown based on sectors dropdown
@app.callback(
    [Output('subsec_cluster', 'disabled'),
   Output('subsec_cluster', 'options')],
    Input('sec_cluster', 'value')
)
def set_subsectores_options(chosen_sector):
    if chosen_sector=="Todos":
        return True, []
    else:
        dff = df_relaciones_productos[df_relaciones_productos["sector"]==chosen_sector]
        return False, [{'label': c, 'value': c} for c in sorted(dff["subsector"].unique())]

# Populate values of products dropdown based on subsectors selection or give entire products list
@app.callback(
   [Output('producto_cluster', 'value'),
   Output('producto_cluster', 'options')],
    Input('subsec_cluster', 'value')
)
def set_productos_options(chosen_subsector):
    if chosen_subsector is None:
        return "090111", [{'label': c, 'value': c[:6]} for c in sorted(df_relaciones_productos["label_productos"])]
    else:
        dff = df_relaciones_productos[df_relaciones_productos["subsector"]==chosen_subsector]
        return "090111", [{'label': c, 'value': c[:6]} for c in sorted(dff["label_productos"])]

# Populate values of variables dropdown based on the radar version
@app.callback(
   [Output('input_index', 'value'),
   Output('input_index', 'options')],
    Input('radar_choice', 'value')
)
def set_productos_options(radar_choice):
    #Depending on the radar choice, the index map dropdown gets updated
    if radar_choice == "Competitividad":
        return "Arancel", [{'label': 'EPI', 'value': 'Sostenibilidad/EPI'}, {'label': 'Innovación', 'value': 'Innovación'},
                                  {'label': 'Competitividad', 'value': 'Competitividad'}, {'label': 'Distancia', 'value': 'Distancia'},
                                  {'label': 'Arancel', 'value': 'Arancel'}, {'label': 'Demanda', 'value': 'Demanda'}]
    else:
        return "Arancel", [{'label': 'Desarrollo', 'value': 'Desarrollo'}, {'label': 'Sostenibilidad', 'value': 'Sostenibilidad'},
                              {'label': 'Oportunidad', 'value': 'Oportunidad'}, {'label': 'Arancel', 'value': 'Arancel'},
                              {'label': 'Demanda', 'value': 'Demanda'}]

# Updating the indexes map based on the option selected by the user
@app.callback(
    Output(component_id='index_map', component_property='figure'),
    [Input(component_id='input_index', component_property='value'),
    Input(component_id='producto_cluster', component_property='value')]
)
def build_graph(plot_option, product_selected):
    #Adding the tariff and demand score columns based on the product selected
    dff=df_paises.copy()
    dff_prod = df_productos.loc[(df_productos["producto"] == product_selected), ["iso3","Demanda","Arancel"]]
    df_joined = pd.merge(dff, dff_prod, on='iso3', how='left')
    #Setting the color scales for the map
    colors_scale = px.colors.diverging.RdYlGn
    #Creating the cloropleth map based on the dropdown option selected and updating its format
    fig = px.choropleth(df_joined, locations="iso3",
                            color=plot_option,
                            hover_name="Nombre_pais",
                            projection='natural earth',
                            title=f"Índice de {plot_option}",
                            color_continuous_scale=colors_scale)
    fig.update_geos(projection_type="orthographic",showocean=True, oceancolor="LightBlue",)
    fig.update_layout(height=600, width=600, title=dict(font=dict(size=28),x=0.5,xanchor='center'), geo=dict(bgcolor= 'rgba(0,0,0,0)'))
                    
    return fig

#Do clustering model with the product and number of clusters, output cloropleth map, sankey graph and summary table
@app.callback(
    [Output(component_id='results_tableCluster', component_property='children'),
    Output(component_id='clusters_graph', component_property='figure'),
    Output(component_id='radar_clusters', component_property='figure'),
     Output(component_id='sankey_graph', component_property='figure'),
     Output(component_id='model-explanation', component_property='children')],
     [Input(component_id='producto_cluster', component_property='value'),
      Input(component_id='radar_choice', component_property='value')]
)
def model_results(producto, radar_v):
    #Selecting the indexes to get results based on the radar choice selected
    if radar_v == "Competitividad":
        cols_to_avg = ["Competitividad", "Innovación", "Sostenibilidad/EPI", "Distancia","Arancel","Demanda"]
    else:
        cols_to_avg = ["Sostenibilidad", "Desarrollo", "Oportunidad", "Arancel","Demanda"]
    #Get dataframe with the results of the clusterization model based on the function in cluster.py
    dff, sil_sc = cluster.getClusterModel(producto, radar_v, 10)
    #Sort and organize the data
    dff.sort_values(by=['cluster'], ascending = False,inplace=True)
    dff["cluster"] = dff["cluster"] + 1
    dff.rename(columns={"cluster":"Clúster", "Nombre_pais":"País"}, inplace=True)
    columns = ["País","Puntaje medio","Clúster"]
    #Get sankey figure from the cluster.py function and update its format
    _, sankey_fig = cluster.getSankey(dff)
    sankey_fig.update_traces(textfont_size=20)
    sankey_fig.update_layout(title_text='Regiones vs Clústeres', title_x=0.5,font_size=14)
    sankey_fig.update_layout(height=800,)
    #Get radar plot
    radar_fig = cluster.getRadar(dff, cols_to_avg)
    #Change cluster type as category for the cloropleth map
    dff["Clúster"] = dff["Clúster"].astype('category')
    #Calculate mean score for the summary table
    dff["Puntaje medio"] = dff[cols_to_avg].mean(axis = 1, numeric_only=True).round(2)
    #Make dash data table with the results of the model
    table = dash_table.DataTable(
                        columns=[{"name": c, "id": c} for c in columns],
                        data=dff[["País","Puntaje medio","Clúster"]].to_dict("records"),
                        style_cell={'textAlign': 'center','font-family':'Segoe UI'}, style_as_list_view=True,
                        style_data={'color': 'white','backgroundColor': '#152F4F'}, 
                        style_header={'backgroundColor': '#373B44','color': 'white','fontWeight': 'bold'},
                        page_size=10, sort_action="native", filter_action="native", export_format="xlsx",
                    )
    colors = ['#3366CC', '#DC3912', '#FF9900', '#109618', '#990099', '#0099C6', '#DD4477', '#66AA00', '#B82E2E', '#316395']
    #Make cloropleth map with the results of the model and update its format
    map_fig = px.choropleth(dff, locations="iso3",
                            color="Clúster",
                            hover_name="País",
                            projection='natural earth',
                            animation_frame="Clúster",
                            title="Resultados de clusterización",
                            color_discrete_sequence=colors)
    map_fig.update_geos(showocean=True, oceancolor="LightBlue",showcountries=True)
    map_fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 2000
    map_fig.update_layout(title_text='Mapa interactivo de Clústeres', title_x=0.5)
    map_fig.update_layout(height=600)
    #Small description of the model and the calculation of the silouehette score
    results_text = "El algoritmo de clusterización utilizado es k-means, con el cual se obtiene un puntaje de silueta promedio de: " + str(round(sil_sc*100,1)) + "%"

    return table, map_fig, radar_fig, sankey_fig, results_text
