"""
<<<<<<< HEAD
ASGI config for pawsome project.
=======
ASGI config for dj_shop project.
>>>>>>> bb75f3e (login and home page)

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pawsome.settings")

application = get_asgi_application()
