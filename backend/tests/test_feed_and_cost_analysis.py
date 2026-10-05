import os
import sys
import unittest
import json
import time

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, backend_dir)

from app import create_app
from app.models import db, FeedItem, FeedPurchase, DailyFlockStatus, DailyFeedConsumption, DailyEggOperation


class TestFeedInventoryAndCostAnalysis(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config["TESTING"] = True
        cls.client = cls.app.test_client()

    def test_01_feed_items_crud(self):
        """Test creating, listing, updating, and deleting feed inventory items."""
        suffix = int(time.time() * 1000)
        item_name = f"Test Barley {suffix}"

        # 1. Create Feed Item
        payload = {
            "name": item_name,
            "category": "Grains",
            "default_unit": "kg",
            "current_stock_kg": 500.0,
            "average_cost_per_kg": 0.35,
            "reorder_level_kg": 150.0,
            "created_by": "test_user"
        }
        res = self.client.post("/api/feed/items", json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        item_id = data["item_id"]
        self.assertEqual(data["name"], item_name)
        self.assertEqual(data["current_stock_mt"], 0.5)

        # 2. Get Feed Item
        res = self.client.get(f"/api/feed/items/{item_id}")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["name"], item_name)

        # 3. Update Feed Item
        res = self.client.put(f"/api/feed/items/{item_id}", json={
            "reorder_level_kg": 200.0,
            "category": "Organic Grains"
        })
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["reorder_level_kg"], 200.0)
        self.assertEqual(res.get_json()["category"], "Organic Grains")

        # 4. Soft Delete Feed Item
        res = self.client.delete(f"/api/feed/items/{item_id}")
        self.assertEqual(res.status_code, 200)

        # Verify not returned in active list
        res = self.client.get("/api/feed/items")
        names = [item["name"] for item in res.get_json()]
        self.assertNotIn(item_name, names)

    def test_02_feed_purchase_and_wac(self):
        """Test recording a purchase in Metric Tons and Weighted Average Cost recalculation."""
        suffix = int(time.time() * 1000)
        item_name = f"Test Sorghum {suffix}"

        res = self.client.post("/api/feed/items", json={
            "name": item_name,
            "category": "Grains",
            "current_stock_kg": 1000.0,
            "average_cost_per_kg": 0.20,
            "reorder_level_kg": 100.0,
            "created_by": "test"
        })
        self.assertEqual(res.status_code, 201)
        item_id = res.get_json()["item_id"]

        # Purchase 2 Metric Tons (2,000 kg) for $600 ($0.30/kg)
        res = self.client.post("/api/feed/purchases", json={
            "item_id": item_id,
            "purchase_date": "2026-10-15",
            "quantity": 2.0,
            "unit": "MT",
            "total_cost": 600.0,
            "vendor_name": "Test Grain Supplier",
            "invoice_no": "INV-TEST-01",
            "created_by": "test"
        })
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        purchase = data["purchase"]
        updated_item = data["updated_item"]

        self.assertEqual(purchase["quantity_kg"], 2000.0)
        self.assertEqual(purchase["quantity_mt"], 2.0)
        self.assertEqual(purchase["cost_per_kg"], 0.30)
        self.assertEqual(updated_item["current_stock_kg"], 3000.0)
        self.assertAlmostEqual(updated_item["average_cost_per_kg"], 0.2667, places=3)

    def test_03_flock_status(self):
        """Test logging daily flock count."""
        test_date = "2026-10-20"
        res = self.client.post("/api/daily/flock", json={
            "date": test_date,
            "active_birds": 12000,
            "mortality": 5,
            "remarks": "Healthy flock"
        })
        self.assertIn(res.status_code, (200, 201))
        data = res.get_json()
        self.assertEqual(data["active_birds"], 12000)
        self.assertEqual(data["mortality"], 5)

        # Retrieve flock
        res = self.client.get(f"/api/daily/flock?date={test_date}")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["active_birds"], 12000)

    def test_04_daily_feed_consumption_and_egg_ops(self):
        """Test daily feeding and egg operations with partial sales on a designated date."""
        test_date = "2026-10-25"

        # 1. Set flock for test_date
        self.client.post("/api/daily/flock", json={
            "date": test_date,
            "active_birds": 10000,
            "mortality": 2
        })

        # 2. Get a feed item
        res = self.client.get("/api/feed/items")
        items = res.get_json()
        corn = next((i for i in items if "corn" in i["name"].lower()), items[0])
        initial_stock = corn["current_stock_kg"]

        # Clean existing consumption for test_date if any
        res_existing = self.client.get(f"/api/daily/consumption?date={test_date}")
        for c in res_existing.get_json():
            self.client.delete(f"/api/daily/consumption/{c['consumption_id']}")

        # Consume 1 Metric Ton (1,000 kg) on test_date
        res = self.client.post("/api/daily/consumption", json={
            "date": test_date,
            "items": [
                {
                    "item_id": corn["item_id"],
                    "quantity": 1.0,
                    "unit": "MT",
                    "remarks": "1 MT corn feed"
                }
            ]
        })
        self.assertEqual(res.status_code, 201)

        # 3. Record egg operations with partial sales
        res = self.client.post("/api/daily/egg-operations", json={
            "date": test_date,
            "opening_stock": 500,
            "eggs_produced": 8500,
            "damaged_eggs": 40,
            "eggs_sold": 6000,  # Partial sales: 6,000 out of (500 + 8,500 - 40 = 8,960)
            "egg_price_per_unit": 0.08,
            "price_unit": "per_egg",
            "remarks": "6,000 sold, 2,960 stored"
        })
        self.assertIn(res.status_code, (200, 201))
        egg_data = res.get_json()
        self.assertEqual(egg_data["eggs_available"], 8960)
        self.assertEqual(egg_data["eggs_sold"], 6000)
        self.assertEqual(egg_data["closing_stock"], 2960)
        self.assertEqual(egg_data["actual_revenue"], 480.0)

        # 4. Verify analysis on test_date
        res = self.client.get(f"/api/analysis/daily?date={test_date}")
        self.assertEqual(res.status_code, 200)
        analysis = res.get_json()

        feed = analysis["feed"]
        flock = analysis["flock"]
        prod = analysis["production"]
        sales = analysis["sales_and_stock"]
        prof = analysis["profitability"]

        self.assertEqual(flock["active_birds"], 10000)
        self.assertEqual(feed["total_feed_mt"], 1.0)
        self.assertEqual(feed["total_feed_kg"], 1000.0)

        # Cost per bird = feed_cost / 10,000
        expected_cost_per_bird = round(feed["total_feed_cost"] / 10000.0, 4)
        self.assertAlmostEqual(feed["feed_cost_per_bird"], expected_cost_per_bird, places=3)

        # Production cost per egg = feed_cost / 8,500
        expected_cost_per_egg = round(feed["total_feed_cost"] / 8500.0, 4)
        self.assertAlmostEqual(prod["production_cost_per_egg"], expected_cost_per_egg, places=3)

        # Profit margin per egg = 0.08 - expected_cost_per_egg
        expected_margin = round(0.08 - expected_cost_per_egg, 4)
        self.assertAlmostEqual(prof["profit_margin_per_egg"], expected_margin, places=3)

        # Realized profit = 6,000 * expected_margin
        expected_profit = round(6000 * expected_margin, 2)
        self.assertAlmostEqual(prof["realized_gross_profit"], expected_profit, delta=1.0)


if __name__ == "__main__":
    unittest.main()
