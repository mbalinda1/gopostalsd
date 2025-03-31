from server import create_server
import warnings
from flask import redirect
import os  

# Suppress warning
warnings.filterwarnings("ignore", category=DeprecationWarning, module='flask_restx')

# Get the environment from .env or default to 'development'
environment = os.getenv("ENVIRONMENT", "development")
debug = os.getenv("DEBUG", True)

# Pass the environment explicitly to the factory function
app = create_server(config=environment)

# Create the root route
@app.route("/api")
def api():
    
    # Redirect to the Swagger documentation
    return redirect("/")  

if __name__ == "__main__":
    app.run(debug=debug)