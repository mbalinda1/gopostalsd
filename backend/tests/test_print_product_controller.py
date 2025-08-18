import pytest
import io
from unittest.mock import MagicMock, patch
from werkzeug.datastructures import FileStorage
from server.controllers.print_product_controller import (
    PrintProductController,
    PrintProductErrors,
    PrintProductSuccessMessages
)
from server.models.print_product import PrintProductCategory, PrintProductType
from server import database as db
from unittest.mock import patch
from server.controllers import Result



CATEGORY_BUSINESS_CARDS = "Business Cards"
CATEGORY_FLYERS = "Flyers"
CATEGORY_POSTERS = "Posters"

@pytest.fixture
def create_categories():
    category1 = PrintProductCategory(name=CATEGORY_BUSINESS_CARDS, enabled=True)
    category2 = PrintProductCategory(name=CATEGORY_FLYERS, enabled=False)
    category3 = PrintProductCategory(name=CATEGORY_POSTERS, enabled=True)

    db.session.add_all([category1, category2, category3])
    db.session.commit()

    # Re-attach for access to IDs
    return (
        db.session.get(PrintProductCategory, category1.id),
        db.session.get(PrintProductCategory, category2.id),
        db.session.get(PrintProductCategory, category3.id),
    )

@pytest.fixture
def clean_categories():
    PrintProductCategory.query.delete()
    db.session.commit()
    yield
    PrintProductCategory.query.delete()
    db.session.commit()

@pytest.fixture
def clean_product_types():
    PrintProductType.query.delete()
    db.session.commit()
    yield
    PrintProductType.query.delete()
    db.session.commit()

@pytest.fixture
def create_product_types(create_categories):
    category1, _, _ = create_categories
    
    # Create some product types for testing
    type1 = PrintProductType(
        name="Premium Business Cards",
        category_id=category1.id,
        description="High-quality business cards with premium finish"
    )
    type2 = PrintProductType(
        name="Standard Business Cards",
        category_id=category1.id,
        description="Standard business cards with basic finish"
    )
    
    db.session.add_all([type1, type2])
    db.session.commit()
    
    # Re-attach for access to IDs
    return (
        db.session.get(PrintProductType, type1.id),
        db.session.get(PrintProductType, type2.id),
        category1
    )

# ========== EMPTY TABLE COVERAGE ==========

def test_get_all_product_categories_empty_table(client, clean_categories):
    result = PrintProductController.get_all_product_categories()
    assert isinstance(result, Result)
    assert result.status is True
    assert result.data == []
    assert result.error is None

def test_get_enabled_product_categories_empty_table(client, clean_categories):
    result = PrintProductController.get_enabled_product_categories()
    assert isinstance(result, Result)
    assert result.status is True
    assert result.data == []
    assert result.error is None

def test_update_print_product_category_status_empty_table(client, clean_categories):
    result = PrintProductController.update_print_product_category_status(1, True)
    assert isinstance(result, Result)
    assert result.status is True  # Still true, just returns empty list
    assert result.data == []
    assert result.error is None

def test_get_all_products_by_category_empty_table(client, clean_categories):
    result = PrintProductController.get_all_products_by_category(1)
    assert isinstance(result, Result)
    assert result.status is True
    assert result.data == []
    assert result.error is None

def test_get_enabled_products_by_category_empty_table(client, clean_categories):
    result = PrintProductController.get_enabled_products_by_category(1)
    assert isinstance(result, Result)
    assert result.status is True
    assert result.data == []
    assert result.error is None

# ========== STANDARD TESTS ==========

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
    assert result.error is None

def test_update_print_product_category_status(client, create_categories):
    _, category2, _ = create_categories
    assert category2.enabled is False

    result = PrintProductController.update_print_product_category_status(category2.id, True)
    assert result.status is True
    assert result.data == {
        "message": PrintProductSuccessMessages.UPDATED_PRINT_PRODUCT_CATEGORY_STATUS_SUCCESSFULLY.value
    }

    # Confirm DB updated
    updated = db.session.get(PrintProductCategory, category2.id)
    assert updated.enabled is True

    result = PrintProductController.update_print_product_category_status(9999, False)
    assert result.status is False
    assert result.error == PrintProductErrors.PRINT_PRODUCT_CATEGORY_NOT_FOUND.value

