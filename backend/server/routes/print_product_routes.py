from flask_restx import Namespace, Resource, fields
from server.controllers.print_product_controller import PrintProductController


# Define a namespace for print products
api = Namespace("Products", description="Operations related to products")

# Define a product response model
product_model = api.model("Product", {
    "id": fields.Integer(description="Product ID"),
    "sku": fields.String(description="Stock Keeping Unit (SKU)"),
    "name": fields.String(description="Product name"),
    "category": fields.String(description="Product category"),
    "enabled": fields.Integer(description="Product availability status"),
})


@api.route("/products")
class PrintProductResource(Resource):
    """Ressource for fetching print products"""

    @api.doc(description="Fetch list of available print products")
    @api.marshal_list_with(product_model, code=200)
    @api.response(500, "Server error")
    def get(self):
        """Retrieve available print products"""
        result = PrintProductController.get_products()
        print(result)

        if result.status:
            return result.data, 200
        else:
            return {"error": result.error}, 500
        
@api.route("/products/<string:category>")
@api.param("category", "The category of the products to retriev")
class PrintProductByCategoryResource(Resource):
    """Resource for fetching print products by category"""

    @api.doc(description="Fetch list of print products listed by category")
    @api.marshal_list_with(product_model, code=200)
    @api.response(404, "Category not found")
    @api.response(500, "Server error")
    def get(self, category):
        """Retrieve print products by category"""
        result = PrintProductController.get_products_by_category(category)
        if result.status:
            if not result.data:
                return {"message": "No products found for this category"}, 404
            return result.data, 200
        else:
            return {"error": result.error}, 500