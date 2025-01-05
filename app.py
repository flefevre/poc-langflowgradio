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
FLOW_ID = "4f190944-89fc-4d92-9a0d-0d5f9a9d7e7e"
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

def extract_messages_by_component_ids(json_data, component_ids):
    """
    Extrait les valeurs de l'attribut 'message' pour une liste de component_id donnée.

    Args:
        json_data (dict): Le JSON des données.
        component_ids (list): La liste des component_id à rechercher.

    Returns:
        dict: Un dictionnaire avec chaque component_id trouvé comme clé et le message correspondant comme valeur.
              Si un component_id n'est pas trouvé, sa valeur sera None.
    """ 
    bresults = {component_id: None for component_id in component_ids}  # Initialisation du dictionnaire des résultats

    # Parcourir les données JSON
    for output in json_data.get("outputs", []):
        for result in output.get("outputs", []):
            # Vérifier si le component_id correspond
            component_id = result.get("component_id")
            if component_id in component_ids:
                # Récupérer le message correspondant
                for message_data in result.get("messages", []):
                    bresults[component_id] = message_data.get("message")
    
    return bresults

class UploadError(Exception):
    """Raised when an error occurs during the upload process."""


def upload(file_path: str, host: str, flow_id: str):
    """Upload a file to Langflow and return the file path."""
    url = f"{host}/api/v1/upload/{flow_id}"
    try:
        with Path(file_path).open("rb") as file:
            logger.info(f"Tentative d'upload du fichier : {file_path} vers {url}")
            response = httpx.post(url, files={"file": file}, timeout=10)
            logger.info(f"Statut de la réponse : {response.status_code}")
            if response.status_code in {httpx.codes.OK, httpx.codes.CREATED}:
                logger.info(f"Réponse : {response.json()}")
                return response.json()
            else:
                logger.error(f"Erreur API : {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"Exception lors de l'upload : {e}")
        raise UploadError(f"Error uploading file: {e}")
    raise UploadError(f"Error uploading file: {response.status_code}")


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
                tweaks[component] = {"path": response["file_path"]}
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
    if file is not None:
        try:
            logger.info("before la")
            tweaks = upload_file(
                file_path=file.name,
                host=BASE_API_URL,
                flow_id=FLOW_ID,
                components=["File-ryvgU"],
                tweaks=TWEAKS
            )
        except Exception as e:
            return f"Erreur lors du téléchargement du fichier : {e}"
    else:
        return "Veuillez fournir un fichier."
    api_url = f"{BASE_API_URL}/api/v1/run/{ENDPOINT}"
    
    payload = {
        #"input_value": "",  # La valeur d'entrée sera définie par le fichier uploadé
        "output_type": "chat",
        "input_type": "chat",
        "tweaks": tweaks
    }

    headers = {"x-api-key": API_KEY}
    try:
        response = requests.post(api_url, json=payload, headers=headers)
        if response.status_code != 200:
            return f"Erreur API : {response.status_code} - {response.text}"

        response_json = response.json()
        #logger.info(json.dumps(response_json, indent=4, ensure_ascii=False))
        
        #"TextOutput-T0rBI", "TextOutput-akHaI", "TextOutput-H2BGi", 
        component_ids = ["TextOutput-VMHD2"]
        outputs = extract_messages_by_component_ids(response_json, component_ids)
        
        return outputs["TextOutput-VMHD2"]

    except requests.exceptions.RequestException as e:
        return f"Erreur lors de la requête : {e}"

# Interface Gradio
with gr.Blocks() as interface:
    gr.Markdown("### Resume Service IA ")

    with gr.Row():
        inputfile = gr.File(label="File to upload", type="filepath")

    with gr.Row():
        output_text_1 = gr.Textbox(label="Resume", lines=10, interactive=False, show_label=True, show_copy_button=True)

    send_button = gr.Button("Send")
    send_button.click(fn=run_flow, inputs=[inputfile], outputs=[output_text_1])

# Lancer Gradio
if __name__ == "__main__":    
    logger.info("Démarrage de l'application Gradio...")
    interface.launch(server_name="0.0.0.0", server_port=7870, show_error=True)


