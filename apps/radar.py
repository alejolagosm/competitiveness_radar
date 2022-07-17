import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pathlib

import dash 
from dash import dcc
from dash import html
from dash import dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

from app import app
from apps import navbar
from apps import radar_df
#---------------------------------------------------------------
#Get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("../data").resolve()

# Loading Country-level Data
df_paises = pd.read_csv(DATA_PATH.joinpath("df_indices_paises.csv"),sep=";")
rename_cat={'nombre':"Nombre_pais",'epi':"Sostenibilidad/EPI", 
            'innovacion':"Innovación", 'competitividad':"Competitividad",'distancia':"Distancia"}
df_paises.rename(columns=rename_cat, inplace=True)
df_idx_var = pd.read_csv(DATA_PATH.joinpath("df_idx_var.csv"),sep=";")

# Loading product-level Data (Including sector and subsectors)
df_relaciones_productos = pd.read_csv(DATA_PATH.joinpath("relaciones_productos.csv"),sep=";")
df_relaciones_productos["label_productos"] = df_relaciones_productos["producto"] + "-" + df_relaciones_productos["desc_producto"]
df_productos = pd.read_csv(DATA_PATH.joinpath('df_productos.csv'),dtype={'producto': str})
#Default theme for the graphs
px.defaults.template = "ggplot2"
#---------------------------------------------------------------
#Page Layout
layout = html.Div([
        navbar.navbar,
        #Title
        dbc.Row([html.H1("Radar de competitividad", style={'textAlign':'center',"margin-top":"16px"}), html.Hr()],
                style={"max-width":"1000px","margin":"auto"}
        ),
        #Dropdown options for the results
        dbc.Row([
            html.Label(['Elija una opción para el radar'],style={'font-weight': 'bold'}),
            dcc.RadioItems(
                id='radar_choice',
                options=[
                         {'label': 'V1: Empresario conservador ', 'value': 'Competitividad'},
                         {'label': 'V2: Emprendedor arriesgado', 'value': 'Oportunidad'},
                ],
                value='Competitividad',
            ),
        ],style={'textAlign':'center',"margin-top":"10px"}),
        dbc.Row(html.P("Elija países y un nivel de exportación (Sector, subsector o productos) para generar resultados",
                         style={'textAlign':'center',"margin-top":"16px"})
                ),
        dbc.Row(
            [
            #First column are the two country-level dropdowns
            dbc.Col(
                 html.Div([
                    html.Label("Acuerdo comercial", style={'fontSize':20, 'textAlign':'center'}),
                    dcc.Dropdown(
                        id='acuerdos_dpn', 
                        options=[{'label': s, 'value': s} for s in sorted(df_paises["comercial"].unique())],
                    ),
                    html.Label("Nombre País", style={'fontSize':20, 'textAlign':'center'}),
                    dcc.Dropdown(
                        id='input_iso3', 
                        options=[{'label': s, 'value': s} for s in sorted(df_paises["Nombre_pais"].unique())],
                        value=['Alemania'],clearable=False, multi=True,
                    ),
                ]), style={'text-align': 'center','align-self':'center','justify-self':'center'}, md=12,lg=6
            ),
            #Second column are the product-level dropdowns
            dbc.Col(
                html.Div([
                    html.Label("Sector", style={'fontSize':20, 'textAlign':'center'}),
                    dcc.Dropdown(
                        id='sectores-dpdn', 
                        options=[{'label': s, 'value': s} for s in sorted(df_relaciones_productos["sector"].unique())],
                        value='Agroindustrial', clearable=False
                    ),
                    html.Label("Subsector", style={'fontSize':18, 'textAlign':'center'}),
                    dcc.Dropdown(id='subsectores-dpdn', options=[]),
                    html.Label("Producto", style={'fontSize':15, 'textAlign':'center'}),
                    dcc.Dropdown(id='productos-dpdn', options=[], multi=True,),
                ]), style={'text-align': 'center','align-self':'center','justify-self':'center'}, md=12,lg=6
            )
            ],
         style={"max-width":"1000px","display":"flex","justify-content":"center","margin":"auto"}
        ),
        #This is the output of the clusterization model, recommending the closest countries to the main selected country.
        dbc.Row(dcc.Markdown(id="recommendations", style={'textAlign':'center',"margin-top":"16px"})),
        #Results of the radar plot
        dbc.Row([html.H1("Resultados principales", style={'textAlign':'center',"margin-top":"16px"}), html.Hr()],
                style={"max-width":"1000px","margin":"auto"}
        ),
        #Main radar plot
        dbc.Row(
            dbc.Spinner(children=[dcc.Graph(id="radar_graph")], size="lg", color="#B51F1F", type="border"),
                        style={"max-width":"700px","display":"flex","justify-content":"center","margin":"auto"}            
        ),
        #Results table summarizing the data shown in the radar plot
        dbc.Row(
            html.Div(id="results_table"),
            style={"max-width":"80%","overflow-x":"scroll","margin":"auto","textAlign":"center","justify-content":"center", "align-items":"center",}
        ),
        #Section to display the indexes variation for every country selected
        dbc.Row(html.H2("Gráficas de comparación", style={'textAlign':'center',"margin-top":"16px"})),
        dbc.Row(html.P("Variación de los índices de los países seleccionados en los últimos 10 años", style={'textAlign':'center',"margin-top":"16px"})),
        dbc.Row(
            dcc.Graph(id='bar_country'),
            style={"max-width":"1000px","margin":"auto","margin-bottom":"50px"}
        ),
        #Section to display the relationships between tariffs and demand score for the sector selected
        dbc.Row(html.P("Comparación de puntajes de arancel y demanda para productos similares a los seleccionados", style={'textAlign':'center',"margin-top":"16px"})),
        dbc.Row(
            html.Div([], id="scatter_country"),
            #dcc.Graph(id='scatter_country'),
            style={"max-width":"1000px","margin":"auto","margin-bottom":"50px"}
        ),
], style={"background": "white","min-height":"100vh",})

