# RapisBus Kiosk Scraper
- A python script that scrapes bus routes and bus stops from the [MyRapid - BusKiosk website](https://myrapidbus.prasarana.com.my/kiosk)
- This script will generate CSV files containing bus routes geometries and bus stops coordinates.

## Usage
### Requirements
```
Python 3.10.4
```
### Setup
If you do not have the required libraries installed, you can do it by running command below in your terminal
```
pip3 install -r requirements.txt
```
### Steps
- To scrape all the regions, simply run
    ```
    python3 bus_kiosk_scraper.py
    ```
- You can scrape particular region(s). These are the regions that are available:
    ```
    kl
    penang
    kuantan
    putrajaya
    ```
  - For example, to scrape "penang" and "kuantan" regions, simply run
    ```
    python3 bus_kiosk_scraper.py penang kuantan
    ```
- After scraping, two CSV files (bus routes and bus stops) for each region will be saved in the `tmp` directory
