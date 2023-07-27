import csv
import json
import requests

from bs4 import BeautifulSoup


URL_MSK = "https://msk.sushi-market.com/"
URL_EKB = "https://ekb.sushi-market.com/"
URL_SPB = "https://spb.sushi-market.com/"


def get_kits_from_scr(scr: str) -> list[dict]:
    group_name: str = "Наборы"
    prefix = "window.productGroups = "
    postfix = ";"
    soup = BeautifulSoup(scr, "lxml")

    product_groups_raw = soup.find("div", id="app").find_next_sibling().string
    start = product_groups_raw.find(prefix)
    product_groups_raw = product_groups_raw[start + len(prefix):]
    end = product_groups_raw.find(postfix)
    product_groups_raw = product_groups_raw[:end]
    product_groups_dict: dict = json.loads(product_groups_raw)

    for group in product_groups_dict.values():
        if group["name"] == group_name:
            return group["products"]


def get_price_per_kg_dict(kits: list[dict]) -> dict[float, dict]:
    return {kit["price"] / kit["weight"]["value"] * (1 if kit["weight"]["unit"] == "кг" else 1000): kit for kit in kits}


def parse_kits(url: str, file_name: str) -> None:
    headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/114.0.0.0 Safari/537.36 OPR/100.0.0.0"}
    scr = requests.get(url, headers=headers).text

    kits = get_kits_from_scr(scr)
    price_per_kg_dict = get_price_per_kg_dict(kits)

    with open(file_name, "w", encoding="utf-8", newline="") as fout:
        columns = ("price_per_kg", "name", "price", "weight")
        writer = csv.writer(fout)
        writer.writerow(columns)
        for price_per_kg in sorted(price_per_kg_dict):
            kit: dict = price_per_kg_dict[price_per_kg]
            row = price_per_kg, kit["name"], kit["price"], kit["weight"]["value"] / (
                1 if kit["weight"]["unit"] == "кг" else 1000)
            writer.writerow(row)


if __name__ == '__main__':
    parse_kits(URL_MSK, "data/msk.csv")
    parse_kits(URL_EKB, "data/ekb.csv")
    parse_kits(URL_SPB, "data/spb.csv")
