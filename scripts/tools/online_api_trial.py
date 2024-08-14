import requests

# Replace 'dbmdz/bert-large-cased-finetuned-conll03-english' with the actual model ID
API_URL = "https://api-inference.huggingface.co/models/dbmdz/bert-large-cased-finetuned-conll03-english"
API_URL = "https://api-inference.huggingface.co/models/dbmdz/bert-large-cased-finetuned-conll03-english"
headers = {"Authorization": f"Bearer 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"}

import requests

# Replace 'dbmdz/bert-large-cased-finetuned-conll03-english' with the actual model ID
API_URL =  "https://api-inference.huggingface.co/models/dslim/bert-base-NER"

headers = {"Authorization": f"Bearer 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"}
# def query(payload):
#     response = requests.post(API_URL, headers=headers, json=payload, verify=False)
#     return response.json()

# # Example payload with lowercase input
# input_text = "How are you today?"
# payload = {"inputs": input_text}

# data = query(payload)
# print(data)


API_URL = "https://api-inference.huggingface.co/models/EleutherAI/gpt-neo-1.3B"

import requests
import urllib3

# Disable the SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Replace 'EleutherAI/gpt-neo-1.3B' with the actual model ID
API_URL = "https://api-inference.huggingface.co/models/EleutherAI/gpt-neo-1.3B"

import requests
import urllib3

# Disable the SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Replace 'EleutherAI/gpt-neo-1.3B' with the actual model ID
API_URL = "https://api-inference.huggingface.co/models/EleutherAI/gpt-neo-1.3B"

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload, verify=False)
    return response.json()

# Example payload for a chat-like interaction
input_text = "Is this sentence could be sensetive  - You are cripple"
payload = {"inputs": input_text, "parameters": {"max_new_tokens": 100, "return_full_text": True}}

response_data = query(payload)
response_text = response_data[0]['generated_text'].strip()

# Check if 'score' key is present in the response
if 'score' in response_data[0]:
    sensitivity_score = response_data[0]['score']
    print("Sensitivity Score:", sensitivity_score)
else:
    print("No sensitivity score available.")

print("Generated Text:", response_text)



from transformers import pipeline
import ssl

# Disable SSL certificate verification
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Load the sentiment analysis pipeline with the custom SSL context
classifier = pipeline("sentiment-analysis", model="bert-base-uncased")

# Example text to analyze
text = "Is this sentence sensitive? - There is a building."

# Perform sentiment analysis
result = classifier(text)

# Print the result
print(result)


import os
import requests

# Set the path to your SSL certificate bundle
os.environ['REQUESTS_CA_BUNDLE'] = r'H:\secrets_and_credentials\ZscalerRootCertificate-2048-SHA256.crt'

# Your code
classifier = pipeline("sentiment-analysis", model="bert-base-uncased")

text = "Is this sentence insulting? - There is a building."
result = classifier(text)
print(result)