#---------------------------------------------------------------
#Callback Functions
# Populate the options of countries based on comercial agreements
@app.callback(
    Output('input_iso3', 'value'),
    Input('acuerdos_dpn', 'value')
)
def set_countries_values(chosen_agreement):
    #Getting the countries names based on the chosen agreement. Default value otherwise is USA.
    if chosen_agreement is None:
        return ["Estados Unidos de América"]
    else:
        dff = df_paises[df_paises["comercial"]==chosen_agreement]
        return sorted(dff["Nombre_pais"].unique())

# Populate the options of subsectors dropdown based on sectors dropdown
@app.callback(
    Output('subsectores-dpdn', 'options'),
    Input('sectores-dpdn', 'value')
)
def set_subsectores_options(chosen_sector):
    dff = df_relaciones_productos[df_relaciones_productos["sector"]==chosen_sector]
    return [{'label': c, 'value': c} for c in sorted(dff["subsector"].unique())]

# Populate values of products dropdown based on subsectors selection or give entire products list
@app.callback(
    Output('productos-dpdn', 'options'),
    Input('subsectores-dpdn', 'value')
)
def set_productos_options(chosen_subsector):
    #Selecting all the products if the user has not filtered by subsector, otherwise, select only the products within the given subsector
    if chosen_subsector is None:
        return [{'label': c, 'value': c[:6]} for c in sorted(df_relaciones_productos["label_productos"])]
    else:
        dff = df_relaciones_productos[df_relaciones_productos["subsector"]==chosen_subsector]
        return [{'label': c, 'value': c[:6]} for c in sorted(dff["label_productos"])]

# Callback to create the radar plot, results table and country recommendations based on the country and product-related dropdown values
@app.callback(
    [Output(component_id='radar_graph', component_property='figure'),
     Output(component_id='results_table',component_property='children'),
     Output(component_id='recommendations',component_property='children'),],
    [Input(component_id='input_iso3', component_property='value'),
    Input(component_id='sectores-dpdn', component_property='value'),
    Input(component_id='subsectores-dpdn', component_property='value'),
    Input(component_id='productos-dpdn', component_property='value'),
    Input(component_id='radar_choice', component_property='value')]
)
def update_output(countries_selected, sector_selected, subsector_selected, products_selected, radar_v):
    #Selecting the columns basedon the radar version
    if radar_v == "Competitividad":
        columns = ["Sostenibilidad/EPI", "Innovación", "Competitividad", "Distancia", "Arancel", "Demanda"]
    else:
        columns = ["Sostenibilidad", "Desarrollo", "Oportunidad", "Arancel", "Demanda"]
    #This condition selects the right function to filter all the dataframes to get the required information for the radar plot and the similar countries recommendations
    if products_selected is not None and len(products_selected) > 0:
        dff_0, recommendation = radar_df.get_radar_products(countries_selected, products_selected, radar_v)
    else:
        dff_0 = radar_df.get_radar_sectors(countries_selected, sector_selected, subsector_selected, radar_v)
        recommendation = "Por favor elija un producto y un país para generar recomendaciones"
    #The summary dataframe is converted to narrow format to input the radar plot
    df_radar = pd.melt(dff_0, id_vars=['Identificador'], var_name='index',value_name='value_idx', 
                        value_vars=columns)
    #The radar plot is created based on indexes and countries
    fig_radar = px.line_polar(
                    df_radar, 
                    r='value_idx', theta='index', color='Identificador', 
                    line_close=True, hover_name='Identificador',range_r=[0,5],
                    color_discrete_sequence=px.colors.qualitative.Dark2) 
    #Styling the plot: Legend and background colors
    fig_radar.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.1, xanchor="right", x=1))

    #Creating the results table shown below the radar plot
    results_table = dash_table.DataTable(
                    columns=[{"name": c, "id": c} for c in ['Identificador']+columns],
                    data=dff_0.to_dict("records"),
                    style_cell={'textAlign': 'center','font-family':'Segoe UI'}, style_as_list_view=True,
                    style_data={'color': 'white','backgroundColor': '#152F4F'},
                    style_header={'backgroundColor': '#373B44','color': 'white','fontWeight': 'bold'},
                    page_size=10,sort_action="native",export_format="xlsx",
                )
    
    return fig_radar, results_table, recommendation

