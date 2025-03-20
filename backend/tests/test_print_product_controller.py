import pytest
from server.controllers.print_product_controller import PrintProductController, PrintProductErrors, PrintProductSuccessMessages
from server.models.print_product import PrintProductCategory
from server import database as db
from server.config import sinalite
from unittest.mock import patch
from server.controllers import Result

def setup_categories():
    category1 = PrintProductCategory(name="Business Cards", enabled=True)
    category2 = PrintProductCategory(name="Flyers", enabled=True)
    db.session.add_all([category1, category2])
    db.session.commit()
    return category1, category2

def test_get_all_product_categories(client):

    _,_ = setup_categories()
    result = PrintProductController.get_all_product_categories()

    print(result.data)
    print(isinstance(result, Result))

    assert isinstance(result, Result)
    assert result.status is True
    assert len(result.data) == 2
    assert result.error is None
    