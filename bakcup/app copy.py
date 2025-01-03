import gradio as gr
import requests

# Variables globales
API_KEY = "qaflow"
BASE_API_URL = "http://localhost:7860"
ENDPOINT = "qaflow"
TWEAKS = {
  "ChatInput-9TNL9": {},
  "ChatOutput-N74hH": {},
  "ParseData-H8Oyb": {},
  "File-ryvgU": {},
  "Prompt-Inllc": {},
  "OllamaModel-2aJB2": {}
}

def run_flow(file: UploadFile):
    """
    Fonction pour envoyer un message à Langflow et récupérer la réponse.
    """
    api_url = f"{BASE_API_URL}/api/v1/run/{ENDPOINT}"

    payload = {
        "input_value": message,
        "output_type": output_type,
        "input_type": input_type,
        "tweaks": tweaks
    }

    headers = {"x-api-key": api_key}

    try:
        # Envoi de la requête POST à l'API Langflow
        response = requests.post(api_url, json=payload, headers=headers)
        
        if response.status_code != 200:
            return f"Erreur API : {response.status_code} - {response.text}"

        # Décodage de la réponse JSON
        response_json = response.json()

        # Extraction du texte du message généré par l'IA
        message_text = response_json['outputs'][0]['outputs'][0]['results']['message']['text']
        
        return message_text

    except requests.exceptions.RequestException as e:
        # En cas d'erreur de requête
        return f"Erreur lors de la requête : {e}"

    except ValueError as ve:
        # En cas d'erreur de décodage JSON
        return f"Erreur de décodage JSON : {ve}"

def chat_with_flow(file):
    """
    Fonction pour gérer le chat avec Langflow.
    """
    return run_flow(file)

# Interface Gradio
with gr.Blocks() as interface:
    gr.Markdown("### Interface Langflow")
    
    gr.Markdown("### Interface Workflow Langflow avec Gradio")

    with gr.Row():
        inputFile_box = gr.File(label="File", show_label=True)
        
    with gr.Row():
        output_text_1 = gr.Textbox(label="Résumé du stage", show_label=True, show_copy_button=True)
    
    # Bouton d'envoi
    send_button = gr.Button("Envoyer")
    send_button.click(fn=chat_with_flow, inputs=inputFile_box, outputs=output_box)

# Lancer l'interface Gradio
interface.launch()
