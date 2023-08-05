from django.conf import settings

STORAGE = getattr(settings, 'ASSETMANAGER_STORAGE',
                  'django.core.files.storage.FileSystemStorage')
PAGE_SIZE = getattr(settings, 'ASSETMANAGER_PAGE_SIZE', 10)
IMAGE_CONTENT_TYPES = getattr(settings, 'ASSETMANAGER_IMAGE_CONTENT_TYPES',
                              ('image/jpeg', 'image/png', 'image/gif',
                               'image/svg+xml'))
MEDIA_ROOT = getattr(settings, 'ASSETMANAGER_MEDIA_ROOT', '/assetmanager/')
MEDIA_URL = getattr(settings, 'ASSETMANAGER_MEDIA_URL', '')
