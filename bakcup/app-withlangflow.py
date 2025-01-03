import gradio as gr
import requests
import json
import warnings
import logging

# Configuration de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from langflow.load import upload_file
except ImportError:
    warnings.warn("Langflow provides a function to help you upload files to the flow. Please install langflow to use it.")
    upload_file = None

# Configuration de base
API_KEY = "sk-LxnvoTxVgyHpFTPl_2Uzds4OafRt50MUsJiGduB_HOw"  # Remplacez par votre clé API Langflow
BASE_API_URL = "https://langflow2.dev.localhost/"
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

def run_flow(file):
    """
    Fonction pour exécuter un workflow Langflow à partir d'un fichier donné.
    """
    if not upload_file:
        return "Langflow n'est pas installé. Veuillez l'installer pour utiliser cette fonctionnalité."

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


