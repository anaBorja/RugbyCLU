from dotenv import load_dotenv
import os
import json
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations import ConversationAnalysisClient

def main():
    try:
        # Cargar variables de entorno
        load_dotenv()
        ls_prediction_endpoint = os.getenv('LS_CONVERSATIONS_ENDPOINT')
        ls_prediction_key = os.getenv('LS_CONVERSATIONS_KEY')

        # Crear cliente para Azure Language Service
        client = ConversationAnalysisClient(
            ls_prediction_endpoint, AzureKeyCredential(ls_prediction_key))

        # Bucle para recibir entradas del usuario
        while True:
            userText = input('\nEscribe tu pregunta sobre la Rugby World Cup 2027 ("salir" para terminar):\n')
            if userText.lower() == 'salir':
                break

            # Consultar el modelo de Azure AI
            cls_project = 'RugbyConversacion'
            deployment_slot = 'production'
            
            with client:
                result = client.analyze_conversation(
                    task={
                        "kind": "Conversation",
                        "analysisInput": {
                            "conversationItem": {
                                "participantId": "1",
                                "id": "1",
                                "modality": "text",
                                "language": "es",
                                "text": userText
                            },
                            "isLoggingEnabled": False
                        },
                        "parameters": {
                            "projectName": cls_project,
                            "deploymentName": deployment_slot,
                            "verbose": True
                        }
                    }
                )
            
            top_intent = result["result"]["prediction"]["topIntent"]
            entities = result["result"]["prediction"]["entities"]
            
            print("\n🔹 Intent Detectado: {}".format(top_intent))
            print("🔸 Confianza: {}".format(result["result"]["prediction"]["intents"][0]["confidenceScore"]))

            if entities:
                print("🔹 Entidades Detectadas:")
                for entity in entities:
                    print("  - {}: {} (Confianza: {})".format(entity["category"], entity["text"], entity["confidenceScore"]))

            # Ejecutar lógica según el intent detectado
            if top_intent == 'Clasificacion al Mundial': #cambiar el nombr
                print(get_qualification_info())
            elif top_intent == 'Ciudades Anfitrionas': # cambiar el nombre 
                city = get_entity_value(entities, 'Ciudades Anfitrionas')
                print(get_host_city_info(city))
            else:
                print("No tengo información sobre eso. Intenta preguntar sobre la clasificación o las ciudades sede del torneo.")
    
    except Exception as ex:
        print("Error:", ex)


def get_qualification_info():
    return "Los equipos se clasifican para la Rugby World Cup 2027 a través de torneos regionales y el ranking de World Rugby."


def get_host_city_info(city):
    city_info = {
        "Sídney": "Sídney albergará la final y varios partidos en el Accor Stadium.",
        "Melbourne": "Melbourne tendrá partidos en el AAMI Park.",
        "Brisbane": "Brisbane acogerá encuentros en el Suncorp Stadium.",
        "Perth": "Perth será sede de algunos partidos en el Optus Stadium.",
        "Adelaide": "Adelaide tendrá juegos en el Adelaide Oval.",
        "Canberra": "Canberra acogerá encuentros en el GIO Stadium.",
        "Newcastle": "Newcastle tendrá partidos en el McDonald Jones Stadium."
    }
    return city_info.get(city, "No tengo información sobre esa ciudad sede.")


def get_entity_value(entities, category):
    for entity in entities:
        if entity["category"] == category:
            return entity["text"]
    return None

if __name__ == "__main__":
    main()
