import streamlit as st
import json
from dotenv import load_dotenv
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations import ConversationAnalysisClient
from rugbyclu import get_tourism_info, get_qualification_info, get_host_city_info, get_news, get_team_info

# Cargar variables de entorno
load_dotenv()
ls_prediction_endpoint = st.secrets['LS_CONVERSATIONS_ENDPOINT']
ls_prediction_key = st.secrets['LS_CONVERSATIONS_KEY']

# Crear cliente de Azure Language Service
client = ConversationAnalysisClient(
    ls_prediction_endpoint, AzureKeyCredential(ls_prediction_key))

# Configuración de la app Streamlit
st.title("Chatbot Rugby World Cup 2027")
st.write("Haz una pregunta sobre la Rugby World Cup 2027")

# Entrada del usuario
userText = st.text_input("Escribe tu pregunta:")

if st.button("Enviar consulta") and userText:
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
                    "projectName": "RugbyConversacion",
                    "deploymentName": "rugbyCLU",
                    "verbose": True
                }
            }
        )
    
    # Obtener el intent y las entidades detectadas
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
    
    # Mostrar el JSON completo en una caja
    st.subheader("Respuesta en JSON")
    st.json(response_json)
    
    # Mostrar entidades detectadas
    st.subheader("Entidades Detectadas")
    if entities:
        for entity in entities:
            st.write(f"- **{entity['category']}**: {entity['text']} (Confianza: {entity['confidenceScore']:.2f})")
    else:
        st.write("No se detectaron entidades en la consulta.")
    
    # Mostrar información relevante según el intent detectado
    st.subheader("Información Adicional")
    if top_intent == 'Turismo en la Mundial':
        city = next((entity["text"] for entity in entities if entity["category"] == "ciudades"), None)
        if city:
            st.write(get_tourism_info(city))
        else:
            st.write("No se detectó una ciudad específica en la consulta.")
    elif top_intent == 'Clasificación al Mundial':
        st.write(get_qualification_info())
    elif top_intent == 'Ciudades Anfitrionas':
        st.write(get_host_city_info())
    elif top_intent == 'Equipos Participantes':
        st.write(get_team_info(entities))
    elif top_intent == 'Noticias':
        st.write(get_news())