def test_get_all_products_by_category_success(client, create_categories):
    """Test get_all_products_by_category with valid category ID"""
    category1, _, _ = create_categories
    
    with patch('server.config.sinalite.get_products', return_value=[
        {"id": 1, "name": "Premium BC", "category": CATEGORY_BUSINESS_CARDS},
        {"id": 2, "name": "Standard BC", "category": CATEGORY_BUSINESS_CARDS},
        {"id": 3, "name": "Flyer", "category": CATEGORY_FLYERS}
    ]):
        result = PrintProductController.get_all_products_by_category(category1.id)
        assert result.status is True
        assert len(result.data) == 2
        assert all(product["category"] == CATEGORY_BUSINESS_CARDS for product in result.data)

def test_get_all_products_by_category_not_found(client, create_categories):
    """Test get_all_products_by_category with non-existent category ID"""
    with patch('server.config.sinalite.get_products', return_value=[{"id": 1, "name": "Business Card"}]):
        result = PrintProductController.get_all_products_by_category(9999)
        assert result.status is False
        assert result.error == PrintProductErrors.PRINT_PRODUCT_CATEGORY_NOT_FOUND.value

def test_get_enabled_products_by_category_success(client, create_categories):
    """Test get_enabled_products_by_category with valid enabled category ID"""
    category1, _, category3 = create_categories
    
    with patch('server.config.sinalite.get_products', return_value=[
        {"id": 1, "name": "Premium BC", "category": CATEGORY_BUSINESS_CARDS},
        {"id": 2, "name": "Standard BC", "category": CATEGORY_BUSINESS_CARDS},
        {"id": 3, "name": "Poster", "category": CATEGORY_POSTERS}
    ]):
        result = PrintProductController.get_enabled_products_by_category(category1.id)
        assert result.status is True
        assert len(result.data) == 2
        assert all(product["category"] == CATEGORY_BUSINESS_CARDS for product in result.data)

def test_get_enabled_products_by_category_disabled_category(client, create_categories):
    """Test get_enabled_products_by_category with disabled category ID"""
    _, category2, _ = create_categories  # category2 is disabled
    
    with patch('server.config.sinalite.get_products', return_value=[
        {"id": 1, "name": "Flyer", "category": CATEGORY_FLYERS}
    ]):
        result = PrintProductController.get_enabled_products_by_category(category2.id)
        assert result.status is False
        assert result.error == PrintProductErrors.PRINT_PRODUCT_CATEGORY_NOT_FOUND.value

def test_get_enabled_products_by_category_not_found(client, create_categories):
    """Test get_enabled_products_by_category with non-existent category ID"""
    with patch('server.config.sinalite.get_products', return_value=[{"id": 1, "name": "Business Card"}]):
        result = PrintProductController.get_enabled_products_by_category(9999)
        assert result.status is False
        assert result.error == PrintProductErrors.PRINT_PRODUCT_CATEGORY_NOT_FOUND.value

def test_get_all_products_by_category_no_matching_products(client, create_categories):
    """Test get_all_products_by_category when no products match the category"""
    category1, _, _ = create_categories
    
    with patch('server.config.sinalite.get_products', return_value=[
        {"id": 1, "name": "Flyer", "category": CATEGORY_FLYERS},
        {"id": 2, "name": "Poster", "category": CATEGORY_POSTERS}
    ]):
        result = PrintProductController.get_all_products_by_category(category1.id)
        assert result.status is True
        assert result.data == []

def test_get_enabled_products_by_category_no_matching_products(client, create_categories):
    """Test get_enabled_products_by_category when no products match the category"""
    category1, _, _ = create_categories
    
    with patch('server.config.sinalite.get_products', return_value=[
        {"id": 1, "name": "Flyer", "category": CATEGORY_FLYERS},
        {"id": 2, "name": "Poster", "category": CATEGORY_POSTERS}
    ]):
        result = PrintProductController.get_enabled_products_by_category(category1.id)
        assert result.status is True
        assert result.data == []

# ========== SYNC ==========

