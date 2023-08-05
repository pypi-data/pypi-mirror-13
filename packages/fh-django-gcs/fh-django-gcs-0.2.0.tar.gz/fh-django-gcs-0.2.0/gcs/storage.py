# -*- coding: utf-8 -*-
import hashlib
import mimetypes
import os

from django.conf import settings
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from google.appengine.api import app_identity
import cloudstorage

from .settings import BUCKET, DEFAULT_ACL


def hash_chunks(iterator, digestmod=hashlib.sha1):

    """
    Hash the contents of a string-yielding iterator.

        >>> import hashlib
        >>> digest = hashlib.sha1('abc').hexdigest()
        >>> strings = iter(['a', 'b', 'c'])
        >>> hash_chunks(strings, digestmod=hashlib.sha1) == digest
        True

    """

    digest = digestmod()
    for chunk in iterator:
        digest.update(chunk)
    return digest.hexdigest()


@deconstructible()
class GoogleCloudStorage(Storage):
    API_ACCESS_ENDPOINT = 'https://storage.googleapis.com'
    GOOGLE_ACCESS_ID = app_identity.get_service_account_name()

    def __init__(self, config):
        # config = settings.get(config)
        config = getattr(settings, config)

        bucket = config.get('bucket') or BUCKET
        location = config.get('location')
        self.location = '/{bucket}{location}'.format(bucket=bucket,
                                                     location=location)
        self.base_url = config.get('base_url')

        acl = config.get('acl')
        self.acl = acl if acl else DEFAULT_ACL

        self.content_addressable = config.get('content_addressable', True)
        self.cache_control = config.get('cache_control', None)

    def path(self, name):
        return os.path.normpath('{}/{}'.format(self.location, name))

    @staticmethod
    def get_available_name(name):
        """Return the name as-is; in CAS, given names are ignored anyway."""
        return name

    def digest(self, content):
        digest = hash_chunks(content.chunks())
        content.seek(0)
        return digest

    def _open(self, name, mode='r'):
        if '/' not in name:
            filename = self.path(name)
        else:
            filename = name

        # rb is not supported
        if mode == 'rb':
            mode = 'r'

        if mode == 'w':
            file_type, encoding = mimetypes.guess_type(name)

            options = {
                'x-goog-acl': self.acl
            }
            if self.cache_control:
                options.update({'cache-control': self.cache_control})

            gcs_file = cloudstorage.open(filename, mode=mode,
                                         content_type=file_type,
                                         options=options)
        else:
            gcs_file = cloudstorage.open(filename, mode=mode)

        return gcs_file

    def _save(self, name, content):
        file_type, encoding = mimetypes.guess_type(name)

        # Split off root from extension
        name_root, name_ext = os.path.splitext(name)

        if self.content_addressable:
            name_root = self.digest(content)

        filename = os.path.normpath('{}/{}{}'.format(self.location, name_root,
                                                     name_ext))

        # Files are stored with public-read permissions.
        # Check out the google acl options if you need to alter this.
        options = {'x-goog-acl': self.acl}
        if self.cache_control:
            options.update({'cache-control': self.cache_control})
        gcs_file = cloudstorage.open(filename, mode='w', content_type=file_type,
                                     options=options)

        try:
            content.open()
        except:
            pass

        gcs_file.write(content.read())

        try:
            content.close()
        except:
            pass
        gcs_file.close()

        return filename

    def delete(self, name):
        filename = self.path(name)
        try:
            cloudstorage.delete(filename)
        except cloudstorage.NotFoundError:
            pass

    def exists(self, name):
        try:
            self.stat_file(name)
            return True
        except cloudstorage.NotFoundError:
            return False

    def listdir(self, path=None):
        raise NotImplementedError('not yet implemented')

    def size(self, name):
        stats = self.stat_file(name)
        return stats.st_size

    def accessed_time(self, name):
        raise NotImplementedError

    def created_time(self, name):
        stats = self.stat_file(name)
        return stats.st_ctime

    def modified_time(self, name):
        return self.created_time(name)

    def url(self, name):
        return '{}{}'.format(self.base_url, name.lstrip('/'))

    def serving_url(self, name):
        '''
        :param name:
        :return: a high-performance serving URL for images
        '''
        raise NotImplementedError('not yet implemented')

    def stat_file(self, name):
        filename = self.path(name)
        return cloudstorage.stat(filename)
