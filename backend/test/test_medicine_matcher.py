"""
Unit tests for Medicine Matcher Service
Run with: pytest backend/test/test_medicine_matcher.py -v
"""

import pytest
from service.medicine_matcher import MedicineMatcher


# Mock Medicine class for testing
class MockMedicine:
    def __init__(self, name, dosage, count, expiration_date):
        self.name = name
        self.dosage = dosage
        self.count = count
        self.expiration_date = expiration_date


# Test fixtures
@pytest.fixture
def sample_inventory():
    """Sample inventory for testing"""
    return [
        MockMedicine("Aspirin", "500mg", 20, "2026-12-31"),
        MockMedicine("Ibuprofen", "200mg", 30, "2025-08-15"),
        MockMedicine("DayQuil", "15ml", 10, "2025-12-31"),
        MockMedicine("Benadryl", "25mg", 15, "2026-03-20")
    ]


@pytest.fixture
def empty_inventory():
    """Empty inventory for testing"""
    return []


# Test Cases
class TestMedicineMatcher:
    
    def test_normalize_name(self):
        """Test name normalization"""
        assert MedicineMatcher.normalize_name("  ASPIRIN  ") == "aspirin"
        assert MedicineMatcher.normalize_name("Ibuprofen") == "ibuprofen"
    
    def test_find_pain_reliever_available(self, sample_inventory):
        """Test finding pain reliever when available"""
        result = MedicineMatcher.find_matching_medicines(
            ["pain_reliever"],
            sample_inventory
        )
        
        assert len(result["available"]) >= 2  # Should find Aspirin and Ibuprofen
        assert len(result["missing_types"]) == 0
        assert len(result["recommendations"]) == 0
        
        names = [m.name for m in result["available"]]
        assert "Aspirin" in names
        assert "Ibuprofen" in names
    
    def test_find_cold_medicine_available(self, sample_inventory):
        """Test finding cold medicine when available"""
        result = MedicineMatcher.find_matching_medicines(
            ["cold_flu"],
            sample_inventory
        )
        
        assert len(result["available"]) == 1
        assert result["available"][0].name == "DayQuil"
        assert len(result["missing_types"]) == 0
    
    def test_medicine_not_available(self, sample_inventory):
        """Test when requested medicine type is not in inventory"""
        result = MedicineMatcher.find_matching_medicines(
            ["stomach"],  # No stomach medicine in sample inventory
            sample_inventory
        )
        
        assert len(result["available"]) == 0
        assert "stomach" in result["missing_types"]
        assert len(result["recommendations"]) > 0
    
    def test_empty_inventory(self, empty_inventory):
        """Test with empty inventory"""
        result = MedicineMatcher.find_matching_medicines(
            ["pain_reliever", "cold_flu"],
            empty_inventory
        )
        
        assert len(result["available"]) == 0
        assert len(result["missing_types"]) == 2
        assert len(result["recommendations"]) > 0
    
    def test_multiple_types_partial_match(self, sample_inventory):
        """Test when some types are available, some are not"""
        result = MedicineMatcher.find_matching_medicines(
            ["pain_reliever", "stomach", "cold_flu"],
            sample_inventory
        )
        
        # Should find pain relievers and cold medicine
        assert len(result["available"]) >= 3
        # Should miss stomach medicine
        assert "stomach" in result["missing_types"]
        # Should recommend stomach medicine
        assert any("antacid" in rec or "tums" in rec for rec in result["recommendations"])
    
    def test_get_medicine_info(self, sample_inventory):
        """Test medicine info formatting"""
        info = MedicineMatcher.get_medicine_info(sample_inventory[0])
        
        assert "Aspirin" in info
        assert "500mg" in info
        assert "20" in info
        assert "2026-12-31" in info
    
    def test_analyze_inventory_status_available(self, sample_inventory):
        """Test status when fully available"""
        result = MedicineMatcher.find_matching_medicines(
            ["pain_reliever"],
            sample_inventory
        )
        status = MedicineMatcher.analyze_inventory_status(result)
        
        assert status == "available"
    
    def test_analyze_inventory_status_not_available(self, empty_inventory):
        """Test status when not available"""
        result = MedicineMatcher.find_matching_medicines(
            ["pain_reliever"],
            empty_inventory
        )
        status = MedicineMatcher.analyze_inventory_status(result)
        
        assert status == "not_available"
    
    def test_analyze_inventory_status_partial(self, sample_inventory):
        """Test status when partially available"""
        result = MedicineMatcher.find_matching_medicines(
            ["pain_reliever", "stomach"],  # Has pain reliever, missing stomach
            sample_inventory
        )
        status = MedicineMatcher.analyze_inventory_status(result)
        
        assert status == "partially_available"


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])