def test_sync_print_product_categories(client, clean_categories):
    with patch('server.config.sinalite.get_product_categories', return_value=[CATEGORY_BUSINESS_CARDS, CATEGORY_FLYERS]):
        result = PrintProductController.sync_print_product_categories()
        assert result.status is True
        assert result.data == {"message": PrintProductSuccessMessages.PRINT_PRODUCT_CATEGORY_IN_SYNC.value}
        assert PrintProductCategory.query.count() == 2

# ========== SINALITE PRODUCTS ==========

def test_get_all_products(client):
    with patch('server.config.sinalite.get_products', return_value=[{"id": 1, "name": "Business Card"}]):
        result = PrintProductController.get_all_products()
        assert result.status is True
        assert result.data[0]["name"] == "Business Card"

    with patch('server.config.sinalite.get_products', return_value=[]):
        result = PrintProductController.get_all_products()
        assert result.status is False
        assert result.error == PrintProductErrors.FAILED_TO_FETCH_PRINT_PRODUCTS.value

# ========== update_print_product_category ==========

def test_update_print_product_category_description(client, create_categories):
    category, _, _ = create_categories
    result = PrintProductController.update_print_product_category(category.id, description="New description")

    assert result.status is True
    assert result.data["message"] == PrintProductSuccessMessages.PRODUCT_CATEGORY_UPDATED_SUCCESSFULLY.value
    updated = db.session.get(PrintProductCategory, category.id)
    assert updated.description == "New description"

def test_update_print_product_category_description_too_long(client, create_categories):
    category, _, _ = create_categories
    long_desc = "a" * 1001
    result = PrintProductController.update_print_product_category(category.id, description=long_desc)

    assert result.status is False
    assert result.error == PrintProductErrors.PRINT_PRODUCT_DESCRIPTION_TOO_LONG.value

def test_update_print_product_category_not_found(client):
    result = PrintProductController.update_print_product_category(category_id=9999, description="Doesn't matter")

    assert result.status is False
    assert result.error == PrintProductErrors.PRINT_PRODUCT_CATEGORY_NOT_FOUND.value

def test_update_print_product_category_invalid_image_type(client, create_categories):
    category, _, _ = create_categories
    result = PrintProductController.update_print_product_category(category.id, image=12345)

    assert result.status is False
    assert result.error == PrintProductErrors.INVALID_IMAGE_FILE.value

def test_update_print_product_category_empty_image_file(client, create_categories):
    category, _, _ = create_categories
    # Create FileStorage with empty filename but some content to ensure it's a valid FileStorage object
    empty_image = FileStorage(stream=io.BytesIO(b"some content"), filename="", content_type="image/png")
    result = PrintProductController.update_print_product_category(category.id, image=empty_image)

    assert result.status is False
    assert result.error == PrintProductErrors.EMPTY_IMAGE_FILENAME.value

def test_update_print_product_category_valid_image(client, create_categories):
    category, _, _ = create_categories
    image_data = FileStorage(stream=io.BytesIO(b"fake image data"), filename="test.png", content_type="image/png")
    
    with patch("server.controllers.print_product_controller.current_app") as mock_current_app:
        fake_storage = MagicMock()
        fake_storage.upload_file.return_value = "http://example.com/image.png"
        mock_current_app.extensions = {"filestorage": fake_storage}
        
        result = PrintProductController.update_print_product_category(category.id, image=image_data)
        
        assert result.status is True
        assert result.data["message"] == PrintProductSuccessMessages.PRODUCT_CATEGORY_UPDATED_SUCCESSFULLY.value
        updated = db.session.get(PrintProductCategory, category.id)
        assert updated.image == "http://example.com/image.png"

def test_update_print_product_category_commit_fails(client, create_categories):
    category, _, _ = create_categories
    
    with patch("server.controllers.print_product_controller.db.session.commit", side_effect=Exception("Database fail")):
        result = PrintProductController.update_print_product_category(category.id, description="Should fail")
        
        assert result.status is False
        assert PrintProductErrors.FAILED_TO_UPDATE_PRODUCT_CATEGORY.value in result.error

# ========== PRINT PRODUCT TYPE TESTS ==========

