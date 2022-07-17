import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn import preprocessing
import pathlib

#---------------------------------------------------------------
# Loading Data
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("../data").resolve()

# Loading product-level Data
df_productos = pd.read_csv(DATA_PATH.joinpath('df_productos.csv'),dtype={'producto': str})
#Loading country level data
df_paises = pd.read_csv(DATA_PATH.joinpath("df_indices_paises.csv"),sep=";")
rename_cat={'iso3':"iso3", 'nombre':"Nombre_pais",'epi':"Sostenibilidad/EPI", 
            'innovacion':"Innovación", 'competitividad':"Competitividad",'distancia':"Distancia"}
df_paises.rename(columns=rename_cat, inplace=True)

#----------------------------------------------------------------------------
# This module has all the functions to perform the Clusterización - Kmeans algorithm

#Function to prepare the data by transforming and scaling the indexes
def prepareData(df):
    #Scaling the column values to avoid one column from influencing the results over the rest
    min_max_scaler = preprocessing.MinMaxScaler()
    x_minmax = min_max_scaler.fit_transform(df)
    feature_names = df.columns
    return pd.DataFrame(x_minmax, columns=feature_names)

#Function to do the clusterization and calculating results
def doClusters(df_norm, df_total, n_clusters = 12):
    #Fitting the model on the normalized variables
    kmeans = KMeans(n_clusters=n_clusters, random_state=7)
    cluster_res = kmeans.fit(df_norm)
    cluster_labels = kmeans.fit_predict(df_norm)
    sil_sc = silhouette_score(df_norm, cluster_labels)
    #Getting cluster labels and distances
    df_labels = pd.DataFrame(cluster_res.predict(df_norm),columns=["cluster"],index=df_total.index)
    distances = pd.DataFrame(cluster_res.transform(df_norm),index=df_total.index).min(axis=1)
    #Returning dataframe with labels and distances to centroids
    df_clusterizado = df_total.join(df_labels)
    df_clusterizado["d_centroides"] = distances
    #Returning a list of countries per cluster in case it is needed
    num_pais_cluster = df_clusterizado.groupby("cluster")["iso3"].count()
    return df_clusterizado, num_pais_cluster, sil_sc

#General function to prepare data and do clusterization model
def getClusterModel(producto, radar_v, n_clusters = 8):
    #Selecting the columns and dataframe to do the clusterization
    if radar_v == "Competitividad":
        df = df_paises[["iso3","Nombre_pais","Region","Sostenibilidad/EPI","Innovación","Competitividad","Distancia"]].copy()
        columns = ["Sostenibilidad/EPI", "Innovación","Competitividad","Distancia","Arancel","Demanda"]
    else:
        df = df_paises[["iso3","Nombre_pais","Region","Sostenibilidad","Desarrollo","Oportunidad"]].copy()
        columns = ["Sostenibilidad", "Desarrollo","Oportunidad","Arancel","Demanda"]
    #Colombia gets deleted before making the model
    df_copy = df.loc[(df["iso3"] != "COL")].copy()
    #Getting tariff and demand scores based on the product selected
    dff_prod = df_productos.loc[(df_productos["producto"] == producto),["iso3","Demanda","Arancel"]]
    #Joining those scores to the country indexes
    df_joined = pd.merge(df_copy, dff_prod, on='iso3', how='left')
    df_joined.fillna(0,inplace=True)
    df_joined.set_index('iso3')
    #Normalizing the data
    df_norm = prepareData(df_joined[columns])
    #Fitting the clustering model
    df_modelo, _, sil_sc = doClusters(df_norm, df_joined, n_clusters)
    return df_modelo, sil_sc

