from src.bot import application

# Expose the ASGI application for Gunicorn
asgi_app = application.asgi_app
