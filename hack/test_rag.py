import requests
import json

# Make a request to the RAG API
response = requests.post(
    "http://localhost:8001/v1/chat/completions",
    json={
        "model": "ollama/mistral",
        "messages": [
            {"role": "user", "content": "What is the RAG pipeline in Obelisk?"}
        ],
        "temperature": 0.7
    }
)

# Print the response
print(f"Status Code: {response.status_code}")
print(json.dumps(response.json(), indent=2))