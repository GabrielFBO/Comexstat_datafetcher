import pandas as pd
import requests as rq
import urllib3
import matplotlib.pyplot as plt
import matplotlib as mpl
import os

#DATA DOWNLOAD

print("Welcome to ComexStat DataFetcher, the program will download and process the data that will be used in the operation. Please wait.")

urllib3.disable_warnings(
    urllib3.exceptions.InsecureRequestWarning
)

os.makedirs("data/raw", exist_ok=True)

files = {
    "EXP_2022.csv": "https://balanca.economia.gov.br/balanca/bd/comexstat-bd/ncm/EXP_2022.csv",
    "EXP_2025.csv": "https://balanca.economia.gov.br/balanca/bd/comexstat-bd/ncm/EXP_2025.csv",
    "IMP_2022.csv": "https://balanca.economia.gov.br/balanca/bd/comexstat-bd/ncm/IMP_2022.csv",
    "IMP_2025.csv": "https://balanca.economia.gov.br/balanca/bd/comexstat-bd/ncm/IMP_2025.csv",
    "NCM.csv": "https://balanca.economia.gov.br/balanca/bd/tabelas/NCM.csv",
    "PAIS.csv": "https://balanca.economia.gov.br/balanca/bd/tabelas/PAIS.csv"
}

for filename, url in files.items():

    filepath = f"data/raw/{filename}"

    print(f"Downloading {filename}...")

    response = rq.get(
        url,
        stream=True,
        timeout=60,
        verify=False
    )

    response.raise_for_status()

    with open(filepath, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                file.write(chunk)

    print(f"{filename} downloaded successfully!")



#DATA CLEANING AND ORGANIZATION

print("\nNow the program will clean and organize the downloaded data. Please wait...")


os.makedirs('data/processed', exist_ok=True)


# 2022 EXPORTATION

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

df.to_csv('data/processed/exp_2022.csv', index=False)

print("Exportations from 2022 saved and ready!")

#2025 EXPORTATION

df = pd.read_csv('data/raw/EXP_2025.csv', sep=";")
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

df.to_csv('data/processed/exp_2025.csv', index=False)

print("Exportations from 2025 saved and ready!")


#2022 IMPORTATION

df = pd.read_csv('data/raw/IMP_2022.csv', sep=";")
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

df.to_csv('data/processed/imp_2022.csv', index=False)

print("Importations from 2022 saved and ready!")

#2025 IMPORTATION

df = pd.read_csv('data/raw/IMP_2025.csv', sep=";")
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

df.to_csv('data/processed/imp_2025.csv', index=False)

print("Importations from 2025 saved and ready!" + "\nThe data is ready to be analized! Enjoy it :D")


#OPERATIONS PROGRAM


mpl.use('TkAgg')
os.makedirs('results', exist_ok=True)

while True:

    #OPERATION
    while True:
        operation = input("\nWelcome to the operation analysis program!" + "\nThis application will show you export or import data from 2022 or 2025" + "\nEnter the operation you want to research Export or Import: ").lower()
        if operation in ['export', 'import']:
           break
        print("Operation not found. Try again!")

    #YEAR
    while True:
        year = input("Enter the year you want to research 2022 or 2025: ")
        if year == '2022':
            if operation == 'export':
                df = pd.read_csv('data/processed/exp_2022.csv')            
            else:
               df = pd.read_csv('data/processed/imp_2022.csv')
            break
        elif year == '2025':
            if operation == 'export':
                df = pd.read_csv('data/processed/exp_2025.csv')            
            else:
               df = pd.read_csv('data/processed/imp_2025.csv')
            break        
        
        print("Year not found. Try again!")
    
    #COUNTRY
    while True:  
        country = input("Enter the name of the country you want to research: ")
        if country == '':
            print("No country selected, please try again.")
            continue
        df_country = df[df['Country'] == country.title()]
        if df_country.empty:
            print("Country not found. Try again!")
            continue
        print(df_country)
        break
    
    filename = (country.replace("/", "-").replace(" ", "_").title())

#CHARTS
    chart = input("Would you like to generate a chart for the top 10 products by USD from the selected country? (y/n): ")
    if chart.lower() == 'y':
        top10 = (df_country.groupby('NCM Description')['Valor USD'].sum().sort_values(ascending=False).head(10))
        print(top10)
        ch_type = int(input("What type of chart? (1)Bar, (2)Pie or (3)Horizontal bar? "))
        if ch_type == 1:
            top10.plot(kind='bar')
            plt.title(f'Top 10 products {operation} - {country.title()} {year}')
            plt.xlabel('Product')
            plt.ylabel('USD Value')
            plt.show()
            ch_save = input("Would you like to save the chart? (y/n): ").lower()
            if ch_save == 'y':
                plt.savefig(f'results/{filename}_barchart_{operation}_{year}.png')
                print('Bar chart saved!')
            else:
                plt.close()
                
            
        elif ch_type == 2:
            top10.plot(kind='pie', autopct='%1.1f%%')
            plt.title(f'Top 10 products {operation} - {country.title()} {year}')
            plt.ylabel('')
            plt.show()
            ch_save = input("Would you like to save the chart? (y/n): ").lower()
            if ch_save == 'y':
                plt.savefig(f'results/{filename}_piechart_{operation}_{year}.png')
                print('Pie chart saved!')
            else:
                plt.close()
                
            
        elif ch_type == 3:
            top10.plot(kind='barh')
            plt.title(f'Top 10 products {operation} - {country.title()} {year}')
            plt.xlabel('USD Value')
            plt.ylabel('Product')
            plt.show()
            ch_save = input("Would you like to save the chart? (y/n): ").lower()
            if ch_save == 'y':
                plt.savefig(f'results/{filename}_horizontal_barchart_{operation}_{year}.png')
                print('Horizontal bar chart saved!')
            else:
                plt.close()
                
        
    save = input("Do you want to save the table? (y/n): ")
    if save.lower() == 'y':
        format = int(input("(1)CSV, (2)Excel or (3)JSON? "))
        if format == 1:
            df_country.to_csv(f'results/{filename}_{operation}_{year}.csv', index=False)
            print('CSV file saved!')
        elif format == 2:
            df_country.to_excel(f'results/{filename}_{operation}_{year}.xlsx')
            print('Excel sheet saved!')
        elif format == 3:
            df_country.to_json(f'results/{filename}_{operation}_{year}.json')
            print('JSON file  saved!')

    new_search = input("Do you want to make a new search? (y/n): ")
    if new_search.lower() != 'y':
        break

print("Program finished!" + "\nThanks for using our system. If there is any problem or suggestions, please contact me on github.com/GabrielFBO. Goodbye :D")