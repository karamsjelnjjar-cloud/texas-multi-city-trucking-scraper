# 🤠 Texas Multi-City Trucking Companies Scraper & Analytics Pipeline

An advanced, enterprise-grade asynchronous web scraping and data analytics pipeline built with **Python**, **Playwright (Async API)**, **Asyncio**, and **Pandas**. It automatically discovers and extracts data across multiple cities in Texas (covering top cities alphabetically from A to Z), parses detailed fleet metrics using Regular Expressions, aggregates regional analytics, and exports structured multi-sheet Excel reports.

## 🚀 Key Features
- **Alphabetical Multi-City Discovery:** Automatically parses the main Texas transport directory, systematically selecting top cities for every letter from A to Z.
- **Asynchronous Concurrency (`asyncio`):** Employs non-blocking browser sessions and semaphore rate-limiting (`asyncio.Semaphore`) to efficiently crawl thousands of records without server blocks.
- **Robust Regex Data Extraction:** Uses precise Regular Expressions (`re`) to extract company names, phone numbers, USDOT identifiers, fleet sizes, and driver counts from unstructured web pages.
- **Advanced Data Aggregation & Excel Export:** Cleans, sorts, and organizes data using `Pandas`, generating a multi-sheet Excel workbook (`texas_trucks_analysis.xlsx`) featuring sorted company registries and city-level fleet summaries.

## 🛠️ Built With
- **Python 3.x**
- **Playwright (Async API)** (High-speed Asynchronous Browser Automation)
- **Asyncio & Re** (Concurrency Management & Pattern Matching)
- **Pandas & OpenPyXL** (Multi-sheet Data Processing & Excel Export)

## ⚙️ How to Run
1. Clone the repository:
   ```bash
   git clone [https://github.com/karamsjelnjjar-cloud/texas-multi-city-trucking-scraper.git](https://github.com/karamsjelnjjar-cloud/texas-multi-city-trucking-scraper.git)
