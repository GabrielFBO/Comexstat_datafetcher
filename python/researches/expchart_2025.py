import matplotlib as mpl
import pandas as pd

df = pd.read_csv('data/processed/exp_2025.csv')

while True:

    country = input("Enter the country name: ")

    df_country = df[df['Country'] == country.title()]
    if country == '':
        print(df)
    else:
        print(df_country)

    # Inserir a opção de criar um gráfico ou não, com as opções de filtragem.
    
    filename = (country.replace("/", "-").replace(" ", "_"))
    save = input("Do you want to save this data? (y/n): ")
    if save.lower() == 'y':
        format = input("CSV, Excel or JSON?")
        if format.capitalize() == 'csv':
            df_country.to_csv(f'results/{filename}_exp_2025.csv', index=False)
            print('CSV file saved!')
        elif format.title() == 'excel':
            df_country.to_excel(f'results/{filename}_exp_2025.xlsx', index=False)
            print('Excel sheet saved!')
        elif format.capitalize() == 'json':
            df_country.to_excel(f'results/{filename}_exp_2025.json', index=False)
            print('JSON file  saved!')

    new_search = input("Do you want to make a new search? (y/n): ")
    if new_search.lower() != 'y':
        break

print("Program finished!")