# Create bar chart of indexes change in last 10 years based on the selected countries
@app.callback(
    Output(component_id='bar_country', component_property='figure'),
    Input(component_id='input_iso3', component_property='value'),
)
def update_scatter(countries_selected):
    countries_selected.sort()
    #Selecting all the iso3 codes of the countries selected
    countries_iso3 = df_paises.loc[df_paises["Nombre_pais"].isin(countries_selected), "iso3"].tolist()
    #Filtering the indexes data by countries selected
    dff_0 = df_idx_var.loc[df_idx_var["iso3"].isin(countries_iso3)]
    #Melting the dataframe for easier use when constructing the plot
    df_bar = pd.melt(dff_0, id_vars=['País','Índice'], var_name='year',value_name='value_idx', 
                          value_vars=["2012","2017","2021"])
    #Creating the line chart and formatting the axis, legend and background
    lineplot = px.line(df_bar, x="year", y="value_idx", color="Índice", markers=True,
                         facet_col="País", facet_col_wrap=2,  facet_row_spacing=0.2, facet_col_spacing=0.1,
                         color_discrete_sequence=px.colors.qualitative.Dark2)
    lineplot.update_xaxes(title="Año", showline=True, linewidth=2, ticks="outside", tickwidth=2, tickcolor="black")
    lineplot.update_yaxes(range=[0, 5.5], showline=True, linewidth=2, ticks="outside", tickwidth=2, tickcolor="black")
    lineplot.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.1, xanchor="right", x=1))

    return lineplot

# Update scatter plot based on sector and countries selected
@app.callback(
    Output(component_id='scatter_country', component_property='children'),
    [Input(component_id='input_iso3', component_property='value'),
    Input(component_id='productos-dpdn', component_property='value'),]
)
def update_scatter(countries_selected, products_selected):
    #Sorting the countries selected alpabhetically to avoid selection problems
    countries_selected.sort()
    if products_selected is None:
        return html.P("Debe elegir por lo menos un producto para generar esta gráfica de resultados", style={'textAlign':'center'})
    else:
        #Starting the figure and colors variable
        fig = go.Figure()
        colors = px.colors.qualitative.Bold
        #This loop adds scatter traces (points) for each country selected
        for idx, country in enumerate(countries_selected):
            #Getting the country ISO3 code
            country_iso3 = df_paises.loc[df_paises["Nombre_pais"]==country, "iso3"].iloc[0]
            #Getting the sector code based on the product (HS2 from the HS6)
            nombres_subsectores = df_relaciones_productos.loc[df_relaciones_productos["producto"].isin(products_selected),"subsector"].unique().tolist()
            productos_subsector = df_relaciones_productos.loc[df_relaciones_productos["subsector"].isin(nombres_subsectores),"producto"].tolist()
            #Filtering the data based on sector code and countries ISO3 
            dff = df_productos.loc[(df_productos["iso3"]==country_iso3) & (df_productos["producto"].isin(productos_subsector)), ["iso3","producto","Demanda","Arancel"]]
            desc_productos = df_relaciones_productos.loc[df_relaciones_productos["producto"].isin(productos_subsector),["label_productos","producto"]]
            dff_1 = pd.merge(dff, desc_productos, on='producto', how='left')
            #Adding each country trace to the plot
            fig.add_trace(go.Scatter(
                            x=dff_1["Demanda"], y=dff_1["Arancel"],
                            mode='markers',name=country, marker=dict(size=dff_1["Demanda"]*5),                         
                            marker_color=colors[idx], text= dff_1['label_productos'])
                        )
        #Editing the entire figure options: Axis and background colors
        fig.update_xaxes(title="Puntaje Demanda", range=[-0.1, 5.5], linewidth=2, ticks="outside", tickwidth=2, tickcolor="black")
        fig.update_yaxes(title="Puntaje Arancel", range=[-0.2, 5.5], linewidth=2, ticks="outside", tickwidth=2, tickcolor="black")
        fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.1, xanchor="right", x=1))
        fig.update_layout(template="ggplot2")
        return dcc.Graph(figure=fig)
