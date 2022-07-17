import numpy as np
import pandas as pd
import pathlib
from apps import cluster

#---------------------------------------------------------------
# Loading Data
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("../data").resolve()
#Country level data
df_paises = pd.read_csv(DATA_PATH.joinpath("df_indices_paises.csv"),sep=";")
rename_cat={'iso3':"iso3", 'nombre':"Nombre_pais",'epi':"Sostenibilidad/EPI", 
            'innovacion':"Innovación", 'competitividad':"Competitividad",'distancia':"Distancia"}
df_paises.rename(columns=rename_cat, inplace=True)
#Product level data
df_sectores = pd.read_csv(DATA_PATH.joinpath("df_sectores.csv"),sep=",")
df_subsectores = pd.read_csv(DATA_PATH.joinpath("df_subsectores.csv"),sep=",")
df_productos = pd.read_csv(DATA_PATH.joinpath('df_productos.csv'),dtype={'producto': str})
df_relaciones_productos = pd.read_csv(DATA_PATH.joinpath("relaciones_productos.csv"),sep=";")

#----------------------------------------------------------------------------
# This module has all the functions to perform the data analysis needed for the radar tab

#This function filters all the dataframes based on the given product and country options and returns a dataframe with all the relevant information
#Also, based on the product and country, the function calls the clustering model to get recommendations for the user
def get_radar_products(countries_selected, products_selected, radar_v = "Competitividad"):
    if radar_v == "Competitividad":
        columns = ["iso3","Nombre_pais","Sostenibilidad/EPI","Innovación","Competitividad","Distancia"]
    else:
        columns = ["iso3","Nombre_pais","Sostenibilidad","Desarrollo","Oportunidad"]
    countries_selected.sort()
    products_selected.sort()
    countries_iso3 = df_paises.loc[df_paises["Nombre_pais"].isin(countries_selected), "iso3"].tolist()
    #Select the general country indexes
    dff_index_countries = df_paises.loc[df_paises["Nombre_pais"].isin(countries_selected),columns]
    #dff_0 = dff_index_countries.copy()
    #This loop selects the appropriate tariff and demand score, based on the lowest user selection (Product, sector or subsector) and adds them to lists
    for idx, product_selected in enumerate(products_selected):
        #Selecting the tariff and demand score from the product datasets and merging them to the index scores for the countries selected
        dff_1 = df_productos.loc[(df_productos["iso3"].isin(countries_iso3)) & (df_productos["producto"] == product_selected)]
        dff_product = pd.merge(dff_index_countries, dff_1[["iso3","Demanda","Arancel"]], on='iso3', how='left')
        dff_product["Identificador"] = dff_product["Nombre_pais"] + "-" + product_selected
        if idx == 0:
            #This code will find the recommended countries based on a k-means clusterization algorithm
            first_country_iso3 = df_paises.loc[df_paises["Nombre_pais"] == countries_selected[0], "iso3"].iloc[0]
            recommended_countries = cluster.getRecommendedCountries(product_selected, first_country_iso3, radar_v)
            countries_to_recommend = ', '.join(recommended_countries)
            recommendation = f"""
                Para {countries_selected[0]} y el producto {product_selected} le recomendamos que también busque:  
                **{countries_to_recommend}**
                """
            dff_0 = dff_product.copy()
        else:
            dff_0 = pd.concat([dff_0, dff_product])
    dff_0.fillna(0, inplace=True)
    return dff_0, recommendation


#This function filters all the dataframes based on the given sector/subsector and countries options and returns a dataframe with all the relevant information
def get_radar_sectors(countries_selected, sector_selected, subsector_selected, radar_v = "Competitividad"):
    if radar_v == "Competitividad":
        columns = ["iso3","Nombre_pais","Sostenibilidad/EPI","Innovación","Competitividad","Distancia"]
    else:
        columns = ["iso3","Nombre_pais","Sostenibilidad","Desarrollo","Oportunidad"]
    countries_selected.sort()
    countries_iso3 = df_paises.loc[df_paises["Nombre_pais"].isin(countries_selected), "iso3"].tolist()
    #Select the general country indexes
    dff_0 = df_paises.loc[df_paises["Nombre_pais"].isin(countries_selected),columns]
    #This condition selects the appropriate tariff and demand score, based on the lowest user selection (sector or subsector) and adds them to lists
    if subsector_selected is not None:
        #This selects tariff and demand score based on each country/subsector pair.
        countries_iso3 = df_paises.loc[df_paises["Nombre_pais"].isin(countries_selected), "iso3"].tolist()
        dff_1 = df_subsectores.loc[(df_subsectores["iso3"].isin(countries_iso3)) & (df_subsectores["subsector"] == subsector_selected)]
        dff_0 = pd.merge(dff_0, dff_1[["iso3","Demanda","Arancel"]], on='iso3', how='left')
    else:
        #Same as before, this cycle selects tariff and demand score based on each country/sector pair
        countries_iso3 = df_paises.loc[df_paises["Nombre_pais"].isin(countries_selected), "iso3"].tolist()
        dff_1 = df_sectores.loc[(df_sectores["iso3"].isin(countries_iso3)) & (df_sectores["sector"] == sector_selected)]
        dff_0 = pd.merge(dff_0, dff_1[["iso3","Demanda","Arancel"]], on='iso3', how='left')
    dff_0.fillna(0, inplace=True)
    dff_0["Identificador"] = dff_0["Nombre_pais"]
    return dff_0