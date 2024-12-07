import requests

url = "http://localhost:8080"
payload = {
    "fileName": "imeoverwrite.txt",
    "text": "checking if it works.",
    "overwrite": True
}
headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())

payload = {
    "fileName": "mustappend.txt",
    "text": "Append me asap.",
    "overwrite": False
}
response = requests.post(url, json=payload, headers=headers)
print(response.json())


