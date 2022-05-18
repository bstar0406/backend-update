import json
from datetime import datetime

from azure.storage.blob import BlobServiceClient
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from django.core.files.uploadhandler import FileUploadHandler, StopFutureHandlers
import os
import uuid
from io import BytesIO


class BlobFileUploadHandler(FileUploadHandler):

    def handle_raw_input(self, input_data, META, content_length, boundary, encoding=None):
        """
        Use the content_length to signal whether or not this handler should be
        used.
        """
        # Check the content-length header to see if we should
        # If the post is too large, we cannot use the Memory handler.
        self.activated = content_length <= settings.FILE_UPLOAD_MAX_MEMORY_SIZE

    def new_file(self, *args, **kwargs):
        """
         Create the file object to append to as data is coming in.
         """
        super().new_file(*args, **kwargs)
        self.file = TemporaryUploadedFile(self.file_name, self.content_type, 0, self.charset, self.content_type_extra)

    def file_complete(self, file_size):
        """Return a file object if this handler is activated."""
        self.file.seek(0)
        self.file.size = file_size
        file_name = ""
        try:
            connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

            # Create the BlobServiceClient object which will be used to create a container client
            blob_service_client = BlobServiceClient.from_connection_string(connect_str)

            # Create a unique name for the container
            container_name = "pac-files"
            file_name = str(uuid.uuid4()) + ".txt"
            # Create a blob client using the local file name as the name for the blob
            blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name)

            # Upload the created file
            file = self.file
            blob_client.upload_blob(file)
            print(file_name)
        except Exception as ex:
            print('Exception:')
            print(ex)

        self.file.seek(0)

        return InMemoryUploadedFile(
            file=self.file,
            field_name=self.file,
            name=file_name,
            content_type=self.content_type,
            size=file_size,
            charset=self.charset,
            content_type_extra=self.content_type_extra
        )

    def receive_data_chunk(self, raw_data, start):
        self.file.write(raw_data)


class AttachedFile():

    def __init__(self, name, container, file_name):
        self.name = name
        self.container = container
        self.blob = file_name
        self.status = "ACTIVE"

    def __repr__(self):
        return json.dumps(self.__dict__)
