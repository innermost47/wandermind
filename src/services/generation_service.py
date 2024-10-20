from fastapi.responses import StreamingResponse
from src.utils import (
    get_foursquare_data,
    LLMUtils,
    get_wikipedia_data,
    get_nearby_events,
    text_to_speech_to_memory,
)
import json
import asyncio
from src.schemas import GenerateSchema


class GenerationService:
    def __init__(self):
        self.llm_utils = LLMUtils()

    async def generate(
        self,
        generate_schema: GenerateSchema,
    ):
        if (
            generate_schema.latitude
            and generate_schema.longitude
            and not generate_schema.context
        ):
            prompt = generate_schema.prompt
            if generate_schema.category:
                if generate_schema.category == "wikipedia":
                    context = await get_wikipedia_data(
                        latitude=generate_schema.latitude,
                        longitude=generate_schema.longitude,
                    )
                    prompt = (
                        "Présentez ce lieu comme un guide touristique réel, similaire à ceux que l'on trouve dans les sorties touristiques, "
                        "et non comme un livre ou un document informatif. Fournissez une description vivante et engageante qui attire "
                        "l'attention des visiteurs et leur donne envie d'explorer cet endroit."
                    )
                elif generate_schema.category == "events":
                    context = await get_nearby_events(
                        latitude=generate_schema.latitude,
                        longitude=generate_schema.longitude,
                    )
                    prompt = "L'utilisateur souhaite obtenir plus de détails sur les événements suivants. Pour chaque événement, donne une description complète en incluant le titre, la date, le lieu, et une brève description de l'événement. Si disponible, précise également des informations supplémentaires telles que la durée, les horaires, et d'autres détails pertinents si ils sont fournis dans le contexte."
                else:
                    context = await get_foursquare_data(
                        latitude=generate_schema.latitude,
                        longitude=generate_schema.longitude,
                        radius=generate_schema.radius,
                        category=generate_schema.category,
                    )
                    if generate_schema.category == "19014,19012,19013,19006":
                        prompt = "L'utilisateur veut davantage d'informations sur ces hébergements. Fournis-lui une description basée sur les données disponibles."
                    elif generate_schema.category == "10027,10023,10034,10032":
                        prompt = "L'utilisateur veut davantage d'informations sur ces lieux culturels. Les catégories sont les suivantes : 10027 pour les musées, 10023 pour les galeries d'art, 10034 pour les lieux historiques, et 10032 pour les bibliothèques.Fournis-lui une description basée sur les données disponibles."
            elif generate_schema.query:
                context = await get_foursquare_data(
                    latitude=generate_schema.latitude,
                    longitude=generate_schema.longitude,
                    radius=generate_schema.radius,
                    query=generate_schema.query,
                )
                if generate_schema.query == "restaurants":
                    prompt = "L'utilisateur veut davantage d'informations sur ces restaurants. Fournis-lui une description basée sur les données disponibles."
        elif (
            generate_schema.context
            and not generate_schema.latitude
            and not generate_schema.longitude
        ):
            context = generate_schema.context
            prompt = generate_schema.prompt
        else:
            return {
                "error": "No location context available. Please select a location first."
            }

        async def generate(generate_schema: GenerateSchema):
            async for chunk in self.llm_utils.query(
                prompt,
                context,
                generate_schema.memory,
            ):
                data = json.dumps(chunk).encode("utf-8") + b"<|end_of_chunk|>"
                yield data
                if "buffer" in chunk:
                    audio_buffer = await text_to_speech_to_memory(chunk["buffer"])
                    yield json.dumps(
                        {
                            "text": None,
                            "audio": audio_buffer,
                            "context": None,
                        }
                    ).encode("utf-8") + b"<|end_of_chunk|>"
                await asyncio.sleep(0)

        return StreamingResponse(
            generate(generate_schema), media_type="text/event-stream"
        )
