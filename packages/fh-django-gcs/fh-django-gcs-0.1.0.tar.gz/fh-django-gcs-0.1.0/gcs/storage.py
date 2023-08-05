# -*- coding: utf-8 -*-
import base64
import datetime
import hashlib
import mimetypes
import os
import urllib
import time

from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from google.appengine.api import app_identity
import cloudstorage

from .settings import BUCKET, DEFAULT_ACL, DEFAULT_CACHE_CONTROL


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

    def __init__(self, location=None, base_url=None, acl=None,
                 content_addressable=True):
        self.location = '/{bucket}{location}'.format(bucket=BUCKET,
                                                     location=location)
        self.base_url = base_url
        self.acl = acl if acl else DEFAULT_ACL
        self.content_addressable = content_addressable

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
            if DEFAULT_CACHE_CONTROL:
                options.update({'cache-control': DEFAULT_CACHE_CONTROL})

            gcs_file = cloudstorage.open(filename, mode=mode,
                                         content_type=file_type,
                                         options=options)
        else:
            gcs_file = cloudstorage.open(filename, mode=mode)

        return gcs_file

    def _save(self, name, content):
        file_type, encoding = mimetypes.guess_type(name)
        cache_control = DEFAULT_CACHE_CONTROL

        # Split off filename if nested in folders
        name_head, name_tail = os.path.split(name)
        # Split off root from extension
        name_root, name_ext = os.path.splitext(name)

        digest = name_root
        if self.content_addressable:
            digest = self.digest(content)

        filename = os.path.normpath('{}/{}/{}{}'.format(self.location, name_head, digest, name_ext))

        # Files are stored with public-read permissions.
        # Check out the google acl options if you need to alter this.
        gss_file = cloudstorage.open(filename, mode='w', content_type=file_type,
                                     options={'x-goog-acl': self.acl,
                                              'cache-control': cache_control})
        try:
            content.open()
        except:
            pass

        gss_file.write(content.read())

        try:
            content.close()
        except:
            pass
        gss_file.close()

        return filename.split('/')[-1]

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
        name = os.path.normpath('{}{}'.format(self.location, name))

        url = '{}{}'.format(self.base_url, name.lstrip('/'))

        return url


    def serving_url(self, name):
        '''
        :param name:
        :return: a high-performance serving URL for images
        '''
        raise NotImplementedError('not yet implemented')

    def stat_file(self, name):
        filename = self.path(name)
        return cloudstorage.stat(filename)
