
from pathlib import Path
from urllib.parse import urljoin
import time
import sqlite3

import requests
import pandas as pd
from bs4 import BeautifulSoup

import config


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output_1000"
MAX_PAGES = 50  # Test 2 pages first
BOOKS_PER_PAGE = 20

RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}


def extract():
    all_books = []

    with requests.Session() as session:
        session.headers.update(config.HEADERS)

        for page in range(1, MAX_PAGES + 1):
            url = urljoin(
                config.BASE_URL,
                f"catalogue/page-{page}.html"
            )

            response = session.get(url, timeout=20)
            response.raise_for_status()
            response.encoding = "utf-8"

            soup = BeautifulSoup(
                response.text, "html.parser"
            )

            books = soup.select("article.product_pod")

            if len(books) != BOOKS_PER_PAGE:
                raise ValueError(
                    f"Page {page}: expected 20 books, "
                    f"got {len(books)}"
                )

            for book in books:
                title = book.select_one("h3 a")
                price = book.select_one("p.price_color")
                status = book.select_one(
                    "p.instock.availability"
                )
                rating = book.select_one("p.star-rating")

                if not all([title, price, status, rating]):
                    raise ValueError(
                        f"Missing fields on page {page}"
                    )

                rating_word = next(
                    (name for name in RATING_MAP
                     if name in rating.get("class", [])),
                    None
                )

                if rating_word is None:
                    raise ValueError("Unknown rating")

                all_books.append({
                    "Title": title.get("title", "").strip(),
                    "Price": price.get_text(strip=True),
                    "Status": status.get_text(strip=True),
                    "Rating": RATING_MAP[rating_word]
                })

            print(f"Page {page}: {len(books)} books collected")
            time.sleep(1)

    return all_books


def transform(books):
    df = pd.DataFrame(books)

    df["Price"] = (
        df["Price"]
        .str.replace("£", "", regex=False)
        .astype(float)
    )

    if df.isna().any().any():
        raise ValueError("Missing values detected")

    if df.duplicated().any():
        raise ValueError("Duplicate rows detected")

    if not df["Rating"].between(1, 5).all():
        raise ValueError("Invalid ratings")

    if not df["Price"].gt(0).all():
        raise ValueError("Invalid prices")

    expected = MAX_PAGES * BOOKS_PER_PAGE

    if len(df) != expected:
        raise ValueError(
            f"Expected {expected} books, got {len(df)}"
        )

    return df


def load(df):
    OUTPUT_DIR.mkdir(exist_ok=True)

    df.to_csv(
        OUTPUT_DIR / "books_data.csv",
        index=False,
        encoding="utf-8-sig"
    )

    df.to_excel(
        OUTPUT_DIR / "books_data.xlsx",
        index=False
    )

    df.to_json(
        OUTPUT_DIR / "books_data.json",
        orient="records",
        force_ascii=False,
        indent=4
    )

    with sqlite3.connect(
        OUTPUT_DIR / "books.db"
    ) as connection:
        df.to_sql(
            "books",
            connection,
            if_exists="replace",
            index=False
        )

    print(f"PASS: {len(df)} books validated")
    print("Exported: CSV, Excel, JSON, SQLite")
    print(f"Output directory: {OUTPUT_DIR}")


def main():
    books = extract()
    cleaned = transform(books)
    load(cleaned)


if __name__ == "__main__":
    main()
