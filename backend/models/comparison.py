from pydantic import BaseModel, field_validator, Field
from typing import Dict, List


class ComparisonRequest(BaseModel):
    place_1: str = Field(..., min_length=2, description="First destination to compare")
    place_2: str = Field(..., min_length=2, description="Second destination to compare")
    user_preferences: str = ""
    budget: str = Field(default="moderate", pattern="^(budget|moderate|luxury)$")
    travel_style: str = Field(default="balanced", pattern="^(backpacker|balanced|luxury|adventure|relaxation)$")
    
    @field_validator('place_1', 'place_2')
    @classmethod
    def validate_places(cls, v: str) -> str:
        """Ensure place names are properly formatted"""
        if not v or not v.strip():
            raise ValueError("Place name cannot be empty")
        return v.strip().title()
    
    @field_validator('place_2')
    @classmethod
    def validate_different_places(cls, v: str, info) -> str:
        """Ensure the two places are different"""
        place_1 = info.data.get('place_1', '').lower()
        if v.lower() == place_1:
            raise ValueError("Cannot compare a place with itself. Please choose two different destinations.")
        return v


class ProsCons(BaseModel):
    pros: List[str] = Field(..., min_length=3, max_length=6, description="3-6 specific advantages")
    cons: List[str] = Field(..., min_length=2, max_length=5, description="2-5 specific disadvantages")
    
    @field_validator('pros', 'cons')
    @classmethod
    def validate_list_items(cls, v: List[str]) -> List[str]:
        """Ensure each item is meaningful"""
        cleaned = [item.strip() for item in v if item and item.strip()]
        if not cleaned:
            raise ValueError("List cannot be empty")
        return cleaned


class BestFor(BaseModel):
    budget: str = Field(..., description="Best destination for budget travelers")
    nightlife: str = Field(..., description="Best destination for nightlife")
    luxury_honeymoon: str = Field(..., description="Best destination for luxury honeymoon")
    water_sports: str = Field(..., description="Best destination for water sports")
    family_trip: str = Field(..., description="Best destination for family trips")


class FinalRecommendation(BaseModel):
    best_option: str = Field(..., min_length=2, description="Recommended destination")
    reason: str = Field(..., min_length=50, description="Detailed reason for recommendation (at least 50 characters)")
    
    @field_validator('reason')
    @classmethod
    def validate_reason(cls, v: str) -> str:
        """Ensure reason is substantial"""
        if len(v.strip()) < 50:
            raise ValueError("Recommendation reason must be at least 50 characters with meaningful explanation")
        return v.strip()


class ComparisonResponse(BaseModel):
    place_1: str
    place_2: str
    best_for: BestFor
    pros_cons: Dict[str, ProsCons]
    final_recommendation: FinalRecommendation