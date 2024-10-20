from .audio_utils import text_to_speech_to_memory
from config import LOCKS, LLAMA_CPP_API_URL
from typing import List
from openai import AsyncOpenAI


class LLMUtils:
    def __init__(self):
        self.client = None

    async def _init_client(self):
        if self.client is None:
            self.client = AsyncOpenAI(
                base_url=LLAMA_CPP_API_URL,
                api_key="wandermid",
            )

    async def _handle_llm_api_call(self, messages: List[dict]):
        try:
            await self._init_client()
            response = await self.client.chat.completions.create(
                model="wandermid",
                messages=messages,
                stream=True,
                temperature=0.7,
                top_p=0.9,
            )
            async for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            print(
                f"An unexpected error occured while trying to generate an answer: {e}"
            )

    async def query(
        self,
        prompt: str,
        context: str,
        memory: List[dict] = None,
    ):
        async with LOCKS["LLAMA"]:
            if not context or context.strip() == "":
                auto_message = "We couldn't find any relevant information for this location. Please try another place."
                yield {"text": auto_message, "audio": None, "context": None}
                return
            if not memory:
                memory = []
            messages = (
                [
                    {
                        "role": "system",
                        "content": f"""Vous jouez le rôle d'un guide touristique professionnel s'adressant à un seul individu. Vous devez répondre exclusivement en utilisant les informations contenues dans le contexte fourni. Vous n'êtes pas autorisé à inventer ou fournir des informations qui ne se trouvent pas dans ce contexte. Si la réponse à une question ne figure pas dans le contexte, vous devez poliment indiquer que vous ne pouvez pas répondre à la question avec les informations disponibles.

            Vous pouvez fournir des informations historiques, culturelles et pratiques concernant les lieux à visiter, les restaurants, les hôtels, ou d'autres informations touristiques utiles, mais uniquement si ces informations sont présentes dans le contexte fourni. Vous devez maintenir un ton engageant, informatif, et amical, tout en restant professionnel.

            Si une question n'est pas liée au tourisme ou au lieu, répondez poliment que vous ne traitez que des questions touristiques liées au lieu visité. Vous devez toujours répondre en français.

            Contexte : {context}""",
                    }
                ]
                + memory
                + [
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ]
            )
            output = self._handle_llm_api_call(messages=messages)

            buffer = ""
            content = ""
            async for chunk in output:
                yield {"text": chunk, "audio": None, "context": None}
                buffer += chunk
                content += chunk

                if len(buffer) >= 512 or any(char in ".?!" for char in chunk):
                    audio_buffer = await text_to_speech_to_memory(buffer)
                    buffer = ""
                    yield {
                        "text": None,
                        "audio": audio_buffer,
                        "context": None,
                    }

            if buffer.strip():
                audio_buffer = await text_to_speech_to_memory(buffer)
                yield {"text": None, "audio": audio_buffer, "context": None}
            yield {"text": None, "audio": None, "context": context}
