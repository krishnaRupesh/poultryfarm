import os
import sys
import unittest
import time
from datetime import date, timedelta

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, backend_dir)

from app import create_app
from app.models import db, Shed, FlockBatch, Incident, FeedItem, FeedPurchase, Customer, Order, Payment


class TestFlockAndRestoreEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config["TESTING"] = True
        cls.client = cls.app.test_client()

    def test_01_shed_crud_and_restore(self):
        """Test shed creation, listing, updating, soft delete, and restore."""
        suffix = int(time.time() * 1000)
        shed_name = f"Test Shed X {suffix}"

        # 1. Create shed
        res = self.client.post("/api/flock/sheds", json={
            "shed_name": shed_name,
            "capacity": 15000,
            "shed_type": "Layer House",
            "notes": "Automated ventilation",
            "created_by": "tester"
        })
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        shed_id = data["shed_id"]
        self.assertEqual(data["shed_name"], shed_name)
        self.assertEqual(data["capacity"], 15000)

        # 2. Get shed
        res = self.client.get(f"/api/flock/sheds/{shed_id}")
        self.assertEqual(res.status_code, 200)

        # 3. Update shed
        res = self.client.put(f"/api/flock/sheds/{shed_id}", json={
            "capacity": 16000,
            "notes": "Updated note"
        })
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["capacity"], 16000)

        # 4. Soft delete shed
        res = self.client.delete(f"/api/flock/sheds/{shed_id}")
        self.assertEqual(res.status_code, 200)

        # 5. Verify omitted by default from active list
        res = self.client.get("/api/flock/sheds")
        active_ids = [s["shed_id"] for s in res.get_json()]
        self.assertNotIn(shed_id, active_ids)

        # 6. Verify included with include_deleted=true
        res = self.client.get("/api/flock/sheds?include_deleted=true")
        all_ids = [s["shed_id"] for s in res.get_json()]
        self.assertIn(shed_id, all_ids)

        # 7. Restore shed
        res = self.client.post(f"/api/flock/sheds/{shed_id}/restore")
        self.assertEqual(res.status_code, 200)
        res = self.client.get("/api/flock/sheds")
        active_ids = [s["shed_id"] for s in res.get_json()]
        self.assertIn(shed_id, active_ids)

    def test_02_flock_batch_crud_and_age_weeks(self):
        """Test flock batch lifecycle with dynamic age_weeks, soft delete and restore."""
        # Get or create a shed
        res = self.client.get("/api/flock/sheds")
        sheds = res.get_json()
        shed_id = sheds[0]["shed_id"] if sheds else None

        suffix = int(time.time() * 1000)
        batch_name = f"2026-test-{suffix}"
        # Placed 14 weeks ago (98 days)
        placement = (date.today() - timedelta(days=98)).isoformat()

        # 1. Create batch
        res = self.client.post("/api/flock/batches", json={
            "batch_name": batch_name,
            "shed_id": shed_id,
            "breed": "Lohmann Brown",
            "initial_birds": 12000,
            "current_birds": 11950,
            "placement_date": placement,
            "status": "Active",
            "notes": "Healthy pullets",
            "created_by": "tester"
        })
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        batch_id = data["batch_id"]
        self.assertEqual(data["batch_name"], batch_name)
        # initial_age_weeks (18) + elapsed weeks (14) = 32 weeks
        self.assertEqual(data["age_weeks"], 32)

        # 2. Update batch
        res = self.client.put(f"/api/flock/batches/{batch_id}", json={
            "current_birds": 11920
        })
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["current_birds"], 11920)

        # 3. Soft delete batch
        res = self.client.delete(f"/api/flock/batches/{batch_id}")
        self.assertEqual(res.status_code, 200)

        # 4. Restore batch
        res = self.client.post(f"/api/flock/batches/{batch_id}/restore")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["batch"]["batch_name"], batch_name)

    def test_03_incidents_optional_shed_batch_and_restore(self):
        """Test incidents with optional shed/batch attribution, soft delete and restore."""
        res = self.client.get("/api/flock/sheds")
        sheds = res.get_json()
        shed_id = sheds[0]["shed_id"] if sheds else None

        res = self.client.get("/api/flock/batches")
        batches = res.get_json()
        batch_id = batches[0]["batch_id"] if batches else None

        suffix = int(time.time() * 1000)
        # Create incident attributed to Shed & Batch
        res = self.client.post("/api/incidents/", json={
            "name": f"Feeder Belt Jam {suffix}",
            "incident_type": "machinery",
            "incident_date": "2026-10-18",
            "shed_id": shed_id,
            "batch_id": batch_id,
            "amount_spent": 145.50,
            "summary": "Replaced worn out drive belt",
            "created_by": "tester"
        })
        self.assertEqual(res.status_code, 201)
        inc = res.get_json()
        inc_id = inc["incident_id"]
        self.assertEqual(inc["shed_id"], shed_id)
        self.assertEqual(inc["batch_id"], batch_id)

        # Soft delete incident
        res = self.client.delete(f"/api/incidents/{inc_id}")
        self.assertEqual(res.status_code, 200)

        # Confirm not in active list
        res = self.client.get("/api/incidents/")
        active_ids = [i["incident_id"] for i in res.get_json()]
        self.assertNotIn(inc_id, active_ids)

        # Restore incident
        res = self.client.post(f"/api/incidents/{inc_id}/restore")
        self.assertEqual(res.status_code, 200)
        res = self.client.get("/api/incidents/")
        active_ids = [i["incident_id"] for i in res.get_json()]
        self.assertIn(inc_id, active_ids)

    def test_04_feed_item_and_purchase_restore(self):
        """Test feed item and purchase soft delete and stock restoration."""
        suffix = int(time.time() * 1000)
        item_res = self.client.post("/api/feed/items", json={
            "name": f"Mineral Premix {suffix}",
            "category": "Supplements",
            "current_stock_kg": 100.0,
            "average_cost_per_kg": 2.50,
            "created_by": "tester"
        })
        self.assertEqual(item_res.status_code, 201)
        item_id = item_res.get_json()["item_id"]

        # Purchase 50 kg
        p_res = self.client.post("/api/feed/purchases", json={
            "item_id": item_id,
            "purchase_date": "2026-10-18",
            "quantity": 50.0,
            "unit": "kg",
            "total_cost": 125.0,
            "created_by": "tester"
        })
        self.assertEqual(p_res.status_code, 201)
        purchase_id = p_res.get_json()["purchase"]["purchase_id"]

        # Check stock is 150 kg
        res = self.client.get(f"/api/feed/items/{item_id}")
        self.assertEqual(res.get_json()["current_stock_kg"], 150.0)

        # Delete purchase -> stock should drop back to 100 kg
        res = self.client.delete(f"/api/feed/purchases/{purchase_id}")
        self.assertEqual(res.status_code, 200)
        res = self.client.get(f"/api/feed/items/{item_id}")
        self.assertEqual(res.get_json()["current_stock_kg"], 100.0)

        # Restore purchase -> stock should return to 150 kg
        res = self.client.post(f"/api/feed/purchases/{purchase_id}/restore")
        self.assertEqual(res.status_code, 200)
        res = self.client.get(f"/api/feed/items/{item_id}")
        self.assertEqual(res.get_json()["current_stock_kg"], 150.0)

        # Soft delete feed item
        res = self.client.delete(f"/api/feed/items/{item_id}")
        self.assertEqual(res.status_code, 200)

        # Restore feed item
        res = self.client.post(f"/api/feed/items/{item_id}/restore")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["item"]["item_id"], item_id)

    def test_05_daily_analysis_batch_breakdown(self):
        """Test daily analysis returns batch_breakdown array comparing Sheds/Batches."""
        res = self.client.get("/api/analysis/daily?date=2026-10-05")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("batch_breakdown", data)
        self.assertIsInstance(data["batch_breakdown"], list)
        self.assertGreaterEqual(len(data["batch_breakdown"]), 1)
        first_batch = data["batch_breakdown"][0]
        self.assertIn("batch_name", first_batch)
        self.assertIn("shed_name", first_batch)
        self.assertIn("active_birds", first_batch)
        self.assertIn("cost_per_egg", first_batch)


if __name__ == "__main__":
    unittest.main()
