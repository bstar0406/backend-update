import mimetypes
import os.path
import uuid

from azure.common import AzureMissingResourceHttpError
from azure.storage.blob import BlobServiceClient
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from django.utils.timezone import localtime
from datetime import datetime


from pac.blobs.utils import AttachedFile

try:
    import azure  # noqa
except ImportError:
    raise ImproperlyConfigured(
        "Could not load Azure bindings. "
        "See https://github.com/WindowsAzure/azure-sdk-for-python")


def clean_name(name):
    return os.path.normpath(name).replace("\\", "/")


def setting(name, default=None):
    """
    Helper function to get a Django setting by name. If setting doesn't exists
    it will return a default.
    :param name: Name of setting
    :type name: str
    :param default: Value if setting is unfound
    :returns: Setting's value
    """
    return getattr(settings, name, default)


@deconstructible
class AzureStorage(Storage):
    # account_name = setting("AZURE_ACCOUNT_NAME")
    # account_key = setting("AZURE_ACCOUNT_KEY")

    azure_container_url = setting("AZURE_CONTAINER_URL")
    azure_ssl = setting("AZURE_SSL")

    def __init__(self, container=None, *args, **kwargs):
        super(AzureStorage, self).__init__(*args, **kwargs)
        self._connection = None

        if container is None:
            self.azure_container = setting("AZURE_CONTAINER")
        else:
            self.azure_container = container

    def get_available_name(self, name, *args, **kwargs):

        return {"original_name": name, "uuid": str(uuid.uuid4())}

    @property
    def connection(self):

        if self._connection is None:
            connect_str = setting("AZURE_STORAGE_CONNECTION_STRING")

            # Create the BlobServiceClient object which will be used to create a container client
            blob_service_client = BlobServiceClient.from_connection_string(connect_str)

            # Create a unique name for the container
            container_name = "pac-files"

            # Create a blob client using the local file name as the name for the blob
            self._connection = blob_service_client

        return self._connection

    @property
    def azure_protocol(self):
        """
        :return: http | https | None
        :rtype: str | None
        """
        if self.azure_ssl:
            return 'https'
        return 'http' if self.azure_ssl is not None else None

    def __get_blob_properties(self, name):
        """
        :param name: Filename
        :rtype: azure.storage.blob.models.Blob | None
        """
        try:
            return self.connection.get_blob_properties(
                self.azure_container,
                name
            )
        except AzureMissingResourceHttpError:
            return None

    def _open(self, container, name, mode="rb"):
        """
        :param str name: Filename
        :param str mode:
        :rtype: ContentFile
        """
        print(f'Retrieving blob: container={self.azure_container}, blob={name}')
        blob_client = self.connection.get_blob_client(container=container, blob=name)
        contents = blob_client.download_blob().readall()
        return ContentFile(contents)

    def exists(self, name):
        """
        :param name: File name
        :rtype: bool
        """
        return False  # self.__get_blob_properties(name) is not None

    def delete(self, name):
        """
        :param name: File name
        :return: None
        """
        try:
            self.connection.delete_blob(self.azure_container, name)
        except AzureMissingResourceHttpError:
            pass

    def size(self, name):
        """
        :param name:
        :rtype: int
        """
        blob = self.connection.get_blob_properties(self.azure_container, name)
        return blob.properties.content_length

    def _save(self, name, content):
        """
        :param name:
        :param File content:
        :return:
        """
        original_name = name.get("original_name")
        blob_file_name = datetime.now().strftime("%Y%m%d-%H:%M:%S.%f_") + original_name
        # blob_name = "{}.{}".format(name.get("uuid"), original_name.partition(".")[-1])

        if hasattr(content.file, 'content_type'):
            content_type = content.file.content_type
        else:
            content_type = mimetypes.guess_type(original_name)

        if hasattr(content, 'chunks'):
            content_data = b''.join(chunk for chunk in content.chunks())
        else:
            content_data = content.read()

        print(f'Saving blob: container={self.azure_container}, blob={blob_file_name}')
        blob_client = self.connection.get_blob_client(container=self.azure_container, blob=blob_file_name)
        obj = blob_client.upload_blob(content_data)
        # create_blob_from_bytes(self.azure_container, name, content_data,
        #
        #                                        content_settings=ContentSettings(content_type=content_type))
        af = AttachedFile(original_name, self.azure_container, blob_file_name)
        return af

    def url(self, name):
        """

        :param str name: Filename
        :return: path
        """
        return self.connection.make_blob_url(
            container_name=self.azure_container,
            blob_name=name,
            protocol=self.azure_protocol,
        )

    def modified_time(self, name):
        """
        :param name:
        :rtype: datetime.datetime
        """
        blob = self.__get_blob_properties(name)

        return localtime(blob.properties.last_modified).replace(tzinfo=None)
