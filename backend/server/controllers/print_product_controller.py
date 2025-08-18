from server.controllers import Result
from enum import Enum
from server.config import sinalite
from server.config import database as db
from server.models.print_product import PrintProductCategory, PrintProductType
from markupsafe import escape
import logging
from werkzeug.datastructures import FileStorage
from flask import current_app

logger = logging.getLogger(__name__)

class PrintProductErrors(Enum):
    FAILED_TO_FETCH_PRINT_PRODUCTS = "Failed to fetch products"
    FAILED_TO_FETCH_PRINT_PRODUCT_CATEGORIES = "Failed to fetch print product categories"
    FAILED_TO_FETCH_ENABLED_PRINT_PRODUCT_CATEGORIES = "Failed to fetch enabled print product categories"
    PRINT_PRODUCT_CATEGORY_NOT_FOUND = "Print product category not found"
    FAILED_TO_UPDATE_PRODUCT_CATEGORY = "Failed to update product categories"
    PRINT_PRODUCT_DESCRIPTION_TOO_LONG = "Description is too long (max 1000 characters)."
    INVALID_IMAGE_FILE = "Invalid image"
    EMPTY_IMAGE_FILENAME = "Empty image filename"
    INVALID_IMAGE_URL = "Invalid image URL. Must start with http:// or https://"
    
    # Product Type specific errors
    PRINT_PRODUCT_TYPE_NOT_FOUND = "Print product type not found"
    FAILED_TO_CREATE_PRODUCT_TYPE = "Failed to create product type"
    FAILED_TO_UPDATE_PRODUCT_TYPE = "Failed to update product type"
    FAILED_TO_DELETE_PRODUCT_TYPE = "Failed to delete product type"
    PRODUCT_TYPE_NAME_REQUIRED = "Product type name is required"
    PRODUCT_TYPE_CATEGORY_ID_REQUIRED = "Product type category ID is required"
    PRODUCT_TYPE_DESCRIPTION_REQUIRED = "Product type description is required"
    PRODUCT_TYPE_CATEGORY_NOT_FOUND = "Product type category not found"
    PRODUCT_TYPE_NAME_ALREADY_EXISTS = "Product type name already exists in this category"
    PRODUCT_TYPE_IN_USE = "Cannot delete product type: It is being used by existing products"
    PRODUCT_TYPE_NAME_TOO_LONG = "Product type name is too long (max 255 characters)"
    PRODUCT_TYPE_NAME_TOO_SHORT = "Product type name is too short (min 2 characters)"
    FAILED_TO_FETCH_PRINT_PRODUCT_TYPES = "Failed to fetch print product types"
    
class PrintProductSuccessMessages(Enum):
    UPDATED_PRINT_PRODUCT_CATEGORY_STATUS_SUCCESSFULLY = "Updated print product category status successfully"
    PRINT_PRODUCT_CATEGORY_IN_SYNC = "Print products are in sync"
    PRODUCT_CATEGORY_UPDATED_SUCCESSFULLY = "Product category updated successfully"
    
    # Product Type specific success messages
    PRODUCT_TYPE_CREATED_SUCCESSFULLY = "Product type created successfully"
    PRODUCT_TYPE_UPDATED_SUCCESSFULLY = "Product type updated successfully"
    PRODUCT_TYPE_DELETED_SUCCESSFULLY = "Product type deleted successfully"

