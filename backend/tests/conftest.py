import pytest
from server.config import database as db
from server import create_server
from sqlalchemy import inspect


# Define the app fixture required by pytest-flask
@pytest.fixture
def app():
    # Create a Flask application instance in testing mode
    test_app = create_server("testing")
    # Set up the application context
    with test_app.app_context():

        # Create tables
        db.create_all()
        
        # Print table names for debugging
        print("TABLES")
        for table in db.engine.table_names():
            print(table)
        yield test_app        # This makes the app available to tests
        db.drop_all()         # Drop tables after tests complete

# Define the client fixture that depends on the app fixture
@pytest.fixture
def client(app):
    return app.test_client()
