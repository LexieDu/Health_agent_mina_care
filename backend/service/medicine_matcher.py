"""
Medicine Matcher - Smart inventory matching for MinaCare
Matches symptoms to medicine types and checks inventory availability
"""

from typing import List, Dict, Any


class MedicineMatcher:
    """
    Intelligently matches needed medicine types with user's inventory
    """
    
    # Medicine type mappings
    MEDICINE_TYPES = {
        "pain_reliever": ["aspirin", "ibuprofen", "paracetamol", "tylenol", "acetaminophen", "advil", "motrin"],
        "fever_reducer": ["aspirin", "ibuprofen", "paracetamol", "tylenol", "acetaminophen"],
        "anti_inflammatory": ["ibuprofen", "aspirin", "naproxen", "advil"],
        "cold_flu": ["dayquil", "nyquil", "theraflu", "cold medicine"],
        "allergy": ["benadryl", "claritin", "zyrtec", "allegra", "antihistamine"],
        "stomach": ["antacid", "tums", "pepto", "pepto-bismol"],
        "cough": ["cough syrup", "dextromethorphan", "robitussin"]
    }
    
    @staticmethod
    def normalize_name(name: str) -> str:
        """Normalize medicine name for matching"""
        return name.lower().strip()
    
    @classmethod
    def find_matching_medicines(cls, needed_types: List[str], inventory: List[Any]) -> Dict[str, Any]:
        """
        Find medicines in inventory that match needed types
        
        Args:
            needed_types: List of medicine types needed (e.g., ["pain_reliever", "fever_reducer"])
            inventory: List of Medicine objects from user's inventory
            
        Returns:
            {
                "available": [list of matching Medicine objects],
                "missing_types": [list of types not found],
                "recommendations": [list of medicine names to buy]
            }
        """
        available = []
        found_types = set()
        
        # Check each medicine in inventory
        for medicine in inventory:
            med_name = cls.normalize_name(medicine.name)
            
            # Check if this medicine matches any needed type
            for needed_type in needed_types:
                if needed_type in cls.MEDICINE_TYPES:
                    type_medicines = cls.MEDICINE_TYPES[needed_type]
                    
                    # Check if medicine name contains any of the type keywords
                    for keyword in type_medicines:
                        if keyword in med_name:
                            if medicine not in available:
                                available.append(medicine)
                                found_types.add(needed_type)
                            break
        
        # Determine what's missing
        missing_types = [t for t in needed_types if t not in found_types]
        
        # Generate purchase recommendations
        recommendations = []
        for missing_type in missing_types:
            if missing_type in cls.MEDICINE_TYPES:
                # Recommend the first 2 options from each type
                recommendations.extend(cls.MEDICINE_TYPES[missing_type][:2])
        
        return {
            "available": available,
            "missing_types": missing_types,
            "recommendations": list(set(recommendations))  # Remove duplicates
        }
    
    @classmethod
    def get_medicine_info(cls, medicine: Any) -> str:
        """
        Format medicine information for display
        
        Args:
            medicine: Medicine object
            
        Returns:
            Formatted string with medicine details
        """
        return f"{medicine.name} ({medicine.dosage}) - {medicine.count} available, expires {medicine.expiration_date}"
    
    @classmethod
    def analyze_inventory_status(cls, match_result: Dict[str, Any]) -> str:
        """
        Generate human-readable inventory status
        
        Args:
            match_result: Result from find_matching_medicines()
            
        Returns:
            Status string: "available", "partially_available", or "not_available"
        """
        if match_result["available"] and not match_result["missing_types"]:
            return "available"
        elif match_result["available"] and match_result["missing_types"]:
            return "partially_available"
        else:
            return "not_available"