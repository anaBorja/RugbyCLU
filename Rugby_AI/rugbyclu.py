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
            deployment_slot = 'rugbyCLU'
            
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
            confidence = result["result"]["prediction"]["intents"][0]["confidenceScore"]
            intents = result["result"]["prediction"]["intents"]
            entities = result["result"]["prediction"]["entities"]
            
            # Construir JSON de salida
            response_json = {
                "query": userText,
                "prediction": {
                    "topIntent": top_intent,
                    "projectKind": "Conversation",
                    "intents": [
                        {
                            "category": intent["category"],
                            "confidenceScore": intent["confidenceScore"]
                        } for intent in intents
                    ],
                    "entities": [
                        {
                            "category": entity["category"],
                            "text": entity["text"],
                            "confidenceScore": entity["confidenceScore"]
                        } for entity in entities
                    ]
                }
            }

            # Imprimir JSON formateado
            print("\n📜 **Respuesta en JSON:**\n")
            print(json.dumps(response_json, indent=4, ensure_ascii=False))

            if entities:
                print("\U0001F4A1 Entidades Detectadas:")
                for entity in entities:
                    print("  - {}: {} (Confianza: {})".format(entity["category"], entity["text"], entity["confidenceScore"]))

            # Ejecutar lógica según el intent detectado
            if top_intent == 'Clasificacion al Mundial':
                print(get_qualification_info())
            elif top_intent == 'Ciudades Anfitrionas':
                city = get_entity_value(entities, 'Ciudad')
                city = normalize_city_name(city)
                print(get_host_city_info(city))
            elif top_intent == 'Turismo en la Mundial':
                city = get_entity_value(entities, 'Ciudad')
                city = normalize_city_name(city)
                print(get_tourism_info(city))
            elif top_intent == 'Equipos Paticipantes':
                print(get_news())
            else:
                print("No tengo información sobre eso. Intenta preguntar sobre la clasificación, ciudades, turismo o noticias del torneo.")
    
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


def get_tourism_info(city):
    tourism_info = {
        "Sídney": "Visita la Ópera de Sídney y la playa Bondi.",
        "Melbourne": "Explora la Great Ocean Road y el barrio Fitzroy.",
        "Brisbane": "Descubre South Bank y el santuario de koalas Lone Pine.",
        "Perth": "Disfruta de la Isla Rottnest y el Kings Park.",
        "Adelaide": "Conoce el valle de Barossa y el Mercado Central de Adelaide.",
        "Canberra": "Explora el Parlamento y el Lago Burley Griffin.",
        "Newcastle": "Relájate en las playas y visita el fuerte Scratchley."
    }
    return tourism_info.get(city, "No tengo información turística sobre esta ciudad.")


def get_team_info(entities):
    if not entities:
        return "No tengo información específica sobre equipos. Pregunta por un equipo en particular."
    
    team = get_entity_value(entities, 'equipos de rugby')
    return f"Información sobre {team}: Próximos partidos y desempeño en el torneo  https://www.rugbyworldcup.com/2027/."

def get_news():
    return "https://www.rugbyworldcup.com/2027/es/news"


def get_entity_value(entities, category):
    for entity in entities:
        if entity["category"] == category:
            return entity["text"]
    return None

def normalize_city_name(city):
    """
    Normaliza nombres de ciudades corrigiendo errores comunes en la entrada del usuario.
    """
    if not  city:
        return None
    
    city_variants = {
        "sydney": "Sídney",
        "melbourne": "Melbourne",
        "brisbane": "Brisbane",
        "perth": "Perth",
        "adelaide": "Adelaide",
        "canberra": "Canberra",
        "newcastle": "Newcastle",
        "pertth": "Perth"  # Corrige errores tipográficos comunes
    }
    return city_variants.get(city.lower(), city)

if __name__ == "__main__":
    main()
