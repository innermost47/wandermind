from llama_cpp import Llama
from services.tts import text_to_speech_to_file
from dotenv import load_dotenv
import os

load_dotenv()

llm = Llama(
    model_path=os.environ.get("LLM_MODEL"),
    n_ctx=int(os.environ.get("N_CTX_SIZE")),
    n_gpu_layers=int(os.environ.get("N_GPU_LAYERS")),
)


def query_llm(prompt, context, lock, session_memory):
    with lock:
        if not context or context.strip() == "":
            auto_message = "We couldn't find any relevant information for this location. Please try another place."

            yield {"text": auto_message, "audio": None}
            return
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
            + session_memory[-8:]
            + [
                {
                    "role": "user",
                    "content": prompt,
                },
            ]
        )
        output = llm.create_chat_completion(
            messages=messages,
            stream=True,
        )
        buffer = ""
        content = ""
        for chunk in output:
            delta = chunk["choices"][0]["delta"]
            if "content" in delta:
                yield {"text": delta["content"], "audio": None}
                buffer += delta["content"]
                content += delta["content"]

                if any(char in ".,;?!:" for char in delta["content"]):
                    audio_file_path = text_to_speech_to_file(buffer)
                    buffer = ""
                    yield {"text": None, "audio": audio_file_path}

        if buffer.strip():
            audio_file_path = text_to_speech_to_file(buffer)
            yield {"text": None, "audio": audio_file_path}
        session_memory.append({"role": "user", "content": prompt})
        session_memory.append({"role": "assistant", "content": content})
