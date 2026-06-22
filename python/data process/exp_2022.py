import pandas as pd

df = pd.read_csv('data/raw/EXP_2022.csv', sep=";")
df = df.drop(columns=['CO_UNID', 'SG_UF_NCM', 'CO_URF', 'CO_VIA', 'QT_ESTAT', 'KG_LIQUIDO'])

df_country = pd.read_csv('data/raw/PAIS.csv', sep=";", encoding='latin1')
df_country = df_country.drop(columns=['CO_PAIS_ISON3', 'CO_PAIS_ISOA3', 'NO_PAIS', 'NO_PAIS_ESP'])

df = df.merge(df_country, on='CO_PAIS', how='left')
df = df.drop(columns=['CO_PAIS'])

df_ncm = pd.read_csv('data/raw/NCM.csv', sep=";", encoding='latin1')
df_ncm = df_ncm.drop(columns=['CO_UNID','CO_SH6','CO_PPE','CO_PPI','CO_FAT_AGREG','CO_CUCI_ITEM','CO_CGCE_N3','CO_SIIT','CO_ISIC_CLASSE','CO_EXP_SUBSET', 'NO_NCM_POR','NO_NCM_ESP'])
df = df.merge(df_ncm, on='CO_NCM', how='left')


df = df.rename(columns={'CO_ANO':'Year', 'CO_MES':'Month', 'CO_NCM':'NCM', 'VL_FOB':'Valor USD', 'NO_PAIS_ING':'Country', 'NO_NCM_ING' : 'NCM Description'})
df = df[['Year', 'Country', 'Month', 'Valor USD', 'NCM Description', 'NCM']]
df = df.sort_values('Country')
print(df)

df.to_csv('data/processed/exp_2022.csv', index=False)
