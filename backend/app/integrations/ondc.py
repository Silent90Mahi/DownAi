"""
ONDC Integration - STUB IMPLEMENTATION
NOTE: This is a stub - no real ONDC API calls
For production, integrate with ONDC marketplace API
"""
from typing import List, Dict, Optional
from datetime import datetime
from core.logging import get_logger

logger = get_logger(__name__)


class ONDCIntegration:
    """STUB: ONDC (Open Network for Digital Commerce) marketplace integration"""

    def __init__(self):
        self.mock_products = {}  # Store mock listed products
        self.mock_orders = []  # Store mock incoming orders
        logger.info("ONDC integration initialized (STUB mode)")

    async def list_product(
        self,
        product_id: int,
        product_name: str,
        category: str,
        price: float,
        description: str,
        seller_name: str,
        seller_district: str,
        images: List[str],
        trust_score: float
    ) -> Dict:
        """
        STUB: List product on ONDC marketplace

        Args:
            product_id: Internal product ID
            product_name: Product name
            category: Product category
            price: Product price
            description: Product description
            seller_name: Seller name
            seller_district: Seller district
            images: Product image URLs
            trust_score: Seller trust score

        Returns:
            Dict with ONDC listing details
        """
        try:
            # Generate mock ONDC product ID
            ondc_product_id = f"ONDC_{product_id}_{datetime.now().strftime('%Y%m%d')}"

            listing = {
                "ondc_product_id": ondc_product_id,
                "internal_product_id": product_id,
                "name": product_name,
                "category": category,
                "price": price,
                "description": description,
                "seller": {
                    "name": seller_name,
                    "location": seller_district,
                    "trust_score": trust_score
                },
                "images": images,
                "status": "active",
                "listed_at": datetime.now().isoformat(),
                "views": 0,
                "orders": 0
            }

            self.mock_products[ondc_product_id] = listing

            logger.info(f"Product listed on ONDC (STUB): {product_name} (ID: {ondc_product_id})")

            return {
                "success": True,
                "ondc_product_id": ondc_product_id,
                "status": "active",
                "marketplace_url": f"https://ondc-marketplace.in/products/{ondc_product_id}",
                "listing_date": datetime.now().strftime("%Y-%m-%d"),
                "stub": True
            }

        except Exception as e:
            logger.error(f"ONDC listing failed (STUB): {e}")
            raise

    async def sync_orders(self) -> List[Dict]:
        """
        STUB: Fetch orders from ONDC marketplace

        Returns:
            List of mock orders from ONDC
        """
        try:
            logger.info("Syncing ONDC orders (STUB)")

            # Return mock orders
            mock_orders = [
                {
                    "ondc_order_id": f"ONDC_ORD_{datetime.now().strftime('%Y%m%d%H%M%S')}_001",
                    "product_id": list(self.mock_products.keys())[0] if self.mock_products else "ONDC_001",
                    "buyer_name": "Mock Buyer 1",
                    "buyer_location": "Delhi",
                    "quantity": 2,
                    "total_amount": 500.00,
                    "status": "confirmed",
                    "order_date": datetime.now().isoformat()
                },
                {
                    "ondc_order_id": f"ONDC_ORD_{datetime.now().strftime('%Y%m%d%H%M%S')}_002",
                    "product_id": list(self.mock_products.keys())[0] if self.mock_products else "ONDC_002",
                    "buyer_name": "Mock Buyer 2",
                    "buyer_location": "Mumbai",
                    "quantity": 1,
                    "total_amount": 350.00,
                    "status": "pending",
                    "order_date": datetime.now().isoformat()
                }
            ]

            self.mock_orders.extend(mock_orders)

            return mock_orders

        except Exception as e:
            logger.error(f"ONDC order sync failed (STUB): {e}")
            raise

    async def update_product_status(
        self,
        ondc_product_id: str,
        status: str
    ) -> Dict:
        """
        STUB: Update product status on ONDC

        Args:
            ondc_product_id: ONDC product ID
            status: New status (active, inactive, sold_out)

        Returns:
            Update result
        """
        try:
            logger.info(f"Updating ONDC product status (STUB): {ondc_product_id} -> {status}")

            if ondc_product_id in self.mock_products:
                self.mock_products[ondc_product_id]["status"] = status
                self.mock_products[ondc_product_id]["updated_at"] = datetime.now().isoformat()

            return {
                "success": True,
                "ondc_product_id": ondc_product_id,
                "status": status,
                "updated_at": datetime.now().isoformat(),
                "stub": True
            }

        except Exception as e:
            logger.error(f"ONDC status update failed (STUB): {e}")
            raise

    async def get_product_analytics(
        self,
        ondc_product_id: str
    ) -> Dict:
        """
        STUB: Get product analytics from ONDC

        Args:
            ondc_product_id: ONDC product ID

        Returns:
            Mock analytics data
        """
        try:
            logger.info(f"Fetching ONDC product analytics (STUB): {ondc_product_id}")

            return {
                "ondc_product_id": ondc_product_id,
                "views": {
                    "total": 150,
                    "this_week": 45,
                    "this_month": 120
                },
                "orders": {
                    "total": 8,
                    "pending": 2,
                    "completed": 6,
                    "cancelled": 0
                },
                "revenue": {
                    "total": 4500.00,
                    "this_month": 1800.00
                },
                "rating": {
                    "average": 4.5,
                    "count": 8
                },
                "stub": True
            }

        except Exception as e:
            logger.error(f"ONDC analytics fetch failed (STUB): {e}")
            raise

    async def cancel_listing(
        self,
        ondc_product_id: str,
        reason: str
    ) -> Dict:
        """
        STUB: Cancel product listing on ONDC

        Args:
            ondc_product_id: ONDC product ID
            reason: Cancellation reason

        Returns:
            Cancellation result
        """
        try:
            logger.info(f"Cancelling ONDC listing (STUB): {ondc_product_id}, Reason: {reason}")

            if ondc_product_id in self.mock_products:
                self.mock_products[ondc_product_id]["status"] = "cancelled"
                self.mock_products[ondc_product_id]["cancelled_at"] = datetime.now().isoformat()
                self.mock_products[ondc_product_id]["cancellation_reason"] = reason

            return {
                "success": True,
                "ondc_product_id": ondc_product_id,
                "status": "cancelled",
                "cancelled_at": datetime.now().isoformat(),
                "reason": reason,
                "stub": True
            }

        except Exception as e:
            logger.error(f"ONDC listing cancellation failed (STUB): {e}")
            raise


# Global ONDC integration instance
ondc_integration = ONDCIntegration()
