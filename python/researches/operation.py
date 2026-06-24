import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import os
mpl.use('TkAgg')
os.makedirs('results', exist_ok=True)

while True:
    operation = input("Welcome to the ComexStat Data Fetcher System!" + "\nThis system will show you export or import data from 2022 or 2025" + "\nEnter the operation you want to research Export or Import: ").lower()
    if operation == 'export':
        year = input("Enter the year you want to research 2022 or 2025: ")
        if year == '2022':
            df = pd.read_csv('data/processed/exp_2022.csv')
        elif year == '2025':
            df = pd.read_csv('data/processed/exp_2025.csv')
    elif operation == 'import':
        year = input("Enter the year you want to research 2022 or 2025: ")
        if year == '2022':
            df = pd.read_csv('data/processed/imp_2022.csv')
        elif year == '2025':
            df = pd.read_csv('data/processed/imp_2025.csv')

    country = input("Enter the name of the country you want to research: ")
    df_country = df[df['Country'] == country.title()]
    if country == '':
        print("No country selected, please try again.")
    else:
        print(df_country)

    filename = (country.replace("/", "-").replace(" ", "_").title())

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