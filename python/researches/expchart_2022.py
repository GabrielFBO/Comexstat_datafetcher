import matplotlib as mpl
import pandas as pd

df = pd.read_csv('data/processed/exp_2022.csv')

while True:

    country = input("Enter the country name: ")

    df_country = df[df['Country'] == country.title()]
    if country == '':
        print(df)
    else:
        print(df_country)

    # Inserir a opção de criar um gráfico ou não, com as opções de filtragem.
    # chart = input("Would you like to generate a chart for the top 10 products by value in USD? (y/n)")
    # if chart.lower() == 'y':
    #     ch_type = input("What type of chart? Bar, Pie or Columns?")
    #         if ch_type.title() = 'bar':
    #             #Gráfico barra top 10
    #         elif ch_type.title() = 'pie':
    #            #Gráfico pizza top 10
            
    #         elif ch_type.title() = 'columns':
    #             #Gráfico colunas top 10
    
    filename = (country.replace("/", "-").replace(" ", "_"))
    
    save = input("Do you want to save this data? (y/n): ")
    if save.lower() == 'y':
        format = input("CSV, Excel or JSON? ").lower()
        if format == 'csv':
            df_country.to_csv(f'results/{filename}_exp_2022.csv', index=False)
            print('CSV file saved!')
        elif format == 'excel':
            df_country.to_excel(f'results/{filename}_exp_2022.xlsx', index=False)
            print('Excel sheet saved!')
        elif format == 'json':
            df_country.to_json(f'results/{filename}_exp_2022.json')
            print('JSON file  saved!')

    new_search = input("Do you want to make a new search? (y/n): ")
    if new_search.lower() != 'y':
        break

print("Program finished!")




