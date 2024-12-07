from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import os

# initialize environmental variables
load_dotenv()

# Azure Blob Configuration
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME = os.getenv("CONTAINER_NAME")

# Initialize the Blob Service Client
blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)

# Handler for HTTP requests
class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])  # Get the length of the request body
        post_data = self.rfile.read(content_length)  # Read the request body
        response = {"status": "error", "message": "Invalid request"}

        # Parse JSON payload
        try:
            data = json.loads(post_data.decode('utf-8'))
            file_name = data.get("fileName")
            text = data.get("text")
            overwrite = data.get("overwrite", False)

            if not file_name or text is None:
                response["message"] = "fileName and text fields are required"
            else:
                # Call the function to write to Azure Blob
                write_to_blob(file_name, text, overwrite)
                response = {"status": "success", "message": f"File '{file_name}' updated successfully"}

        except Exception as e:
            response["message"] = f"Error processing request: {str(e)}"

        # Send Response
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))

# Azure Blob write logic
def write_to_blob(file_name, text, overwrite):
    """
    Writes or appends text to an Azure Blob file.
    :param file_name: Name of the file in the Azure Blob
    :param text: Text content to write
    :param overwrite: If True, overwrites the blob. Otherwise, appends to it.
    """
    try:
        blob_client = container_client.get_blob_client(file_name)

        if overwrite:
            # Overwrite the blob with new content
            blob_client.upload_blob(text, overwrite=True)
        else:
            # Append to existing blob
            if blob_client.exists():
                existing_data = blob_client.download_blob().readall().decode('utf-8')
                text = existing_data + "\n" + text
            blob_client.upload_blob(text, overwrite=True)

    except Exception as e:
        raise RuntimeError(f"Error writing to blob: {str(e)}")

# Run the HTTP server
def run_server():
    server_address = ('', 8080)  # Serve on all network interfaces, port 8080
    httpd = HTTPServer(server_address, RequestHandler)
    print("Server running on port 8080...")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