# ========== GET ALL PRINT PRODUCT TYPES TESTS ==========

def test_get_all_print_product_types_empty_table(client, clean_product_types):
    """Test get_all_print_product_types when table is empty"""
    result = PrintProductController.get_all_print_product_types()
    
    assert isinstance(result, Result)
    assert result.status is True
    assert result.data == []
    assert result.error is None

def test_get_all_print_product_types_success(client, create_product_types):
    """Test successful retrieval of all print product types"""
    product_type1, product_type2, _ = create_product_types
    
    result = PrintProductController.get_all_print_product_types()
    
    assert isinstance(result, Result)
    assert result.status is True
    assert len(result.data) == 2
    assert result.error is None
    
    # Verify data structure and sorting (should be sorted by name)
    assert result.data[0]['name'] == "Premium Business Cards"  # Alphabetically first
    assert result.data[1]['name'] == "Standard Business Cards"  # Alphabetically second
    
    # Verify all required fields are present
    for product_type in result.data:
        assert 'id' in product_type
        assert 'name' in product_type
        assert 'category_id' in product_type
        assert 'description' in product_type
        assert 'image' in product_type
        assert 'created_at' in product_type
        assert 'updated_at' in product_type

def test_get_all_print_product_types_with_mixed_data(client, create_categories):
    """Test retrieval with mixed product types including some with images"""
    category1, category2, _ = create_categories
    
    # Create product types with different attributes
    type1 = PrintProductType(
        name="Type A",
        category_id=category1.id,
        description="Description A",
        image="http://example.com/image1.jpg"
    )
    type2 = PrintProductType(
        name="Type B", 
        category_id=category2.id,
        description="Description B",
        image=None
    )
    type3 = PrintProductType(
        name="Type C",
        category_id=category1.id,
        description="Description C",
        image="http://example.com/image3.jpg"
    )
    
    db.session.add_all([type1, type2, type3])
    db.session.commit()
    
    result = PrintProductController.get_all_print_product_types()
    
    assert result.status is True
    assert len(result.data) == 3
    
    # Should be sorted alphabetically by name
    names = [pt['name'] for pt in result.data]
    assert names == ["Type A", "Type B", "Type C"]
    
    # Verify image handling
    type_a = next(pt for pt in result.data if pt['name'] == "Type A")
    type_b = next(pt for pt in result.data if pt['name'] == "Type B")
    
    assert type_a['image'] == "http://example.com/image1.jpg"
    assert type_b['image'] is None

def test_get_all_print_product_types_database_error(client):
    """Test get_all_print_product_types when database query fails"""
    with patch("server.controllers.print_product_controller.PrintProductType.query") as mock_query:
        # Mock first() to fail immediately (this will trigger the exception handling)
        mock_query.first.side_effect = Exception("Database connection failed")
        
        result = PrintProductController.get_all_print_product_types()
        
        assert result.status is False
        assert PrintProductErrors.FAILED_TO_FETCH_PRINT_PRODUCT_TYPES.value in result.error
        assert "Database connection failed" in result.error

def test_get_all_print_product_types_query_failure(client):
    """Test get_all_print_product_types when query.all() fails"""
    with patch("server.controllers.print_product_controller.PrintProductType.query") as mock_query:
        # Mock first() to return a dummy object (not None) so the method continues
        mock_first = MagicMock()
        mock_first.id = 1  # Dummy object to represent "table not empty"
        mock_query.first.return_value = mock_first
        
        # Mock the order_by().all() chain to fail
        mock_order_by = MagicMock()
        mock_order_by.all.side_effect = Exception("Query execution failed")
        mock_query.order_by.return_value = mock_order_by
        
        result = PrintProductController.get_all_print_product_types()
        assert result.status is False
        assert PrintProductErrors.FAILED_TO_FETCH_PRINT_PRODUCT_TYPES.value in result.error
        assert "Query execution failed" in result.error


# ========== CREATE PRINT PRODUCT TYPE TESTS ==========

