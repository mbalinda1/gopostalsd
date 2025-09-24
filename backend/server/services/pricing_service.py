"""
Pricing Service for Go Postal SD Application

This service implements the Strategy and Factory design patterns to handle
product pricing, cart management, and shipping calculations using the Sinalite API.

The service provides a clean abstraction layer for pricing operations and
implements caching strategies to optimize API usage and performance.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import logging
from server import database as db
from server.models.pricing import (
    ProductOption, ProductPricing, Cart, CartItem, 
    ShippingOption, ProductVariant, StoreCode
)
from server.thirdparty.sinalite import SinaliteAdapter
from server.thirdparty.helpers import logger

logger = logging.getLogger(__name__)


class PricingStrategy(ABC):
    """
    Abstract base class for pricing strategies.
    Implements the Strategy pattern to allow different pricing approaches.
    """
    
    @abstractmethod
    def calculate_price(self, product_id: int, options: List[int], store_code: int) -> Optional[Dict]:
        """Calculate price for a product with given options."""
        pass


class SinalitePricingStrategy(PricingStrategy):
    """
    Concrete pricing strategy that uses the Sinalite API for pricing calculations.
    Implements caching to reduce API calls and improve performance.
    """
    
    def __init__(self, sinalite_adapter: SinaliteAdapter):
        self.sinalite = sinalite_adapter
        self.cache_duration = timedelta(hours=1)  # Cache pricing for 1 hour
    
    def calculate_price(self, product_id: int, options: List[int], store_code: int) -> Optional[Dict]:
        """
        Calculate price using Sinalite API key-based pricing with caching.
        
        Args:
            product_id: Sinalite product ID
            options: List of selected option IDs
            store_code: Store code (6 for Canada, 9 for US)
            
        Returns:
            Dict containing price and package information, or None if failed
        """
        try:
            # Create option key for caching (sorted for consistency)
            option_key = "-".join(map(str, sorted(options)))
            
            # Check cache first
            cached_pricing = self._get_cached_pricing(product_id, store_code, option_key)
            if cached_pricing:
                logger.info(f"Using cached pricing for product {product_id}")
                return cached_pricing
            
            # Use key-based pricing from Sinalite API
            pricing_data = self.sinalite.get_price_by_key(product_id, option_key)
            if not pricing_data:
                logger.error(f"Failed to get pricing for product {product_id} with key {option_key}")
                return None
            
            # Handle the response format - Sinalite returns a list with price dict
            price_value = 0
            if isinstance(pricing_data, list) and len(pricing_data) > 0:
                price_value = pricing_data[0].get('price', 0)
            elif isinstance(pricing_data, dict):
                price_value = pricing_data.get('price', 0)
            
            # Format the response to match expected structure
            formatted_pricing = {
                'price': price_value,
                'packageInfo': {},  # Will be populated from product details if needed
                'productOptions': options
            }
            
            # Cache the result
            self._cache_pricing(product_id, store_code, option_key, formatted_pricing, options)
            
            return formatted_pricing
            
        except Exception as e:
            logger.error(f"Error calculating price for product {product_id}: {str(e)}")
            return None
    
    def _get_cached_pricing(self, product_id: int, store_code: int, option_key: str) -> Optional[Dict]:
        """Retrieve cached pricing data if still valid."""
        try:
            cached = ProductPricing.query.filter_by(
                product_id=product_id,
                store_code=store_code,
                option_key=option_key
            ).first()
            
            if cached and cached.updated_at > datetime.utcnow() - self.cache_duration:
                return {
                    'price': str(cached.price),
                    'packageInfo': cached.package_info,
                    'productOptions': cached.product_options
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving cached pricing: {str(e)}")
            return None
    
    def _cache_pricing(self, product_id: int, store_code: int, option_key: str, 
                      pricing_data: Dict, options: List[int]) -> None:
        """Cache pricing data for future use."""
        try:
            # Check if already exists
            existing = ProductPricing.query.filter_by(
                product_id=product_id,
                store_code=store_code,
                option_key=option_key
            ).first()
            
            if existing:
                # Update existing record
                existing.price = pricing_data.get('price', 0)
                existing.package_info = pricing_data.get('packageInfo')
                existing.product_options = pricing_data.get('productOptions')
                existing.updated_at = datetime.utcnow()
            else:
                # Create new record
                new_pricing = ProductPricing(
                    product_id=product_id,
                    store_code=store_code,
                    option_key=option_key,
                    price=pricing_data.get('price', 0),
                    package_info=pricing_data.get('packageInfo'),
                    product_options=pricing_data.get('productOptions')
                )
                db.session.add(new_pricing)
            
            db.session.commit()
            logger.info(f"Cached pricing for product {product_id}")
            
        except Exception as e:
            logger.error(f"Error caching pricing: {str(e)}")
            db.session.rollback()


class PricingService:
    """
    Main pricing service that coordinates pricing operations.
    Implements the Facade pattern to provide a simple interface for complex operations.
    """
    
    def __init__(self, sinalite_adapter: SinaliteAdapter):
        self.sinalite = sinalite_adapter
        self.pricing_strategy = SinalitePricingStrategy(sinalite_adapter)
    
    def get_product_options(self, product_id: int, store_code: int) -> List[Dict]:
        """
        Get available options for a product.
        
        Args:
            product_id: Sinalite product ID
            store_code: Store code (6 for Canada, 9 for US)
            
        Returns:
            List of product options grouped by category
        """
        try:
            # Check cache first
            cached_options = self._get_cached_options(product_id, store_code)
            if cached_options:
                return cached_options
            
            # Fetch from API
            product_details = self.sinalite.get_product_details(product_id, store_code)
            if not product_details or len(product_details) < 1:
                logger.error(f"No product details found for product {product_id}")
                return []
            
            options = product_details[0]  # First array contains options
            
            # Cache the options
            self._cache_options(product_id, store_code, options)
            
            # Group options by category
            grouped_options = self._group_options_by_category(options)
            return grouped_options
            
        except Exception as e:
            logger.error(f"Error getting product options for product {product_id}: {str(e)}")
            return []
    
    def get_product_variants(self, product_id: int, offset: int = 0) -> List[Dict]:
        """
        Get product variants with pricing.
        
        Args:
            product_id: Sinalite product ID
            offset: Pagination offset
            
        Returns:
            List of variants with prices and keys
        """
        try:
            # Check cache first
            cached_variants = self._get_cached_variants(product_id, offset)
            if cached_variants:
                return cached_variants
            
            # Fetch from API
            variants = self.sinalite.get_product_variants(product_id, offset)
            if not variants:
                logger.error(f"No variants found for product {product_id}")
                return []
            
            # Cache the variants
            self._cache_variants(product_id, offset, variants)
            
            return variants
            
        except Exception as e:
            logger.error(f"Error getting product variants for product {product_id}: {str(e)}")
            return []
    
    def calculate_product_price(self, product_id: int, options: List[int], store_code: int) -> Optional[Dict]:
        """
        Calculate price for a product with selected options.
        
        Args:
            product_id: Sinalite product ID
            options: List of selected option IDs
            store_code: Store code (6 for Canada, 9 for US)
            
        Returns:
            Dict containing price and package information
        """
        return self.pricing_strategy.calculate_price(product_id, options, store_code)
    
    def get_shipping_estimates(self, cart_items: List[Dict], shipping_info: Dict) -> List[Dict]:
        """
        Get shipping estimates for cart items.
        
        Args:
            cart_items: List of cart items with productId and options
            shipping_info: Shipping destination information
            
        Returns:
            List of available shipping options
        """
        try:
            # Prepare items for API call
            api_items = []
            for item in cart_items:
                api_items.append({
                    'productId': item['product_id'],
                    'options': item['selected_options']
                })
            
            # Get shipping estimates from API
            estimates = self.sinalite.get_shipping_estimate(api_items, shipping_info)
            
            # Format response
            shipping_options = []
            for estimate in estimates:
                if len(estimate) >= 4:
                    shipping_options.append({
                        'carrier_name': estimate[0],
                        'method_name': estimate[1],
                        'price': float(estimate[2]),
                        'shipping_days': int(estimate[3])
                    })
            
            return shipping_options
            
        except Exception as e:
            logger.error(f"Error getting shipping estimates: {str(e)}")
            return []
    
    def _get_cached_options(self, product_id: int, store_code: int) -> Optional[List[Dict]]:
        """Retrieve cached product options if available."""
        try:
            cached_options = ProductOption.query.filter_by(
                product_id=product_id
            ).all()
            
            if cached_options:
                return self._group_options_by_category([opt.to_dict() for opt in cached_options])
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving cached options: {str(e)}")
            return None
    
    def _cache_options(self, product_id: int, store_code: int, options: List[Dict]) -> None:
        """Cache product options for future use."""
        try:
            # Clear existing options for this product
            ProductOption.query.filter_by(product_id=product_id).delete()
            
            # Add new options
            for option in options:
                new_option = ProductOption(
                    sinalite_option_id=option['id'],
                    product_id=product_id,
                    group=option['group'],
                    name=option['name']
                )
                db.session.add(new_option)
            
            db.session.commit()
            logger.info(f"Cached {len(options)} options for product {product_id}")
            
        except Exception as e:
            logger.error(f"Error caching options: {str(e)}")
            db.session.rollback()
    
    def _group_options_by_category(self, options: List[Dict]) -> List[Dict]:
        """Group options by their category/group."""
        grouped = {}
        for option in options:
            group = option.get('group', 'Other')
            if group not in grouped:
                grouped[group] = []
            grouped[group].append(option)
        
        # Convert to list format
        result = []
        for group, group_options in grouped.items():
            result.append({
                'group': group,
                'options': group_options
            })
        
        return result
    
    def _get_cached_variants(self, product_id: int, offset: int) -> Optional[List[Dict]]:
        """Retrieve cached product variants if available."""
        try:
            cached_variants = ProductVariant.query.filter_by(
                product_id=product_id
            ).offset(offset).limit(1000).all()
            
            if cached_variants:
                return [variant.to_dict() for variant in cached_variants]
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving cached variants: {str(e)}")
            return None
    
    def _cache_variants(self, product_id: int, offset: int, variants: List[Dict]) -> None:
        """Cache product variants for future use."""
        try:
            # Clear existing variants for this product
            ProductVariant.query.filter_by(product_id=product_id).delete()
            
            # Add new variants
            for variant in variants:
                new_variant = ProductVariant(
                    product_id=product_id,
                    variant_key=variant['key'],
                    price=variant['price']
                )
                db.session.add(new_variant)
            
            db.session.commit()
            logger.info(f"Cached {len(variants)} variants for product {product_id}")
            
        except Exception as e:
            logger.error(f"Error caching variants: {str(e)}")
            db.session.rollback()


class CartService:
    """
    Service for managing shopping cart operations.
    Implements the Repository pattern for data access.
    """
    
    def __init__(self, pricing_service: PricingService):
        self.pricing_service = pricing_service
    
    def get_or_create_cart(self, session_id: str, user_id: Optional[int] = None, 
                          store_code: int = StoreCode.CANADA.value) -> Cart:
        """
        Get existing cart or create a new one.
        
        Args:
            session_id: Session identifier
            user_id: Optional user ID for logged-in users
            store_code: Store code (6 for Canada, 9 for US)
            
        Returns:
            Cart instance
        """
        try:
            cart = Cart.query.filter_by(session_id=session_id).first()
            
            if not cart:
                cart = Cart(
                    session_id=session_id,
                    user_id=user_id,
                    store_code=store_code
                )
                db.session.add(cart)
                db.session.commit()
                logger.info(f"Created new cart for session {session_id}")
            else:
                # Update store code if different
                if cart.store_code != store_code:
                    cart.store_code = store_code
                    db.session.commit()
            
            return cart
            
        except Exception as e:
            logger.error(f"Error getting/creating cart: {str(e)}")
            db.session.rollback()
            raise
    
    def add_item_to_cart(self, cart_id: int, product_id: int, product_name: str,
                        product_sku: str, selected_options: List[int], 
                        quantity: int = 1) -> Optional[CartItem]:
        """
        Add item to cart with pricing calculation.
        
        Args:
            cart_id: Cart ID
            product_id: Sinalite product ID
            product_name: Product name
            product_sku: Product SKU
            selected_options: List of selected option IDs
            quantity: Quantity to add
            
        Returns:
            CartItem instance or None if failed
        """
        try:
            cart = Cart.query.get(cart_id)
            if not cart:
                logger.error(f"Cart {cart_id} not found")
                return None
            
            # Calculate price
            pricing = self.pricing_service.calculate_product_price(
                product_id, selected_options, cart.store_code
            )
            
            if not pricing:
                logger.error(f"Could not calculate price for product {product_id}")
                return None
            
            # Create option key
            option_key = "-".join(map(str, sorted(selected_options)))
            
            # Check if item already exists
            existing_item = CartItem.query.filter_by(
                cart_id=cart_id,
                product_id=product_id,
                option_key=option_key
            ).first()
            
            if existing_item:
                # Update quantity
                existing_item.quantity += quantity
                existing_item.total_price = existing_item.quantity * existing_item.unit_price
                existing_item.updated_at = datetime.utcnow()
                db.session.commit()
                return existing_item
            
            # Create new cart item
            unit_price = float(pricing.get('price', 0))
            total_price = unit_price * quantity
            
            cart_item = CartItem(
                cart_id=cart_id,
                product_id=product_id,
                product_name=product_name,
                product_sku=product_sku,
                quantity=quantity,
                selected_options=selected_options,
                option_key=option_key,
                unit_price=unit_price,
                total_price=total_price,
                package_info=pricing.get('packageInfo')
            )
            
            db.session.add(cart_item)
            db.session.commit()
            
            logger.info(f"Added item to cart {cart_id}: {product_name}")
            return cart_item
            
        except Exception as e:
            logger.error(f"Error adding item to cart: {str(e)}")
            db.session.rollback()
            return None
    
    def update_cart_item_quantity(self, cart_item_id: int, quantity: int) -> bool:
        """
        Update quantity of a cart item.
        
        Args:
            cart_item_id: Cart item ID
            quantity: New quantity
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cart_item = CartItem.query.get(cart_item_id)
            if not cart_item:
                logger.error(f"Cart item {cart_item_id} not found")
                return False
            
            cart_item.quantity = quantity
            cart_item.total_price = cart_item.quantity * cart_item.unit_price
            cart_item.updated_at = datetime.utcnow()
            
            db.session.commit()
            logger.info(f"Updated cart item {cart_item_id} quantity to {quantity}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating cart item quantity: {str(e)}")
            db.session.rollback()
            return False
    
    def remove_cart_item(self, cart_item_id: int) -> bool:
        """
        Remove item from cart.
        
        Args:
            cart_item_id: Cart item ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cart_item = CartItem.query.get(cart_item_id)
            if not cart_item:
                logger.error(f"Cart item {cart_item_id} not found")
                return False
            
            db.session.delete(cart_item)
            db.session.commit()
            
            logger.info(f"Removed cart item {cart_item_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing cart item: {str(e)}")
            db.session.rollback()
            return False
    
    def get_cart_total(self, cart_id: int) -> Dict[str, float]:
        """
        Calculate cart total including subtotal and tax.
        
        Args:
            cart_id: Cart ID
            
        Returns:
            Dict with subtotal, tax, and total amounts
        """
        try:
            cart_items = CartItem.query.filter_by(cart_id=cart_id).all()
            
            subtotal = sum(item.total_price for item in cart_items)
            # TODO: Implement tax calculation based on location
            tax = 0.0  # Placeholder for tax calculation
            total = subtotal + tax
            
            return {
                'subtotal': float(subtotal),
                'tax': float(tax),
                'total': float(total),
                'item_count': len(cart_items)
            }
            
        except Exception as e:
            logger.error(f"Error calculating cart total: {str(e)}")
            return {'subtotal': 0.0, 'tax': 0.0, 'total': 0.0, 'item_count': 0}
