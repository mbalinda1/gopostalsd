import pytest
from server.controllers.print_product_controller import PrintProductController, PrintProductErrors, PrintProductSuccessMessages
from server.models.print_product import PrintProductCategory
from server import database as db
from unittest.mock import patch
from server.controllers import Result

@pytest.fixture
def create_categories():
    category1 = PrintProductCategory(name="Business Cards", enabled=True)
    category2 = PrintProductCategory(name="Flyers", enabled=False)
    category3 = PrintProductCategory(name="Posters", enabled=True)
    db.session.add_all([category1, category2, category3])
    db.session.commit()
    return category1, category2, category3

def test_get_all_product_categories(client, create_categories):
    result = PrintProductController.get_all_product_categories()
    assert isinstance(result, Result)
    assert result.status is True
    assert len(result.data) == 3
    assert result.error is None

def test_get_enabled_product_categories(client, create_categories):
    result = PrintProductController.get_enabled_product_categories()
    assert isinstance(result, Result)
    assert result.status is True
    assert len(result.data) == 2
    assert result.data[0]['name'] == "Business Cards"
    assert result.data[1]['name'] == "Posters"
    assert result.error is None

def test_update_print_product_category_status(client, create_categories):
    _, category2, _ = create_categories

    initial_category = db.session.get(PrintProductCategory, category2.id)
    assert initial_category.enabled is False

    # Valid catrgory id
    result = PrintProductController.update_print_product_category_status(category2.id, True)

    assert isinstance(result, Result)
    assert result.status is True
    assert result.data == PrintProductSuccessMessages.UPDATED_PRINT_PRODUCT_CATEGORY_STATUS_SUCCESSFULLY.value
    assert result.error is None

    updated_category = db.session.get(PrintProductCategory, category2.id)
    assert updated_category.enabled is True

    # Invalid category id
    result = PrintProductController.update_print_product_category_status(999, True)
    assert isinstance(result, Result)
    assert result.status == False
    assert result.data == None
    assert result.error == PrintProductErrors.PRINT_PRODUCT_CATEGORY_NOT_FOUND.value

def test_sync_print_product_categories(client):
    with patch('server.config.sinalite.get_product_categories', return_value=["Business Cards", "Flyers", "Posters"]) as mock_get_product_categories:
        PrintProductCategory.query.delete() # Clear existing categories
        db.session.commit()

        result = PrintProductController.sync_print_product_categories()

        assert isinstance(result, Result)
        assert result.status is True
        assert result.data == PrintProductSuccessMessages.PRINT_PRODUCT_CATEGORY_IN_SYNC.value
        assert result.error is None

        categories = PrintProductCategory.query.all()
        assert len(categories) == 3

        mock_get_product_categories.assert_called_once()

def test_get_all_products(client):
    with patch('server.config.sinalite.get_products', return_value=[{"id": 1, "name": "Business Card"}]) as mock_get_products:
        result = PrintProductController.get_all_products()

        assert isinstance(result, Result)
        assert result.status is True
        assert len(result.data) == 1
        assert result.data[0]["name"] == "Business Card"
        assert result.error is None
        mock_get_products.assert_called_once()

    with patch('server.config.sinalite.get_products', return_value=[]) as mock_get_products:
        result = PrintProductController.get_all_products()

        assert isinstance(result, Result)
        assert result.status is False
        assert result.error == PrintProductErrors.FAILED_TO_FETCH_PRINT_PRODUCTS.value
        assert result.data is None
        mock_get_products.assert_called_once()

def test_get_products_by_category(client, create_categories):

    # Mock Sinalite API product list
    with patch('server.config.sinalite.get_products', return_value=[
        {"id": 1, "name": "Premium Business Card", "category": "Business Cards"},
        {"id": 2, "name": "Standard Business Card", "category": "Business Cards"},
        {"id": 3, "name": "Marketing Flyer", "category": "Flyers"},
    ]) as mock_get_products:
        
        # Test valid and enabled category
        result = PrintProductController.get_products_by_category("Business Cards")

        assert isinstance(result, Result)
        assert result.status == True
        assert len(result.data) == 2
        assert result.data[0]["name"] == "Premium Business Card"
        assert result.data[1]["name"] == "Standard Business Card"
        assert result.error is None

        mock_get_products.assert_called_once()

        # Tests category that exists but is disabled
        result = PrintProductController.get_products_by_category("Flyers")
        assert isinstance(result, Result)
        assert result.status == False
        assert result.data is None
        assert result.error == PrintProductErrors.PRINT_PRODUCT_CATEGORY_NOT_FOUND.value

        # Tests category that does not exist in the database
        result = PrintProductController.get_products_by_category("Shirts")
        assert isinstance(result, Result)
        assert result.status is False
        assert result.data is None
        assert result.error == PrintProductErrors.PRINT_PRODUCT_CATEGORY_NOT_FOUND.value

    # Test category with no matching product
    with patch('server.config.sinalite.get_products', return_value=[
        {"id": 1, "name": "Premium Business Card", "category": "Business Cards"},
        {"id": 2, "name": "Standard Business Card", "category": "Business Cards"},
    ]) as mock_get_products:
        
        result = PrintProductController.get_products_by_category('Posters')

        assert isinstance(result, Result)
        assert result.status is True
        assert result.data == [] # Empty list when no products match
        assert result.error is None

        mock_get_products.assert_called_once()




    

    

    