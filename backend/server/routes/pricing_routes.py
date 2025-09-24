"""
Pricing Routes for Go Postal SD Application

This module registers pricing-related routes with the Flask application.
It initializes the pricing controller and makes it available to the app context.
"""

from flask import Flask
from server.controllers.pricing_controller import pricing_ns, PricingController
from server.thirdparty.sinalite import SinaliteAdapter
import logging

logger = logging.getLogger(__name__)


def register_pricing_routes(app: Flask) -> None:
    """
    Register pricing routes with the Flask application.
    
    Args:
        app: Flask application instance
    """
    try:
        # Get Sinalite adapter from app extensions
        sinalite_adapter = app.extensions.get('sinalite')
        
        if not sinalite_adapter:
            logger.error("Sinalite adapter not found in app extensions")
            return
        
        # Create pricing controller
        pricing_controller = PricingController(sinalite_adapter)
        
        # Store controller in app extensions for use by resources
        app.extensions['pricing_controller'] = pricing_controller
        
        # Register the namespace with the API
        from server.config import swagger
        swagger.add_namespace(pricing_ns, path='/api/pricing')
        
        logger.info("Pricing routes registered successfully")
        
    except Exception as e:
        logger.error(f"Error registering pricing routes: {str(e)}")
        raise
