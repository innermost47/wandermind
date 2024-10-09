import requests
from dotenv import load_dotenv
import os

load_dotenv()


def get_foursquare_data(latitude, longitude, radius=1000, query=None, category=None):
    url = "https://api.foursquare.com/v3/places/search"

    params = {
        "ll": f"{latitude},{longitude}",
        "radius": radius,
        "limit": 10,
    }

    if query:
        params["query"] = query
    if category:
        params["categories"] = category

    headers = {"Authorization": os.environ.get("FOURSQUARE_API_KEY")}
    verify = True if os.environ.get("VERIFY") == "True" else False
    response = requests.get(url, params=params, headers=headers, verify=verify)

    if response.status_code == 200:
        items = response.json().get("results", [])
        formatted_text = []
        if items:
            for item in items:
                formatted_text.append(format_for_llm(item))

        if formatted_text:
            return "\n".join(formatted_text)
        else:
            return f"No places were found nearby."
    else:
        print(f"Error while making Foursquare request: {response.status_code}")
        return None


def format_for_llm(item):
    name = item.get("name", "Nom inconnu")
    address = item["location"].get("formatted_address", "Adresse non disponible")
    distance = item.get("distance", "Distance inconnue")
    categories = ", ".join([category["name"] for category in item["categories"]])
    hours = item.get("hours", {}).get("display", "Horaires non disponibles")
    rating = item.get("rating", "Note non disponible")
    formatted_info = (
        f"item : {name}\n"
        f"Adresse : {address}\n"
        f"Distance : {distance} mètres\n"
        f"Catégorie : {categories}\n"
        f"Horaires : {hours}\n"
        f"Note : {rating}/5\n"
        f"-----------------------------"
    )
    return formatted_info
