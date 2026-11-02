import os

BASE_URL = "https://books.toscrape.com/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


CSV_FILEPATH = os.path.join(OUTPUT_DIR, "books_data.csv")
EXCEL_FILEPATH = os.path.join(OUTPUT_DIR, "books_data.xlsx")
JSON_FILEPATH = os.path.join(OUTPUT_DIR, "books_data.json")


Rating_map = {"One": 1
            ,"Two": 2
            ,"Three": 3
            ,"Four": 4
            ,"Five": 5}