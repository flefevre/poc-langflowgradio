import gradio as gr
import requests
import json
import warnings
import logging
from pathlib import Path

import httpx
# try:
#     from langflow.load import upload_file
# except ImportError:
#     warnings.warn("Langflow provides a function to help you upload files to the flow. Please install langflow to use it.")
#     upload_file = None

# Configuration de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



# Configuration de base
API_KEY = "sk-LxnvoTxVgyHpFTPl_2Uzds4OafRt50MUsJiGduB_HOw"  # Remplacez par votre clé API Langflow
#BASE_API_URL = "https://langflow2.dev.localhost/"
BASE_API_URL = "http://langflow2:7860"
ENDPOINT = "qaflow"  # Nom de l'endpoint
TWEAKS = {
  "ChatInput-9TNL9": {
    "files": "",
    "background_color": "",
    "chat_icon": "",
    "input_value": "Fais moi un résumé de ce document en français",
    "sender": "User",
    "sender_name": "User",
    "session_id": "",
    "should_store_message": True,
    "text_color": ""
  },
  "ParseData-H8Oyb": {
    "sep": "\n",
    "template": "{text}"
  },
  "File-ryvgU": {
    "path": "",
    "concurrency_multithreading": 4,
    "silent_errors": False,
    "use_multithreading": False
  },
  "Prompt-Inllc": {
    "template": "Answer user's questions based on the document below:\n\n---\n\n{Document}\n\n---\n\nQuestion: fais moi un résumé en français",
    "Document": ""
  },
  "OllamaModel-2aJB2": {
    "base_url": "http://ollama:11444",
    "format": "",
    "input_value": "",
    "metadata": {},
    "mirostat": "Disabled",
    "mirostat_eta": None,
    "mirostat_tau": None,
    "model_name": "llama3.2:3b",
    "num_ctx": None,
    "num_gpu": None,
    "num_thread": None,
    "repeat_last_n": None,
    "repeat_penalty": None,
    "stop_tokens": "",
    "stream": False,
    "system": "",
    "system_message": "",
    "tags": "",
    "temperature": 0,
    "template": "",
    "tfs_z": None,
    "timeout": None,
    "top_k": None,
    "top_p": None,
    "verbose": False
  },
  "TextOutput-VMHD2": {
    "input_value": ""
  }
}


class UploadError(Exception):
    """Raised when an error occurs during the upload process."""


def upload(file_path: str, host: str, flow_id: str):
    """Upload a file to Langflow and return the file path.

    Args:
        file_path (str): The path to the file to be uploaded.
        host (str): The host URL of Langflow.
        flow_id (UUID): The ID of the flow to which the file belongs.

    Returns:
        dict: A dictionary containing the file path.

    Raises:
        UploadError: If an error occurs during the upload process.
    """
    try:
        url = f"{host}/api/v1/upload/{flow_id}"
        with Path(file_path).open("rb") as file:
            response = httpx.post(url, files={"file": file})
            if response.status_code in {httpx.codes.OK, httpx.codes.CREATED}:
                return response.json()
    except Exception as e:
        msg = f"Error uploading file: {e}"
        raise UploadError(msg) from e

    msg = f"Error uploading file: {response.status_code}"
    raise UploadError(msg)


def upload_file(file_path: str, host: str, flow_id: str, components: list[str], tweaks: dict | None = None):
    """Upload a file to Langflow and return the file path.

    Args:
        file_path (str): The path to the file to be uploaded.
        host (str): The host URL of Langflow.
        port (int): The port number of Langflow.
        flow_id (UUID): The ID of the flow to which the file belongs.
        components (str): List of component IDs or names that need the file.
        tweaks (dict): A dictionary of tweaks to be applied to the file.

    Returns:
        dict: A dictionary containing the file path and any tweaks that were applied.

    Raises:
        UploadError: If an error occurs during the upload process.
    """
    try:
        response = upload(file_path, host, flow_id)
    except Exception as e:
        msg = f"Error uploading file: {e}"
        raise UploadError(msg) from e

    if not tweaks:
        tweaks = {}
    if response["file_path"]:
        for component in components:
            if isinstance(component, str):
                tweaks[component] = {"path": responupload_filese["file_path"]}
            else:
                msg = f"Error uploading file: component ID or name must be a string. Got {type(component)}"
                raise UploadError(msg)
        return tweaks

    msg = "Error uploading file"
    raise UploadError(msg)

