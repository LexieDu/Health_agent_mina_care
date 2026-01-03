from pydantic import BaseModel
class Medicine(BaseModel):
    name: str
    dosage: str
    count: int
    expiration_date: str

class MedicineResponse(BaseModel):
    id: int
    name: str
    dosage: str
    count: int
    expiration_date: str
    created_at: str
