import pandas as pd

#A datset prepared by team 235 which contains country names and iso3 codes
paises = pd.read_csv("raw_data/relacion_codigos_iso3.csv",sep=";",encoding='unicode_escape')
#A dataset with the relationships between sector, subsector and products, extracted from the original data sent
df_relaciones_productos = pd.read_csv("raw_data/relaciones_productos.csv",sep=";")

#Dataframe sectores
df = pd.read_csv("raw_data/sector.txt",sep="|",low_memory=False)
df['iso3'] = df['Pais'].map(paises.set_index('Name')['ISO3'])
df_sector = df[["Pais","iso3","Sector","s_p_general","s_p_o_general","s_p_d_general"]].copy()
df_sector.rename(columns={'Sector': 'sector','Pais': 'pais','s_p_general': 'score_general','s_p_o_general': 'score_oferta','s_p_d_general': 'score_demanda'},inplace=True, errors='raise')

#Dataframe subsectores
df2 = pd.read_csv("raw_data/subsector.txt",sep="|",low_memory=False)
df2['iso3'] = df2['Pais'].map(paises.set_index('Name')['ISO3'])
df_subsector = df2[["Pais","iso3","Subsector","s_p_general","s_p_o_general","s_p_d_general"]].copy()
df_subsector.rename(columns={'Subsector': 'subsector','Pais': 'pais','s_p_general': 'score_general','s_p_o_general': 'score_oferta','s_p_d_general': 'score_demanda'},
                    inplace=True, errors='raise')

#Dataframe productos
df3 = pd.read_csv("raw_data/producto.txt",sep="|",low_memory=False)
df3['iso3'] = df3['Pais'].map(paises.set_index('Name')['ISO3'])
df_producto = df3[["Pais","iso3","CD_Producto","s_p_general","s_p_o_general","s_p_d_general"]].copy()
df_producto.rename(columns={'CD_Producto': 'producto','Pais': 'pais','s_p_general': 'score_general','s_p_o_general': 'score_oferta','s_p_d_general': 'score_demanda'},
                    inplace=True, errors='raise')
#The null values are not countries but territories, so its possible to drop them
df_producto = df_producto[~df_producto["iso3"].isnull()].astype({'producto': 'str'})

#Aranceles
df4 = pd.read_csv("raw_data/aranceles.csv", sep=";", low_memory=False)
df4['iso3'] = df4['pais'].map(paises.set_index('Name')['ISO3'])
df_aranceles = df4[["Arancel_Pais_Colombia_T", "Código del producto", "pais", "iso3"]].copy()
df_aranceles.rename(columns={'Arancel_Pais_Colombia_T':'arancel', 'Código del producto':'producto'}, inplace=True, errors='raise')
df_aranceles = df_aranceles[~df_aranceles["arancel"].isnull()]
df_aranceles = df_aranceles.astype({'producto': 'str'})
df_aranceles['producto'] = df_aranceles['producto'].apply(lambda x: "0"+x if len(x)==5 else x)
df_aranceles.head()

#----------------------------------------------------------------------------
#Code to get scores for product, subsector and sector dataframes based on the info by ProColombia

#Merging the tariff scores to the products demand dataframe
df_outer = pd.merge(df_producto, df_aranceles, on=['producto',"iso3"], how='left')
#Getting the 80% percentile tariff for each product. This will be used as the maximum value to re-scale the tariff to a 0-5 scale.
#This decision was made because the tariffs dataset has really high outliers so rescaling on max() values would not give good results.
df_median = df_outer[["producto","arancel"]].groupby('producto')['arancel'].quantile(0.8)
df_outer2 = pd.merge(df_outer, df_median, on=['producto'], how='left')
#The tariff score of a country for a given product is dependant on the 80% percentile for all the tariffs of that product.
#This 80% is used as the maximum value to rescale, anything above 80% will have a 0.0 tariff score.
df_outer2["Arancel"] = round((1 - df_outer2["arancel_x"]/df_outer2["arancel_y"])*5,2)
#If there is no information, the tariff score will also be zero to punish lack of information, this could be corrected by the entity if it so chooses
df_outer2["Arancel"].fillna(0, inplace=True)
df_outer2["Arancel"]= df_outer2["Arancel"].apply(lambda r: max(r,0))
#The demand and offer scores are already normalized 0 to 1, so it is enough to multiply by 5
df_outer2["Oferta"] = round(df_outer2["score_oferta"]*5,2)
df_outer2["Demanda"] = round(df_outer2["score_demanda"]*5,2)

#Defining the final product dataframe
df_productos = df_outer2[["iso3","producto","Oferta","Demanda","Arancel"]].copy()
df_productos.to_csv('df_productos.csv', index = False)

#For subsector and sector, the tariff score for a country will be a simple average of the score for every product in that sector
#Demand and offer scores same as before, simple multiplication to re scale

#The process is as follows: The product df gets assigned the subsector or sector names
# Then, the tariff score per product gets aggregated by averaging scross country and subsector/sector
# This is the tariff score assigned to each country-subsector/sector combination

#Code to get the scores for subsector df
df_productos_subsec = pd.merge(df_productos, df_relaciones_productos[["subsector","producto"]], on=['producto'], how='left')
df_arancel_produ = df_productos_subsec[["iso3","subsector","Arancel"]].groupby(['subsector',"iso3"]).mean()
df_outer4 = pd.merge(df_subsector, df_arancel_produ, on=['subsector',"iso3"], how='left')
df_outer4["Arancel"].fillna(0, inplace=True)
df_outer4["Oferta"] = round(df_outer4["score_oferta"]*5,2)
df_outer4["Demanda"] = round(df_outer4["score_demanda"]*5,2)
df_outer4["Arancel"]= df_outer4["Arancel"].apply(lambda r: min(max(round(r,3),0.0),5.0))
df_subsectores = df_outer4[["iso3","subsector","Oferta","Demanda","Arancel"]].copy()
df_subsectores.to_csv('df_subsectores.csv', index = False)

#Code to get the scores for sector df
df_productos_sec = pd.merge(df_productos, df_relaciones_productos[["sector","producto"]], on=['producto'], how='left')
df_arancel_produ = df_productos_sec[["iso3","sector","Arancel"]].groupby(['sector',"iso3"]).mean()
df_outer3 = pd.merge(df_sector, df_arancel_produ, on=['sector',"iso3"], how='left')
df_outer3["Arancel"].fillna(0, inplace=True)
df_outer3["Oferta"] = round(df_outer3["score_oferta"]*5,2)
df_outer3["Demanda"] = round(df_outer3["score_demanda"]*5,2)
df_outer3["Arancel"]= df_outer3["Arancel"].apply(lambda r: min(max(round(r,3),0.0),5.0))
df_sectores = df_outer3[["iso3","sector","Oferta","Demanda","Arancel"]].copy()
df_sectores.to_csv('df_sectores.csv', index = False)
