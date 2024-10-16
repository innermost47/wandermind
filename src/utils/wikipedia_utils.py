import httpx
from config import VERIFY


async def get_wikipedia_data(latitude, longitude):
    url = "https://fr.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "geosearch",
        "gscoord": f"{latitude}|{longitude}",
        "gsradius": 1000,
        "gslimit": 1,
        "format": "json",
    }
    async with httpx.AsyncClient(verify=VERIFY) as client:
        response = await client.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data["query"]["geosearch"]:
                page_id = data["query"]["geosearch"][0]["pageid"]
                return await get_wikipedia_page(page_id)
    return None


async def get_wikipedia_page(page_id):
    url = "https://fr.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "pageids": page_id,
        "prop": "extracts",
        "explaintext": True,
        "format": "json",
    }
    async with httpx.AsyncClient(verify=VERIFY) as client:
        response = await client.get(url, params=params)
        if response.status_code == 200:
            page = response.json()
            content = page["query"]["pages"][str(page_id)]["extract"]

            sections_to_remove = ["Notes et références", "Voir aussi", "Liens externes"]

            for section in sections_to_remove:
                if section in content:
                    content = content.split(section)[0]

            return content
    return None
