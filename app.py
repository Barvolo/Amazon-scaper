from socket import create_connection
from database.db import add_search_history, get_search_history, get_daily_search_count, increment_daily_search_count, update_last_search_prices
import datetime
import asyncio
from typing import List, Dict
from bs4 import BeautifulSoup
import aiohttp
import re
from fastapi import FastAPI, Request, Depends, HTTPException, Body
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import aiofiles
from pydantic import BaseModel
from sqlalchemy.orm import Session
import requests
from fastapi.templating import Jinja2Templates
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from requests_html import HTMLSession, AsyncHTMLSession

app = FastAPI()


app.mount("/static", StaticFiles(directory="static"), name="static")


conversion_rates = {
    "USD": 1,           # US Dollar
    "GBP": 1.32,        # British Pound
    "EUR": 1.17,        # Euro
    "CAD": 0.80,        # Canadian Dollar
}

prices_list = []

class SearchItemInput(BaseModel):
    query: str

@app.post("/search")
async def search(search_input: SearchItemInput):
    # Check if the daily search limit is reached
    today = datetime.date.today().strftime("%Y-%m-%d")
    search_count = get_daily_search_count(today)
    if search_count >= 10:
        raise HTTPException(status_code=400, detail="Daily searches cap reached. Consider upgrading to the premium service in order to search for more items.")
    
    # Perform the search and get the top 10 results
    results = await search_items(search_input.query)
    # Add the search to the search history
    if len(results) > 0:
        if "prices" in results[0]:
            add_search_history(search_input.query, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), results[0]["title"], results[0]["prices"])
        else:
            add_search_history(search_input.query, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), results[0]["title"], None)
    else:
        # Handle the case where there are no results
        raise HTTPException(status_code=404, detail="No results found.")
    # Increment the daily search count
    increment_daily_search_count(today)
    

    return results


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    async with aiofiles.open("static/index.html", mode="r") as f:
        content = await f.read()
    return HTMLResponse(content=content)


async def fetch(session: aiohttp.ClientSession, url: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.3",
        "Accept-Language": "en-US,en;q=0.9",
    }
    async with session.get(url, headers=headers) as response:
        return await response.text()


async def search_items(query: str) -> List[dict]:
    prices = {}
    search_url = f"https://www.amazon.com/s?k={query}"
    async with aiohttp.ClientSession() as session:
        html_content = await fetch(session, search_url)
        soup = BeautifulSoup(html_content, "html.parser")
        search_results = []
        for item in soup.select("div[data-asin]"):
            asin = item["data-asin"]
            title_tag = item.find("h2")
            if title_tag is None:
                continue
            title = title_tag.text.strip()
            image_url_tag = item.find("img")
            if image_url_tag is None:
                continue
            image_url = image_url_tag["src"]
            search_results.append({"title": title, "image_url": image_url, "asin": asin})

        return search_results[:10]
    

async def parse_item(session: aiohttp.ClientSession, site: str, url: str, currency: str):
    html = await fetch(session, url)
    soup = BeautifulSoup(html, "html.parser")

    item_name = soup.find(id="productTitle")
    if item_name:
        item_name = item_name.get_text(strip=True)
    else:
        item_name = None

    item_rating = soup.find(id="acrPopover")
    if item_rating:
        item_rating = float(item_rating.get("title").split()[0])
    else:
        item_rating = None

    price_element = soup.find("span", {"class": "a-price"})
    if price_element:
        price_amount = price_element.find("span", {"class": "a-price-whole"})
        price_fraction = price_element.find("span", {"class": "a-price-fraction"})

        if price_amount and price_fraction:
            price_whole = re.sub(r"[^\d]", "", price_amount.get_text())
            price_frac = re.sub(r"[^\d]", "", price_fraction.get_text())
            price = f"{price_whole}.{price_frac}"
        else:
            # Handle cases like Amazon.co.uk and Amazon.de where the price is in a single element
            price_offscreen = price_element.find("span", {"class": "a-offscreen"})
            if price_offscreen:
                price = re.sub(r"[^\d.,]", "", price_offscreen.get_text())
                # Replace comma with a period for European number formats
                price = price.replace(",", ".")
            else:
                # Check for hidden input element with the price
                price_input = soup.find("input", {"id": "twister-plus-price-data-price"})
                if price_input:
                    price = price_input.get("value")
                else:
                    print("Price not found")
                    price = None

        if price:
            price = round(float(price) * conversion_rates[currency], 2)
            
    else:
        price = None
    
    prices_list.append(price)
    if len(prices_list) == 4:
        print(prices_list)
        update_last_search_prices(prices_list)
        prices_list.clear()

    return {
        "Item": item_name,
        "Rating": item_rating,
        "Price": price,
        "url": url
} if item_name is not None else None


@app.get("/item/{asin}")
async def get_item(asin: str):
    amazon_sites = {
        "Amazon.com": {
            "url": f"https://www.amazon.com/dp/{asin}",
            "currency": "USD"
        },
        "Amazon.co.uk": {
            "url": f"https://www.amazon.co.uk/dp/{asin}",
            "currency": "GBP"
        }
        ,
        "Amazon.de": {
            "url": f"https://www.amazon.de/dp/{asin}",
            "currency": "EUR"
        },
        "Amazon.ca": {
            "url": f"https://www.amazon.ca/dp/{asin}",
            "currency": "CAD"
        }
    }

    item_data = {}
    async with aiohttp.ClientSession() as session:
        for site, data in amazon_sites.items():
            parsed_data = await parse_item(session, site, data["url"], data["currency"])
            if parsed_data is not None:
                item_data[site] = parsed_data

    return item_data

@app.post("/item", response_model=Dict[str, str])
async def item_route(asin: str) -> Dict[str, str]:
    item_data = await get_item(asin)
    if not item_data:
        raise HTTPException(status_code=404, detail="Item not found")
    return item_data

@app.post("/history")
def store_search_history(query: str, search_time: str, item_name: str, prices: dict):
    add_search_history(query, search_time, item_name, prices)
    return {"message": "Search history added successfully"}

@app.get("/search_limit")
def check_daily_search_limit():
    today = datetime.date.today().strftime("%Y-%m-%d")
    search_count = get_daily_search_count(today)
    return {"search_count": search_count}

@app.get("/item/{asin}")
async def item_details(asin: str):
    item_data = await get_item(asin)
    if not item_data:
        raise HTTPException(status_code=404, detail="Item not found")
    return item_data

@app.get("/past-searches")
def show_search_history():
    search_history = get_search_history()
    return search_history



if __name__ == "__main__":
    import uvicorn
    from database.db import init_db
    init_db()
    uvicorn.run(app, host="127.0.0.1", port=8009)


