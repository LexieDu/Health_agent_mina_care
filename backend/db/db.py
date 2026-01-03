from models.Medicine import *

medicine1 = MedicineResponse(
    id=1,
    name="Aspirin",
    dosage="500mg",
    count=20,
    expiration_date="2026-12-31",
    created_at="2024-06-01T12:00:00"
)

# Method 2: Create with dictionary unpacking
medicine_data = {
    "id": 2,
    "name": "Ibuprofen",
    "dosage": "200mg",
    "count": 30,
    "expiration_date": "2025-08-15",
    "created_at": "2024-06-02T15:30:00"
}
medicine2 = MedicineResponse(**medicine_data)

medicines_db = [medicine1, medicine2]