import requests


def get_wikipedia_data(lat, lon):
    url = f"https://fr.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "geosearch",
        "gscoord": f"{lat}|{lon}",
        "gsradius": 1000,
        "gslimit": 1,
        "format": "json",
    }
    response = requests.get(url, params=params, verify=False)
    if response.status_code == 200:
        data = response.json()
        if data["query"]["geosearch"]:
            page_id = data["query"]["geosearch"][0]["pageid"]
            return get_wikipedia_page(page_id)
    return None


def get_wikipedia_page(page_id):
    url = f"https://fr.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "pageids": page_id,
        "prop": "extracts",
        "explaintext": True,
        "format": "json",
    }
    response = requests.get(url, params=params, verify=False)
    if response.status_code == 200:
        page = response.json()
        return page["query"]["pages"][str(page_id)]["extract"]
    return None
