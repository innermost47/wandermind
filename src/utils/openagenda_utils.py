import httpx
from config import API_KEYS, VERIFY
from datetime import datetime


async def get_region_from_coordinates(latitude, longitude):
    url = f"https://nominatim.openstreetmap.org/reverse?lat={latitude}&lon={longitude}&format=json"
    headers = {"User-Agent": "TouristGuideApp/1.0"}
    async with httpx.AsyncClient(verify=VERIFY) as client:
        response = await client.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data.get("address", {}).get("state", "Région inconnue")
        else:
            print(
                f"Erreur lors de la récupération de la région : {response.status_code}"
            )
            return None


async def get_agendas_by_region(region):
    url = "https://api.openagenda.com/v2/agendas"
    params = {
        "search": region,
        "key": API_KEYS["OPENAGENDA"],
    }
    async with httpx.AsyncClient(verify=VERIFY) as client:
        response = await client.get(url, params=params)
        if response.status_code == 200:
            return response.json().get("agendas", [])
        else:
            print(f"Erreur lors de la requête Open Agenda : {response.status_code}")
            return None


async def get_events_from_agenda(agenda_uid):
    url = f"https://api.openagenda.com/v2/agendas/{agenda_uid}/events"
    current_date = datetime.now().isoformat()
    params = {
        "detailed": 1,
        "timings[gte]": current_date,
        "size": 3,
        "key": API_KEYS["OPENAGENDA"],
    }
    async with httpx.AsyncClient(verify=VERIFY) as client:
        response = await client.get(url, params=params)
        if response.status_code == 200:
            return response.json().get("events", [])
        else:
            print(
                f"Erreur lors de la récupération des événements : {response.status_code}"
            )
            return None


async def get_nearby_events(latitude, longitude):
    region = await get_region_from_coordinates(latitude, longitude)
    agendas = await get_agendas_by_region(region)
    if not agendas:
        return "Aucun événement trouvé."
    formatted_text = []
    for agenda in agendas[:4]:
        agenda_uid = agenda["uid"]
        events = await get_events_from_agenda(agenda_uid)
        if events:
            for item in events:
                formatted_text.append(format_for_llm(item))

    if formatted_text:
        return "\n".join(formatted_text)
    else:
        return "Aucun événement trouvé."


def format_for_llm(event):
    name = event.get("title", "Nom de l'événement inconnu")
    start_date = event.get("dateRange", {}).get("start", "Date de début inconnue")
    venue_address = event.get("location", {}).get(
        "address", "Adresse du lieu non disponible"
    )
    venue_name = event.get("venue", {}).get("name", "Nom du lieu non disponible")
    description = event.get("description", "Description non disponible")

    formatted_event_info = (
        f"Événement : {name}\n"
        f"Date de début : {start_date}\n"
        f"Lieu : {venue_name}\n"
        f"Adresse : {venue_address}\n"
        f"Description : {description}\n"
        f"-----------------------------"
    )
    return formatted_event_info
