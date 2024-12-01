import os
import csv
import requests
import datetime
import pandas as pd

def main():
    date = datetime.datetime.now().strftime("%d%m%y")
    city = "Bytom"
    output_dir = "./output"
    csv_file = f"{output_dir}/output_{date}_{city}.csv"
    xlsx_file = f"{output_dir}/output_{date}_{city}.xlsx"
    get_env_ready(output_dir=output_dir, csv_path=csv_file)
    olx_data = scrape(city=city, filepath=csv_file)
    save_to_xlsx(filepath=xlsx_file, data=csv_file)

def get_city_and_region_id(city):
    data = requests.get(f"https://www.olx.pl/api/v1/friendly-links/query-params/nieruchomosci,mieszkania,{city}/").json()
    print({
        "region": str(data["data"]["region_id"]), 
        "city": str(data["data"]["city_id"])
    })
    return {
        "region": str(data["data"]["region_id"]), 
        "city": str(data["data"]["city_id"])
    }

def scrape(city, filepath):
    counter = 0
    iterations = 0
    ids = get_city_and_region_id(city)
    city_id = ids["city"]
    region_id = ids["region"]
    for x in range(0, 500, 40):
        data = requests.get(f"https://www.olx.pl/api/v1/offers/?offset={x}&limit=40&category_id=1307&region_id={region_id}&city_id={city_id}").json()["data"]
        iterations += 1
        for line in data:
            url = line["url"]
            external_url = line["external_url"] if "external_url" in line else "brak"
            title = line["title"]
            if line["params"] is not None or "":
                for param in line["params"]:
                    key = param["key"]
                    if key == "furniture":
                        umeblowane = "tak" if param["value"]["key"] == "yes" else "nie"
                    if key == "floor_select":
                        pietro = param["value"]["label"] if param["value"]["label"] is not None or "" else "nieznane"
                    if key == "price":
                        cena = param["value"]["label"]
                    if key == "builttype":
                        zabudowa = param["value"]["label"] if param["value"]["label"] is not None or "" else "nieznane"
                    if key == "m":
                        powierzchnia = param["value"]["label"] if param["value"]["label"] is not None or "" else "nieznane"
                    if key == "rooms":
                        liczba_pokoi = param["value"]["label"] if param["value"]["label"] is not None or "" else "nieznane"
                if line["description"] is not None or "":
                    zwierzeta = False
                    if any(keyword in line["description"] for keyword in ("zwierzęta", "zwierzętom", "zwierząt", "pieski", "psy", "pies", "psem", "zwierzęciu", "zwierz")):
                        zwierzeta = True
            save_to_csv(filepath=filepath, data=[title, powierzchnia, liczba_pokoi, zwierzeta, cena, pietro, zabudowa, umeblowane, url, external_url])
            counter += 1
    print(f"ended scraping {city}. scraped {counter} flats in {iterations} iterations")

def get_env_ready(output_dir, csv_path):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print("Directory created.")
    else:
        print("Directory already exists. Exiting.")
    
    if not os.path.exists(csv_path):
        with open(file=csv_path, mode="w") as file:
            writer = csv.writer(file)
            writer.writerow(["tytul", "powierzchnia", "liczba pokoi", "zwierzeta", "cena", "pietro", "zabudowa", "umeblowane", "link", "link zewnetrzny"])
    else:
        os.remove(csv_path)
        with open(file=csv_path, mode="w") as file:
            writer = csv.writer(file)
            writer.writerow(["tytul", "powierzchnia", "liczba pokoi", "zwierzeta", "cena", "pietro", "zabudowa", "umeblowane", "link", "link zewnetrzny"])

def save_to_csv(filepath, data):
    with open(file=filepath, mode="a") as file:
        writer = csv.writer(file)
        writer.writerow(data)
    print(f"Written data to {filepath}")

def save_to_xlsx(filepath, data):
    read_file = pd.read_csv(data)
    read_file.to_excel(filepath, index=None, header=True)
    print(f"Written data to {filepath}")

if __name__ == "__main__":
    main()