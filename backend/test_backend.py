import sys
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def run_all_tests():
    print("=== Starting EnergiQ Backend API Verification Tests ===")

    # 1. Test Root
    res = client.get("/")
    assert res.status_code == 200, f"Root failed: {res.text}"
    print("✓ GET / -> 200 OK")

    # 2. Test Summary
    res = client.get("/summary")
    assert res.status_code == 200, f"Summary failed: {res.text}"
    summary = res.json()
    assert "total_energy_kwh" in summary
    assert "estimated_cost" in summary
    assert "active_anomalies" in summary
    assert "predicted_next_day_kwh" in summary
    assert "estimated_co2_kg" in summary
    print(f"✓ GET /summary -> 200 OK | Metrics: {summary}")

    # 3. Test Consumption (All & Filtered)
    res = client.get("/consumption")
    assert res.status_code == 200, f"Consumption failed: {res.text}"
    data = res.json()["data"]
    assert len(data) > 0
    print(f"✓ GET /consumption -> 200 OK | Loaded {len(data)} records")

    res_filtered = client.get("/consumption?building=Building A&room=Lab 1")
    assert res_filtered.status_code == 200
    filtered_data = res_filtered.json()["data"]
    assert all(d["building"] == "Building A" and d["room"] == "Lab 1" for d in filtered_data)
    print(f"✓ GET /consumption?building=Building A&room=Lab 1 -> 200 OK | Loaded {len(filtered_data)} records")

    # 4. Test Anomalies (All & Filtered)
    res = client.get("/anomalies")
    assert res.status_code == 200, f"Anomalies failed: {res.text}"
    anomalies = res.json()["anomalies"]
    assert len(anomalies) > 0
    print(f"✓ GET /anomalies -> 200 OK | Detected {len(anomalies)} anomalies")

    res_anom_filt = client.get("/anomalies?building=Building B")
    assert res_anom_filt.status_code == 200
    filtered_anom = res_anom_filt.json()["anomalies"]
    assert all(a["building"] == "Building B" for a in filtered_anom)
    print(f"✓ GET /anomalies?building=Building B -> 200 OK | Loaded {len(filtered_anom)} records")

    # 5. Test Prediction
    res = client.get("/prediction")
    assert res.status_code == 200, f"Prediction failed: {res.text}"
    preds = res.json()["predictions"]
    assert len(preds) > 0
    print(f"✓ GET /prediction -> 200 OK | Loaded {len(preds)} predictions")

    # 6. Test Rooms Hierarchy
    res = client.get("/rooms")
    assert res.status_code == 200, f"Rooms failed: {res.text}"
    buildings = res.json()["buildings"]
    assert len(buildings) > 0
    print(f"✓ GET /rooms -> 200 OK | Found {len(buildings)} building(s)")

    # 7. Test Recommendations
    res = client.get("/recommendations")
    assert res.status_code == 200, f"Recommendations failed: {res.text}"
    recs = res.json()["recommendations"]
    assert len(recs) > 0
    print(f"✓ GET /recommendations -> 200 OK | Generated {len(recs)} recommendation(s)")

    print("\n🎉 ALL BACKEND API TESTS PASSED SUCCESSFULLY! 🎉")

if __name__ == "__main__":
    run_all_tests()