class PrintProductController:

    @staticmethod
    def get_all_product_categories() -> Result:
        """Retrieve all product categories from the database."""

        result = Result()

        table_is_empty = (PrintProductCategory.query.first() is None) # TODO: Add test case
        if(table_is_empty):
            result.data = []
            return result

        # Always fetch categories sorted by name
        categories = PrintProductCategory.query.order_by(PrintProductCategory.name.asc()).all()

        if categories:
            result.data = [category.to_dict() for category in categories]
        else:
            result.status = False
            result.error = PrintProductErrors.FAILED_TO_FETCH_PRINT_PRODUCT_CATEGORIES.value
        
        return result

    @staticmethod
    def get_enabled_product_categories() -> Result:
        """Retrieve only enabled categories."""
        
        result = Result()

        table_is_empty = (PrintProductCategory.query.first() is None) # TODO: Add test case
        if(table_is_empty):
            result.data = []
            return result

        logger.info("Fetching enabled categories ... ")
        categories = PrintProductCategory.query.filter_by(enabled=True).all()
       
        num_categories = len(categories)
        if num_categories == 1:
            logger.info(f"Found {num_categories} enabled category ... ")
            result.data = [categories[0].to_dict()]
        else:
            logger.info(f"Found {num_categories} enabled categories ... ")
            result.data = [category.to_dict() for category in categories]
        
        return result

    @staticmethod
    def update_print_product_category_status(category_id: int, enabled: bool):
        """Enable or disable a category."""
        result = Result()

        try:
            table_is_empty = (PrintProductCategory.query.first() is None)  # TODO: Add test case
            if table_is_empty:
                result.data = []
                return result

            # Fetch the category by ID
            category = db.session.get(PrintProductCategory, category_id)
            if not category:
                logger.warning(f"Category with ID {category_id} not found.")
                result.status = False
                result.error = PrintProductErrors.PRINT_PRODUCT_CATEGORY_NOT_FOUND.value
                return result

            # Update category status
            category.enabled = enabled
            db.session.commit()  

            result.data = {"message": PrintProductSuccessMessages.UPDATED_PRINT_PRODUCT_CATEGORY_STATUS_SUCCESSFULLY.value}
        
        except Exception as e:
            logger.error(f"Failed to update category status: {e}")
            db.session.rollback()  # Rollback in case of failure
            result.status = False
            result.error = "An error occurred while updating the category."
        

        return result

    @staticmethod
    def sync_print_product_categories() -> Result:
        """Sync categories from Sinalite API (manual trigger)."""
        result = Result()

        logger.info("Requesting all product categories from Sinalite ...")
        try:
            sinalite_categories = sinalite.get_product_categories()
            if not sinalite_categories:
                raise ValueError("No categories returned from Sinalite API")
        except Exception as e:
            logger.error(f"Failed to fetch categories from Sinalite API: {e}")
            result.data = {"message": "Failed to sync product categories"}
            return result

        logger.info("Fetching all product categories currently known ...")
        try:
            existing_categories = {
                category.name for category in PrintProductCategory.query.with_entities(PrintProductCategory.name).all()
            }
        except Exception as e:
            logger.error(f"Failed to fetch existing product categories: {e}")
            result.data = {"message": "Failed to sync product categories"}
            return result

        new_categories = [
            PrintProductCategory(name=name) for name in sinalite_categories if name not in existing_categories
        ]

        logger.info(f"Found {len(new_categories)} new {'category' if len(new_categories) == 1 else 'categories'} ...")

        if new_categories:
            logger.info("Syncing product categories ...")
            try:
                db.session.bulk_save_objects(new_categories) 
                db.session.commit() 
                logger.info("Synced product categories successfully ...")
            except Exception as e:
                logger.error(f"Failed to sync new product categories: {e}")
                db.session.rollback()  # ✅ Rollback in case of failure
                result.data = {"message": "Failed to sync product categories"}
                return result

        result.data = {"message": PrintProductSuccessMessages.PRINT_PRODUCT_CATEGORY_IN_SYNC.value}
        return result

    @staticmethod
    def get_all_products() -> Result:
        """Fetch print products from Sinalite"""

        result = Result()
        products = sinalite.get_products()

        if products:
            result.data = products
        else:
            result.status = False
            result.error = PrintProductErrors.FAILED_TO_FETCH_PRINT_PRODUCTS.value
        
        return result
    
    @staticmethod
    def get_all_products_by_category(category_id: int) -> Result:
        """Fetch print products from Sinalite API by category ID, regardless of enabled status"""
        result = Result()

        table_is_empty = (PrintProductCategory.query.first() is None) # TODO: Add test case
        if(table_is_empty):
            result.data = []
            return result
        
        # Validate category exists (regardless of enabled status)
        local_category = db.session.get(PrintProductCategory, category_id)
        if not local_category:
            result.status = False
            result.error = PrintProductErrors.PRINT_PRODUCT_CATEGORY_NOT_FOUND.value
            return result

        # Fetch all products from sinalite
        all_products = sinalite.get_products()

        # Filter products by category name
        filtered_products = [product for product in all_products if product['category'] == local_category.name]

        # Always return a list even if empty
        result.data = filtered_products

        return result

    @staticmethod
    def get_enabled_products_by_category(category_id: int) -> Result:
        """Fetch print products from Sinalite API by category ID, ensuring category is enabled in the database"""
        result = Result()

        table_is_empty = (PrintProductCategory.query.first() is None) # TODO: Add test case
        if(table_is_empty):
            result.data = []
            return result

        # Validate category exists and is enabled in the database
        local_category = db.session.get(PrintProductCategory, category_id)
        if not local_category or not local_category.enabled:
            result.status = False
            result.error = PrintProductErrors.PRINT_PRODUCT_CATEGORY_NOT_FOUND.value
            return result
        
        # Fetch all products from sinalite
        all_products = sinalite.get_products()

        # Filter products by category name
        filtered_products = [product for product in all_products if product['category'] == local_category.name]

        # Always return a list even if empty
        result.data = filtered_products

        return result

    @staticmethod
    def update_print_product_category(category_id: int, description: str = None, image=None) -> Result:
        """Update the description or image of a product category securely"""
        result = Result()

        try:
            category = db.session.get(PrintProductCategory, category_id)

            if not category:
                result.status = False
                result.error = PrintProductErrors.PRINT_PRODUCT_CATEGORY_NOT_FOUND.value
                return result

            # Sanitize and validate description
            if description:
                description = escape(description.strip())
                if len(description) > 1000:
                    result.status = False
                    result.error = PrintProductErrors.PRINT_PRODUCT_DESCRIPTION_TOO_LONG.value
                    return result
                category.description = description

            # Handle image upload
            if image is not None:
                if isinstance(image, FileStorage):
                    # Ensure file is not empty
                    if image.filename == "":
                        result.status = False
                        
                        result.error = PrintProductErrors.EMPTY_IMAGE_FILENAME.value
                        return result

                    content_type = image.content_type
                    filename = image.filename
                    file_data = image.read()

                    # Upload file using current filestorage
                    filestorage = current_app.extensions["filestorage"]
                    image_url = filestorage.upload_file(file_data, filename, content_type)

                    # Save URL in DB
                    category.image = image_url
                else:
                    result.status = False
                    result.error = PrintProductErrors.INVALID_IMAGE_FILE.value
                    return result

            db.session.commit()
            result.data = {"message": PrintProductSuccessMessages.PRODUCT_CATEGORY_UPDATED_SUCCESSFULLY.value}

        except Exception as e:
            db.session.rollback()
            result.status = False
            result.error = f"{PrintProductErrors.FAILED_TO_UPDATE_PRODUCT_CATEGORY.value}: {str(e)}"

        return result

    @staticmethod
    def get_all_print_product_types() -> Result:
        """Retrieve all print product types from the database."""
        result = Result()

        try:
            # Check if table is empty
            table_is_empty = (PrintProductType.query.first() is None)
            if table_is_empty:
                result.data = []
                result.status = True
                return result

            # Fetch all product types sorted by name
            product_types = PrintProductType.query.order_by(PrintProductType.name.asc()).all()

            if product_types:
                result.data = [product_type.to_dict() for product_type in product_types]
                result.status = True
            else:
                result.status = False
                result.error = PrintProductErrors.FAILED_TO_FETCH_PRINT_PRODUCT_TYPES.value
            
        except Exception as e:
            result.status = False
            result.error = f"{PrintProductErrors.FAILED_TO_FETCH_PRINT_PRODUCT_TYPES.value}: {str(e)}"
            logger.error(f"Error fetching print product types: {str(e)}")

        
        return result

    @staticmethod
    def create_print_product_type(data: dict) -> Result:
        """Create a new print product type in the database."""
        result = Result()
        
        try:
            # Extract fields from input data
            name = data.get('name')
            category_id = data.get('category_id')
            description = data.get('description')
            image = data.get('image')

            # Validate required fields
            if not name:
                result.status = False
                result.error = PrintProductErrors.PRODUCT_TYPE_NAME_REQUIRED.value
                return result
            
            if not category_id:
                result.status = False
                result.error = PrintProductErrors.PRODUCT_TYPE_CATEGORY_ID_REQUIRED.value
                return result
                
            if not description:
                result.status = False
                result.error = PrintProductErrors.PRODUCT_TYPE_DESCRIPTION_REQUIRED.value
                return result
            
            # Validate name length
            if len(name) < 2:
                result.status = False
                result.error = PrintProductErrors.PRODUCT_TYPE_NAME_TOO_SHORT.value
                return result
                
            if len(name) > 255:
                result.status = False
                result.error = PrintProductErrors.PRODUCT_TYPE_NAME_TOO_LONG.value
                return result
            
            # Validate category exists
            category = db.session.get(PrintProductCategory, category_id)
            if not category:
                result.status = False
                result.error = PrintProductErrors.PRODUCT_TYPE_CATEGORY_NOT_FOUND.value
                return result

            # Check if product type with same name already exists in this category
            existing_type = PrintProductType.query.filter_by(
                name=name, 
                category_id=category_id
            ).first()
            
            if existing_type:
                result.status = False
                result.error = PrintProductErrors.PRODUCT_TYPE_NAME_ALREADY_EXISTS.value
                return result

            # Create new product type (image is optional)
            new_product_type = PrintProductType(
                name=name,
                category_id=category_id,
                description=description,
                image=image if image else None
            )
            
            db.session.add(new_product_type)
            db.session.commit()
            
            result.data = new_product_type.to_dict()
            result.status = True
            
        except Exception as e:
            db.session.rollback()
            result.status = False
            result.error = f"{PrintProductErrors.FAILED_TO_CREATE_PRODUCT_TYPE.value}: {str(e)}"
            logger.error(f"Error creating product type: {str(e)}")

        return result

    @staticmethod
    def update_print_product_type(type_id: int, description: str = None, image=None) -> Result:
        """Update the description or image of a product type securely"""
        result = Result()

        try:
            product_type = db.session.get(PrintProductType, type_id)

            if not product_type:
                result.status = False
                result.error = PrintProductErrors.PRINT_PRODUCT_TYPE_NOT_FOUND.value
                return result

            # Sanitize and validate description
            if description:
                description = escape(description.strip())
                if len(description) > 1000:
                    result.status = False
                    result.error = PrintProductErrors.PRINT_PRODUCT_DESCRIPTION_TOO_LONG.value
                    return result
                product_type.description = description

            # Handle image upload
            if image is not None:
                if isinstance(image, FileStorage):
                    # Ensure file is not empty
                    if image.filename == "":
                        result.status = False
                        result.error = PrintProductErrors.EMPTY_IMAGE_FILENAME.value
                        return result

                    content_type = image.content_type
                    filename = image.filename
                    file_data = image.read()

                    # Upload file using current filestorage
                    filestorage = current_app.extensions["filestorage"]
                    image_url = filestorage.upload_file(file_data, filename, content_type)

                    # Save URL in DB
                    product_type.image = image_url
                else:
                    result.status = False
                    result.error = PrintProductErrors.INVALID_IMAGE_FILE.value
                    return result

            db.session.commit()
            result.data = {"message": PrintProductSuccessMessages.PRODUCT_TYPE_UPDATED_SUCCESSFULLY.value}

        except Exception as e:
            db.session.rollback()
            result.status = False
            result.error = f"{PrintProductErrors.FAILED_TO_UPDATE_PRODUCT_TYPE.value}: {str(e)}"

        return result

    @staticmethod
    def delete_print_product_type(type_id: int) -> Result:
        """Delete a print product type from the database."""
        result = Result()

        try:
            product_type = db.session.get(PrintProductType, type_id)

            if not product_type:
                result.status = False
                result.error = PrintProductErrors.PRINT_PRODUCT_TYPE_NOT_FOUND.value
                return result

            # Check if there are any products using this type
            from server.models.print_product import PrintProduct
            products_using_type = PrintProduct.query.filter_by(type_id=type_id).first()
            
            print(products_using_type)
            if products_using_type:
                result.status = False
                result.error = PrintProductErrors.PRODUCT_TYPE_IN_USE.value
                return result

            # Delete the product type
            db.session.delete(product_type)
            db.session.commit()

            result.data = {"message": PrintProductSuccessMessages.PRODUCT_TYPE_DELETED_SUCCESSFULLY.value}
            result.status = True

        except Exception as e:
            db.session.rollback()
            result.status = False
            result.error = f"{PrintProductErrors.FAILED_TO_DELETE_PRODUCT_TYPE.value}: {str(e)}"
            logger.error(f"Error deleting product type: {str(e)}")

        return result