def test_create_print_product_type_success(client, create_categories):
    """Test successful creation of a print product type"""
    category, _, _ = create_categories
    
    data = {
        'name': 'New Business Card Type',
        'category_id': category.id,
        'description': 'A new type of business card'
    }
    
    result = PrintProductController.create_print_product_type(data)
    
    assert result.status is True
    assert result.data['name'] == 'New Business Card Type'
    assert result.data['category_id'] == category.id
    assert result.data['description'] == 'A new type of business card'
    assert result.data['image'] is None

def test_create_print_product_type_with_image(client, create_categories):
    """Test successful creation of a print product type with image"""
    category, _, _ = create_categories
    
    data = {
        'name': 'Business Card with Image',
        'category_id': category.id,
        'description': 'Business card type with image',
        'image': 'http://example.com/image.jpg'
    }
    
    result = PrintProductController.create_print_product_type(data)
    
    assert result.status is True
    assert result.data['name'] == 'Business Card with Image'
    assert result.data['image'] == 'http://example.com/image.jpg'

def test_create_print_product_type_name_required(client, create_categories):
    """Test creation fails when name is missing"""
    category, _, _ = create_categories
    
    data = {
        'category_id': category.id,
        'description': 'Description without name'
    }
    
    result = PrintProductController.create_print_product_type(data)
    
    assert result.status is False
    assert result.error == PrintProductErrors.PRODUCT_TYPE_NAME_REQUIRED.value

def test_create_print_product_type_category_id_required(client, create_categories):
    """Test creation fails when category_id is missing"""
    category, _, _ = create_categories
    
    data = {
        'name': 'Business Card Type',
        'description': 'Description without category'
    }
    
    result = PrintProductController.create_print_product_type(data)
    
    assert result.status is False
    assert result.error == PrintProductErrors.PRODUCT_TYPE_CATEGORY_ID_REQUIRED.value

def test_create_print_product_type_description_required(client, create_categories):
    """Test creation fails when description is missing"""
    category, _, _ = create_categories
    
    data = {
        'name': 'Business Card Type',
        'category_id': category.id
    }
    
    result = PrintProductController.create_print_product_type(data)
    
    assert result.status is False
    assert result.error == PrintProductErrors.PRODUCT_TYPE_DESCRIPTION_REQUIRED.value

def test_create_print_product_type_name_too_short(client, create_categories):
    """Test creation fails when name is too short"""
    category, _, _ = create_categories
    
    data = {
        'name': 'A',  # Only 1 character
        'category_id': category.id,
        'description': 'Description'
    }
    
    result = PrintProductController.create_print_product_type(data)
    
    assert result.status is False
    assert result.error == PrintProductErrors.PRODUCT_TYPE_NAME_TOO_SHORT.value

def test_create_print_product_type_name_too_long(client, create_categories):
    """Test creation fails when name is too long"""
    category, _, _ = create_categories
    
    data = {
        'name': 'A' * 256,  # 256 characters (exceeds 255 limit)
        'category_id': category.id,
        'description': 'Description'
    }
    
    result = PrintProductController.create_print_product_type(data)
    
    assert result.status is False
    assert result.error == PrintProductErrors.PRODUCT_TYPE_NAME_TOO_LONG.value

def test_create_print_product_type_category_not_found(client, create_categories):
    """Test creation fails when category doesn't exist"""
    data = {
        'name': 'Business Card Type',
        'category_id': 9999,  # Non-existent category
        'description': 'Description'
    }
    
    result = PrintProductController.create_print_product_type(data)
    
    assert result.status is False
    assert result.error == PrintProductErrors.PRODUCT_TYPE_CATEGORY_NOT_FOUND.value

def test_create_print_product_type_name_already_exists(client, create_categories):
    """Test creation fails when name already exists in the same category"""
    category, _, _ = create_categories
    
    # First creation should succeed
    data1 = {
        'name': 'Duplicate Name',
        'category_id': category.id,
        'description': 'First description'
    }
    result1 = PrintProductController.create_print_product_type(data1)
    assert result1.status is True
    
    # Second creation with same name in same category should fail
    data2 = {
        'name': 'Duplicate Name',
        'category_id': category.id,
        'description': 'Second description'
    }
    result2 = PrintProductController.create_print_product_type(data2)
    
    assert result2.status is False
    assert result2.error == PrintProductErrors.PRODUCT_TYPE_NAME_ALREADY_EXISTS.value

