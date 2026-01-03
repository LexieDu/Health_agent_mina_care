from models.Medicine import *
from datetime import datetime, timedelta

# Helper function to generate future expiration dates
def future_date(months=12):
    return (datetime.now() + timedelta(days=30*months)).strftime("%Y-%m-%d")

medicine1 = MedicineResponse(
    id=1,
    name="Aspirin",
    dosage="500mg",
    count=20,
    expiration_date="2026-12-31",
    created_at="2024-06-01T12:00:00"
)

medicine2 = MedicineResponse(
    id=2,
    name="Advil",
    dosage="200mg",
    count=24,
    expiration_date=future_date(18),
    created_at=datetime.now().isoformat()
)

medicine3 = MedicineResponse(
    id=3,
    name="Tylenol",
    dosage="500mg",
    count=50,
    expiration_date=future_date(24),
    created_at=datetime.now().isoformat()
)

medicine4 = MedicineResponse(
    id=4,
    name="Midol Complete",
    dosage="2 caplets",
    count=40,
    expiration_date=future_date(20),
    created_at=datetime.now().isoformat()
)

medicine5 = MedicineResponse(
    id=5,
    name="Benadryl",
    dosage="25mg",
    count=36,
    expiration_date=future_date(15),
    created_at=datetime.now().isoformat()
)

medicine6 = MedicineResponse(
    id=6,
    name="Claritin",
    dosage="10mg",
    count=30,
    expiration_date=future_date(22),
    created_at=datetime.now().isoformat()
)

medicine7 = MedicineResponse(
    id=7,
    name="Tums",
    dosage="750mg",
    count=60,
    expiration_date=future_date(12),
    created_at=datetime.now().isoformat()
)

medicine8 = MedicineResponse(
    id=8,
    name="Pepto-Bismol",
    dosage="262mg",
    count=48,
    expiration_date=future_date(16),
    created_at=datetime.now().isoformat()
)

medicine9 = MedicineResponse(
    id=9,
    name="Zyrtec",
    dosage="10mg",
    count=45,
    expiration_date=future_date(20),
    created_at=datetime.now().isoformat()
)

medicine10 = MedicineResponse(
    id=10,
    name="Mucinex",
    dosage="600mg",
    count=20,
    expiration_date=future_date(14),
    created_at=datetime.now().isoformat()
)

medicine11 = MedicineResponse(
    id=11,
    name="Nyquil",
    dosage="30ml",
    count=12,
    expiration_date=future_date(18),
    created_at=datetime.now().isoformat()
)

medicines_db = [
    medicine1, medicine2, medicine3, medicine4, medicine5, medicine6,
    medicine7, medicine8, medicine9, medicine10, medicine11
]