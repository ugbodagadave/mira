from src.bot import create_app

# Create the application instance using the factory
application = create_app()

# Expose the ASGI application for Gunicorn
asgi_app = application.asgi_app
