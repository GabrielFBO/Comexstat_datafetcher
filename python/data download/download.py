import requests as rq
import os

# Create data/raw directory if it doesn't exist
os.makedirs("data/raw", exist_ok=True)

files = {
    "EXP_2022.csv": "https://balanca.economia.gov.br/balanca/bd/comexstat-bd/ncm/EXP_2022.csv",
    "EXP_2025.csv": "https://balanca.economia.gov.br/balanca/bd/comexstat-bd/ncm/EXP_2025.csv",
    "IMP_2022.csv": "https://balanca.economia.gov.br/balanca/bd/comexstat-bd/ncm/IMP_2022.csv",
    "IMP_2025.csv": "https://balanca.economia.gov.br/balanca/bd/comexstat-bd/ncm/IMP_2025.csv",
    "NCM.csv": "https://balanca.economia.gov.br/balanca/bd/tabelas/NCM.csv",
    "PAIS.csv": "https://balanca.economia.gov.br/balanca/bd/tabelas/PAIS.csv"
}

print("Starting downloads...\n")

for filename, url in files.items():

    filepath = f"data/raw/{filename}"

    # Skip download if file already exists
    if os.path.exists(filepath):
        print(f"✓ {filename} already exists. Skipping.")
        continue

    print(f"Downloading {filename}...")

    try:

        response = rq.get(url, stream=True, timeout=60)
        response.raise_for_status()

        with open(filepath, "wb") as file:

            for chunk in response.iter_content(chunk_size=8192):

                if chunk:
                    file.write(chunk)

        print(f"✓ {filename} downloaded successfully.\n")

    except rq.exceptions.RequestException as error:

        print(f"✗ Error downloading {filename}")
        print(f"  {error}\n")

print("Download process finished.")