def test_create_print_product_type_same_name_different_category(client, create_categories):
    """Test creation succeeds when same name exists in different category"""
    category1, category2, _ = create_categories
    
    # First creation in category1
    data1 = {
        'name': 'Same Name',
        'category_id': category1.id,
        'description': 'First description'
    }
    result1 = PrintProductController.create_print_product_type(data1)
    assert result1.status is True
    
    # Second creation with same name in category2 should succeed
    data2 = {
        'name': 'Same Name',
        'category_id': category2.id,
        'description': 'Second description'
    }
    result2 = PrintProductController.create_print_product_type(data2)
    
    assert result2.status is True
    assert result2.data['name'] == 'Same Name'
    assert result2.data['category_id'] == category2.id

def test_create_print_product_type_commit_fails(client, create_categories):
    """Test creation fails when database commit fails"""
    category, _, _ = create_categories
    
    data = {
        'name': 'Business Card Type',
        'category_id': category.id,
        'description': 'Description'
    }
    
    with patch("server.controllers.print_product_controller.db.session.commit", side_effect=Exception("Database fail")):
        result = PrintProductController.create_print_product_type(data)
        
        assert result.status is False
        assert PrintProductErrors.FAILED_TO_CREATE_PRODUCT_TYPE.value in result.error

# ========== UPDATE PRINT PRODUCT TYPE TESTS ==========

def test_update_print_product_type_description_success(client, create_product_types):
    """Test successful update of product type description"""
    product_type, _, _ = create_product_types
    
    result = PrintProductController.update_print_product_type(
        product_type.id, 
        description="Updated description"
    )
    
    assert result.status is True
    assert result.data["message"] == PrintProductSuccessMessages.PRODUCT_TYPE_UPDATED_SUCCESSFULLY.value
    
    # Verify database was updated
    updated = db.session.get(PrintProductType, product_type.id)
    assert updated.description == "Updated description"

def test_update_print_product_type_image_success(client, create_product_types):
    """Test successful update of product type image"""
    product_type, _, _ = create_product_types
    
    image_data = FileStorage(
        stream=io.BytesIO(b"fake image data"), 
        filename="test.png", 
        content_type="image/png"
    )
    
    with patch("server.controllers.print_product_controller.current_app") as mock_current_app:
        fake_storage = MagicMock()
        fake_storage.upload_file.return_value = "http://example.com/new_image.png"
        mock_current_app.extensions = {"filestorage": fake_storage}
        
        result = PrintProductController.update_print_product_type(
            product_type.id, 
            image=image_data
        )
        
        assert result.status is True
        assert result.data["message"] == PrintProductSuccessMessages.PRODUCT_TYPE_UPDATED_SUCCESSFULLY.value
        
        # Verify database was updated
        updated = db.session.get(PrintProductType, product_type.id)
        assert updated.image == "http://example.com/new_image.png"

def test_update_print_product_type_both_description_and_image(client, create_product_types):
    """Test successful update of both description and image"""
    product_type, _, _ = create_product_types
    
    image_data = FileStorage(
        stream=io.BytesIO(b"fake image data"), 
        filename="test.png", 
        content_type="image/png"
    )
    
    with patch("server.controllers.print_product_controller.current_app") as mock_current_app:
        fake_storage = MagicMock()
        fake_storage.upload_file.return_value = "http://example.com/combined.png"
        mock_current_app.extensions = {"filestorage": fake_storage}
        
        result = PrintProductController.update_print_product_type(
            product_type.id, 
            description="Combined update",
            image=image_data
        )
        
        assert result.status is True
        assert result.data["message"] == PrintProductSuccessMessages.PRODUCT_TYPE_UPDATED_SUCCESSFULLY.value
        
        # Verify both were updated
        updated = db.session.get(PrintProductType, product_type.id)
        assert updated.description == "Combined update"
        assert updated.image == "http://example.com/combined.png"

def test_update_print_product_type_not_found(client):
    """Test update fails when product type doesn't exist"""
    result = PrintProductController.update_print_product_type(
        9999, 
        description="Doesn't matter"
    )
    
    assert result.status is False
    assert result.error == PrintProductErrors.PRINT_PRODUCT_TYPE_NOT_FOUND.value