def run_flow(file):
    """
    Fonction pour exécuter un workflow Langflow à partir d'un fichier donné.
    """
    # if file is not None:
    #     try:
    #         # Mettre à jour le chemin du fichier dans les tweaks
    #         TWEAKS["File-ryvgU"]["path"] = file.name
    #         #TWEAKS["ChatInput-9TNL9"]["input_value"] = ""
    #         logger.info(f"file {file.name}")
    #         api_url = f"{BASE_API_URL}/api/v1/run/{ENDPOINT}"
    #         payload = {
    #             #"input_value": "ChatInput-9TNL9",  # La valeur d'entrée sera définie par le fichier uploadé
    #             "output_type": "chat",
    #             "input_type": "chat",
    #             "tweaks": TWEAKS
    #         }

    #         headers = {"x-api-key": API_KEY}
    #         logger.info("Envoi de la requête à l'API...")

    #         response = requests.post(api_url, json=payload, headers=headers)

    #         if response.status_code != 200:
    #             return f"Erreur API : {response.status_code} - {response.text}"

    #         response_json = response.json()

    #         # Retourner une réponse formatée
    #         return json.dumps(response_json, indent=4, ensure_ascii=False)

    #     except Exception as e:
    #         return f"Erreur lors du traitement du fichier : {e}"

    # else:
    #     return "Veuillez fournir un fichier."
      
    logger.info("ici")
    if file is not None:
        try:
            logger.info("before la")
            tweaks = upload_file(
                file_path=file.name,
                host=BASE_API_URL,
                flow_id=ENDPOINT,
                components=["File-ryvgU"],
                tweaks=TWEAKS
            )
            logger.info("la")
        except Exception as e:
            return f"Erreur lors du téléchargement du fichier : {e}"
    else:
        return "Veuillez fournir un fichier."
    logger.info("go")
    api_url = f"{BASE_API_URL}/api/v1/run/{ENDPOINT}"
    
    payload = {
        "input_value": "",  # La valeur d'entrée sera définie par le fichier uploadé
        "output_type": "chat",
        "input_type": "chat",
        "tweaks": tweaks
    }
    
    # "input_value": inputs.get("ChatInput-lbGcg", ""),
    #     "output_type": "chat",
    #     "input_type": "chat",
    #     "tweaks": TWEAKS

    headers = {"x-api-key": API_KEY}
    logger.info("go2")
    try:
        response = requests.post(api_url, json=payload, headers=headers)
        logger.info("go3")
        if response.status_code != 200:
            return f"Erreur API : {response.status_code} - {response.text}"

        response_json = response.json()

        # Retourner une réponse formatée
        return json.dumps(response_json, indent=4, ensure_ascii=False)

    except requests.exceptions.RequestException as e:
        return f"Erreur lors de la requête : {e}"

# Interface Gradio
with gr.Blocks() as interface:
    gr.Markdown("### Interface Langflow avec Gradio")

    with gr.Row():
        inputfile = gr.File(label="Fichier à envoyer", type="filepath")

    with gr.Row():
        output_text_1 = gr.Textbox(label="Résultat", lines=10, interactive=False)

    send_button = gr.Button("Envoyer")
    send_button.click(fn=run_flow, inputs=[inputfile], outputs=[output_text_1])

# Lancer Gradio
if __name__ == "__main__":    
    logger.info("Démarrage de l'application Gradio...")
    interface.launch(server_name="0.0.0.0", server_port=7870, show_error=True)


