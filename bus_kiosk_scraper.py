"""
This scraper scrapes all the bus routes and bus stops information from MyRapid Bus Kiosk website
"""
import sys
import time
import re
import csv
import json
import requests
from bs4 import BeautifulSoup
from shapely.geometry import LineString
from shapely.ops import transform

URL = "https://myrapidbus.prasarana.com.my/kiosk"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/111.0",
}

REGIONS = {
    "kl": "rkl",
    "penang": "rpg",
    "kuantan": "rkn",
    "putrajaya": "rkl-putrajaya",
}


def query(url):
    time.sleep(2)  # prevent abuse
    rsp = requests.get(url, headers=HEADERS)

    if rsp.status_code != 200:
        return None

    return BeautifulSoup(rsp.text, "html.parser")


def get_dict(region):
    return {k: v for k, v in REGIONS.items() if k in region}


def extract(regions=None):
    areas = get_dict(regions) if regions else REGIONS
    print(f'Regions to scrape: {list(areas.keys())}')
    for area in areas:
        print(f'Scraping region: {area}')
        url = URL + "/" + REGIONS[area]
        soup = query(url)
        route_lst = parse_routes(soup)

        header = route_lst.pop(0)
        routes = {}
        for d in route_lst:
            routes.update(d)

        rt_data = []
        bstp_data = []
        for i in routes.items():
            route_id = str(i[0])
            route_no = str(i[-1])
            # print(f'scraping route no: {route_no}')

            route_soup = query(url + "?route=" + route_id)
            (rt, bstp) = get_route_info(route_soup)
            for item in rt:
                item["route_id"] = route_id
                item["route_no"] = route_no  # add route number
                item["region"] = area
            for item in bstp:
                item["route_no"] = route_no  # add route number
                item["region"] = area
            rt_data += rt
            bstp_data += bstp

        tmstmp = int(time.time())
        suffix = f'{area}_{tmstmp}'
        print('Exporting files')
        write_to_csv(f'routes_{suffix}', rt_data)
        write_to_csv(f'bus_stops_{suffix}', bstp_data)


def write_to_csv(filename, lst):
    print(lst)
    header = list(lst[0].keys())
    with open(f"tmp/{filename}.csv", "w", encoding="UTF8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(lst)


def parse_routes(soup):
    options = soup.select_one('select[id="route"]').select("option")
    return [
        dict(zip([x.get("value")], [x.text])) for x in options
    ]  # list of dicts like so [{route_id: route_name}]


def get_route_info(soup):
    # collect routes shape and busstops coordinate
    script_str = soup.find_all("script", type="text/javascript")[2].text
    route_lst = get_route_shape(script_str)
    bstop_lst = get_route_bus_stops(script_str)
    return route_lst, bstop_lst


def get_route_shape(str):
    try:
        substr = re.search("const rawShapes = \$.parseJSON\(`(.+?)`\);", str).group(1)
    except AttributeError:
        substr = ""
    raw_shapes = json.loads(substr)
    if type(raw_shapes) is dict:
        inbound = raw_shapes.get("02", [])
        outbound = raw_shapes.get("01", [])
        # shapely
        inverted_linestr = LineString(inbound + outbound)
        linestr = transform(lambda x, y: (y, x), inverted_linestr).wkt  # EPSG:4326
    else:
        linestr = ""
    return parse_route_data(linestr)


def parse_route_data(lstr):
    return [{"geometry": lstr}]


def get_route_bus_stops(str):
    try:
        substr = re.search("var bstp = (.+?);", str).group(1)
    except AttributeError:
        substr = ""
    bstp = json.loads(substr)  # list of dictionaries
    return parse_bstp_data(bstp)


def parse_bstp_data(lst):
    # rename keys
    for d in lst:
        d["latitude"] = d.pop("lat")
        d["longitude"] = d.pop("lng")
    return lst


if __name__ == "__main__":
    arg = sys.argv[1:] or None
    extract(arg)
