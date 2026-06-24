import requests as rq
import urllib3
import os

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