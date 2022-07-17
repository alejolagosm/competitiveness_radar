from dash import dcc
from dash import html
from dash.dependencies import Input, Output

# Connect to main app.py file
from app import app
from app import server

# Connect to your app pages
from apps import radar, model, disclaimer, inicio

#This perform the routing of the application
url_content_layout = html.Div(children=[
    dcc.Location(id="url",refresh=False),
    html.Div(id="output-div")
])
app.layout = url_content_layout
app.validation_layout = html.Div([
    url_content_layout,
    radar.layout,
    model.layout
])

#Callback to create the dinamic routing of the application
@app.callback(Output(component_id="output-div",component_property="children"),Input(component_id="url",component_property="pathname"))
def display_page(pathname):
    if pathname == '/apps/radar':
        return radar.layout
    if pathname == '/apps/model':
        return model.layout
    if pathname == '/apps/disclaimer':
        return disclaimer.layout
    else:
        return inicio.layout

if __name__ == '__main__':
    app.run_server(debug=False)