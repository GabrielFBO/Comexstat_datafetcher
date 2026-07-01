# ComexStat Data Fetcher

A Python application for downloading, processing, analyzing, and exporting Brazilian foreign trade data from the official ComexStat database.

The application allows users to search import and export data by country, generate charts of the top exported/imported products, and export the results in multiple formats.

---

## Features

- Download official ComexStat datasets automatically
- Process raw CSV files into clean datasets
- Search trade data by country
- Support for:
  - Export operations
  - Import operations
- Available years:
  - 2022
  - 2025
- Generate Top 10 products charts
  - Vertical Bar Chart
  - Horizontal Bar Chart
  - Pie Chart
- Export results as:
  - CSV
  - Excel (.xlsx)
  - JSON

---

## Technologies

- Python 3
- Pandas
- Matplotlib
- Requests
- OpenPyXL

---

## Project Structure

```
ComexStat_DataFetcher/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── results/
│
├── python/
│
├── requirements.txt
├── .gitignore
└── main.py
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/GabrielFBO/ComexStat_DataFetcher.git
cd ComexStat_DataFetcher
```

Create a virtual environment:

### Linux / macOS

```bash
python -m venv venv
source venv/bin/activate
```

### Fish Shell

```bash
python -m venv venv
source venv/bin/activate.fish
```

Install the required libraries:

```bash
pip install -r requirements.txt
```

---

## Usage

Run the application:

```bash
python main.py
```

The program will guide you through the following steps:

1. Select the operation (Export or Import)
2. Select the year
3. Enter the country name
4. Display the results
5. Optionally generate charts
6. Optionally export the data

---

## Data Source

Official ComexStat database provided by the Brazilian Government.

https://balanca.economia.gov.br/balanca/bd/comexstat-bd/

---

## Example

Example search:

```
Operation:
Export

Year:
2025

Country:
Japan
```

Output:

- All exported products to Japan
- Total USD value
- Top 10 products chart
- Export to CSV / Excel / JSON

---

## Future Improvements

- Support for additional years
- Country list auto-complete
- Search by NCM code
- Search by product description
- Interactive dashboard
- Streamlit web interface
- Better error handling
- Automatic update checker

---

## License

This project is licensed under the MIT License.

---

## Author

Gabriel B.

GitHub:
https://github.com/GabrielFBO
