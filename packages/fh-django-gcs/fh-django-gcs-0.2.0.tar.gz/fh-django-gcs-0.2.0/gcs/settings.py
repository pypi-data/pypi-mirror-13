from django.conf import settings

BUCKET = getattr(
        settings, 'GOOGLE_CLOUD_STORAGE_BUCKET', None)

CONTENT_ADDRESSABLE = getattr(
        settings, 'GOOGLE_CLOUD_STORAGE_CONTENT_ADDRESSABLE', True)

DEFAULT_ACL = getattr(
        settings, 'GOOGLE_CLOUD_STORAGE_DEFAULT_ACL', 'project-private')