def test_update_print_product_type_description_too_long(client, create_product_types):
    """Test update fails when description is too long"""
    product_type, _, _ = create_product_types
    
    long_desc = "a" * 1001  # Exceeds 1000 character limit
    
    result = PrintProductController.update_print_product_type(
        product_type.id, 
        description=long_desc
    )
    
    assert result.status is False
    assert result.error == PrintProductErrors.PRINT_PRODUCT_DESCRIPTION_TOO_LONG.value

def test_update_print_product_type_invalid_image_type(client, create_product_types):
    """Test update fails when image is not FileStorage"""
    product_type, _, _ = create_product_types
    
    result = PrintProductController.update_print_product_type(
        product_type.id, 
        image="not a file"
    )
    
    assert result.status is False
    assert result.error == PrintProductErrors.INVALID_IMAGE_FILE.value

def test_update_print_product_type_empty_image_filename(client, create_product_types):
    """Test update fails when image filename is empty"""
    product_type, _, _ = create_product_types
    
    empty_image = FileStorage(
        stream=io.BytesIO(b"some content"), 
        filename="", 
        content_type="image/png"
    )
    
    result = PrintProductController.update_print_product_type(
        product_type.id, 
        image=empty_image
    )
    
    assert result.status is False
    assert result.error == PrintProductErrors.EMPTY_IMAGE_FILENAME.value

def test_update_print_product_type_commit_fails(client, create_product_types):
    """Test update fails when database commit fails"""
    product_type, _, _ = create_product_types
    
    with patch("server.controllers.print_product_controller.db.session.commit", side_effect=Exception("Database fail")):
        result = PrintProductController.update_print_product_type(
            product_type.id, 
            description="Should fail"
        )
        
        assert result.status is False
        assert PrintProductErrors.FAILED_TO_UPDATE_PRODUCT_TYPE.value in result.error

# ========== DELETE PRINT PRODUCT TYPE TESTS ==========

def test_delete_print_product_type_success(client, create_product_types):
    """Test successful deletion of a print product type"""
    product_type, _, _ = create_product_types
    
    result = PrintProductController.delete_print_product_type(product_type.id)
    
    assert result.status is True
    assert result.data["message"] == PrintProductSuccessMessages.PRODUCT_TYPE_DELETED_SUCCESSFULLY.value
    
    # Verify it was deleted from database
    deleted = db.session.get(PrintProductType, product_type.id)
    assert deleted is None

def test_delete_print_product_type_not_found(client):
    """Test deletion fails when product type doesn't exist"""
    result = PrintProductController.delete_print_product_type(9999)
    
    assert result.status is False
    assert result.error == PrintProductErrors.PRINT_PRODUCT_TYPE_NOT_FOUND.value

def test_delete_print_product_type_in_use(client, create_product_types):
    """Test deletion fails when product type is being used by products"""
    product_type, _, _ = create_product_types
    
    # Create a mock product object that will be returned by the query
    mock_product = MagicMock()
    mock_product.id = 1
    mock_product.name = "Product using type"
    
    with patch('server.models.print_product.PrintProduct.query') as mock_query:
        # Mock the filter_by().first() chain
        mock_filter_by = MagicMock()
        mock_filter_by.first.return_value = mock_product
        mock_query.filter_by.return_value = mock_filter_by
        
        result = PrintProductController.delete_print_product_type(product_type.id)
        assert result.status is False
        assert result.error == PrintProductErrors.PRODUCT_TYPE_IN_USE.value
        
        # Verify it was not deleted from database
        not_deleted = db.session.get(PrintProductType, product_type.id)
        assert not_deleted is not None

def test_delete_print_product_type_commit_fails(client, create_product_types):
    """Test deletion fails when database commit fails"""
    product_type, _, _ = create_product_types
    
    with patch("server.controllers.print_product_controller.db.session.commit", side_effect=Exception("Database fail")):
        result = PrintProductController.delete_print_product_type(product_type.id)
        
        assert result.status is False
        assert PrintProductErrors.FAILED_TO_DELETE_PRODUCT_TYPE.value in result.error