#Function to get the four closest countries according to the results of a clusterization model
def getRecommendedCountries(producto, country, radar_v):
    #Get dataframe with cluster results, labels and distances
    df_clusterizado, _ = getClusterModel(producto, radar_v)
    #Get the searched country cluster label
    country_cluster_num = df_clusterizado.loc[df_clusterizado["iso3"]==country,"cluster"].iloc[0]
    #Selecting only the cluster to which the country belongs and sorting by distance
    df_clusterpais = df_clusterizado.loc[(df_clusterizado["cluster"]==country_cluster_num)]
    df_sorted = df_clusterpais.sort_values(by=['d_centroides'], ascending = False)
    #This next condition selects the four closest countries by distance to centroid
    idx_country = list(np.where(df_sorted["iso3"] == country)[0])[0]
    num_countries_in_cluster = len(df_sorted.index)
    if num_countries_in_cluster < 4:
        indexes = list(range(num_countries_in_cluster))
        indexes.remove(idx_country)
    elif idx_country < 2:
        indexes = [idx_country+1,idx_country+2,idx_country+3,idx_country+4]
    elif idx_country < len(df_clusterizado.index)-2:
        indexes = [idx_country-1,idx_country-2,idx_country-3,idx_country-4]
    else:
        indexes = [idx_country-1,idx_country-2,idx_country+1,idx_country+2]
    #Returning only the four recommended countries
    paises_recomendados = df_sorted.iloc[indexes]["Nombre_pais"].tolist()
    return paises_recomendados

#Function to make the sankey diagram according to a dataframe with the clusterization results
def getSankey(df_clusterizado):
    #Make a sankey diagram grouping the clusterization results by region
    dff = df_clusterizado.groupby(['Region','Clúster'], as_index=False).agg({"País": "count",'iso3': ','.join}).copy()
    rename_cat={'Region':'source','Clúster':"target",'País':"value"}
    dff.rename(columns=rename_cat, inplace=True)
    #Defining the necessary data format for the sankey diagram
    unique_source_target = list(pd.unique(dff[['source', 'target']].values.ravel('K')))
    mapping_dict ={k : v for v, k in enumerate(unique_source_target)}
    dff = dff.copy()
    dff['source'] = dff['source'].map(mapping_dict)
    dff['target'] = dff['target'].map(mapping_dict)
    dff_dict = dff.to_dict(orient='list')
    #Styling colors to avoid repeating
    colors_amount = len(dff.index)
    color_scale = px.colors.qualitative.Set3
    colors_list=[]
    colors_list.extend([color_scale[i%12] for i in range(colors_amount)])
    #Creating the Sankey diagram based on the available results data and updating layout title
    sankey_fig = go.Figure(data=[go.Sankey(
                                    node = dict(
                                    pad = 15,
                                    thickness = 20,
                                    line = dict(color ="black", width = 0.5),
                                    label = unique_source_target,
                                    color = "#152f4f"
                                    ),
                                    link = dict(
                                    source = dff_dict["source"],
                                    target = dff_dict["target"],
                                    value = dff_dict["value"],
                                    color = colors_list,
                                    customdata = dff_dict["iso3"],
                                    hovertemplate='Desde %{source.label} hacia el clúster %{target.label} van %{value:.0f} paises:<br /> '+ '%{customdata}',
                                ))
                        ]
                    )
    sankey_fig.update_layout(title_text="Diagrama de Sankey", font_size=10)
    return dff, sankey_fig

#Function to get the average radar plot for each of the clusters
def getRadar(df_clusterizado, columns):
    #Make a radar plot grouping the indexes results by cluster
    dff = df_clusterizado.groupby(['Clúster'], as_index=False)[columns].mean().copy()
    dff.sort_values(by=['Clúster'], ascending = False,inplace=True)
    #Create radar plot
    df_radar = pd.melt(dff, id_vars=['Clúster'], var_name='index',value_name='value_idx', 
                        value_vars=columns)
    colors = ['#3366CC', '#DC3912', '#FF9900', '#109618', '#990099', '#0099C6', '#DD4477', '#66AA00', '#B82E2E', '#316395']
    #The radar plot is created based on indexes and countries
    fig_radar = px.line_polar(
                    df_radar,
                    r='value_idx', theta='index', color='Clúster', 
                    line_close=True, hover_name='Clúster',range_r=[0,5],
                    color_discrete_sequence=colors)
    fig_radar.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.1, xanchor="right", x=1))

    return fig_radar