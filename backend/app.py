from server import create_server
import warnings
import os  # For environment variable management

# Suppress warning
warnings.filterwarnings("ignore", category=DeprecationWarning, module='flask_restx')

# Get the environment from .env or default to 'development'
environment = os.getenv("ENVIRONMENT", "development")
debug = os.getenv("DEBUG", False)

# Pass the environment explicitly to the factory function
app = create_server(config=environment)

if __name__ == "__main__":
    app.run(debug=debug)