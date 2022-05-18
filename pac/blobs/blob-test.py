import os, uuid
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, __version__

try:
    connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

    print("Azure Blob storage v" + __version__ + " - Python quickstart sample")
    # Create a file in local data directory to upload and download
    local_path = "./data"
    local_file_name = "quickstart" + str(uuid.uuid4()) + ".txt"
    upload_file_path = os.path.join(local_path, local_file_name)
    # Write text to the file
    file = open(upload_file_path, 'w')
    file.write("Hello, World!")
    file.close()

    # Create the BlobServiceClient object which will be used to create a container client
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    # Create a unique name for the container
    container_name = "pac-files"

    # Create a blob client using the local file name as the name for the blob
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=local_file_name)

    # Upload the created file
    with open(upload_file_path, "rb") as data:
        blob_client.upload_blob(data)
        # blob_client.

except Exception as ex:
    print('Exception:')
    print(ex)
