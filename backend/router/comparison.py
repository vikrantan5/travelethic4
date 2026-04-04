from fastapi import APIRouter, HTTPException, status
from loguru import logger
from models.comparison import (
    ComparisonRequest,
    ComparisonResponse,
    ProsCons,
    BestFor,
    FinalRecommendation,
)
from config.groq_agents import GroqAgent
import json
import re

router = APIRouter(prefix="/api/compare", tags=["Destination Comparison"])

# Create a dedicated comparison agent
comparison_agent_groq = GroqAgent(
    name="Destination Comparison Expert",
    role="objective travel destination comparison and recommendation specialist",
    instructions=[
        "You are a world-class travel advisor with expertise in destinations globally",
        "Compare destinations based on FACTUAL, REAL-WORLD data and verified information",
        "Be completely OBJECTIVE and UNBIASED - never favor one destination without clear evidence",
        "Analyze across multiple criteria: actual costs, safety records, infrastructure, activities, cultural offerings",
        "Consider the user's specific budget level and travel style when making recommendations",
        "Provide balanced, honest pros and cons backed by real data and examples",
        "Match recommendations to user preferences - budget travelers need different advice than luxury travelers",
        "Account for factors like: real cost of living, documented safety statistics, weather patterns, accessibility, local culture",
        "Provide specific, actionable insights with real-world context and examples",
        "Be thorough but concise - focus on facts over opinions",
        "CRITICAL: Do NOT have a default favorite - each comparison should be evaluated independently",
        "CRITICAL: Different user profiles should get different recommendations even for the same destinations",
        "Return output in valid JSON format only - no markdown formatting",
    ],
    temperature=0.2,  # Lower temperature for more consistent, factual responses
    max_tokens=4096,
)

@router.post(
    "/",
    response_model=ComparisonResponse,
    summary="Compare Two Destinations",
    description="Compare two travel destinations and get a detailed analysis with pros, cons, and recommendations",
)
async def compare_destinations(request: ComparisonRequest) -> ComparisonResponse:
    """
    Compare two destinations and provide detailed analysis.

    Args:
        request: Comparison request with two destinations and user preferences

    Returns:
        ComparisonResponse: Detailed comparison with pros, cons, and recommendations
    """
    try:
        logger.info(f"Comparing destinations: {request.place_1} vs {request.place_2}")

        prompt = f"""
You are an expert travel advisor with extensive knowledge of destinations worldwide. Compare these two travel destinations objectively and accurately based on real-world data, facts, and traveler experiences.

**Destinations to Compare:**
- Place 1: {request.place_1}
- Place 2: {request.place_2}

**User Context:**
- Budget Level: {request.budget}
- Travel Style: {request.travel_style}
- Preferences: {request.user_preferences or 'Not specified'}

**Important Instructions:**
1. Base your comparison on REAL, FACTUAL information about each destination
2. Be completely OBJECTIVE - do NOT favor one destination over another without clear reasoning
3. Consider the actual characteristics of each place, not stereotypes
4. Evaluate based on: cost of living, safety, accessibility, attractions, weather, culture, activities, infrastructure
5. Match recommendations to the user's stated budget and travel style
6. If one place is genuinely better for a category, state it clearly with specific reasons
7. If both places are similar for a category, acknowledge that

**Analysis Framework:**
For each destination, consider:
- **Budget**: Actual average costs (accommodation, food, activities, transport)
- **Nightlife**: Quality, variety, and safety of evening entertainment options
- **Luxury Options**: Availability of high-end hotels, restaurants, and experiences
- **Water Sports**: Specific water activities available (surfing, diving, sailing, etc.)
- **Family-Friendly**: Kid-friendly attractions, safety, facilities, educational value
- **Accessibility**: How easy it is to reach and navigate
- **Cultural Richness**: Museums, historical sites, local experiences
- **Natural Beauty**: Beaches, mountains, landscapes, parks
- **Food Scene**: Local cuisine quality, variety, dining options
- **Safety**: Crime rates, tourist safety, health infrastructure

Provide your analysis in this EXACT JSON format (no markdown, no extra text):

{{
    "place_1": "{request.place_1}",
    "place_2": "{request.place_2}",
    "best_for": {{
        "budget": "Choose the destination that is ACTUALLY more affordable based on real costs. State: '{request.place_1}' or '{request.place_2}'",
        "nightlife": "Choose based on ACTUAL nightlife quality and variety. State: '{request.place_1}' or '{request.place_2}'",
        "luxury_honeymoon": "Choose based on ACTUAL luxury options and romantic atmosphere. State: '{request.place_1}' or '{request.place_2}'",
        "water_sports": "Choose based on ACTUAL water sports availability and quality. State: '{request.place_1}' or '{request.place_2}'",
        "family_trip": "Choose based on ACTUAL family-friendly features. State: '{request.place_1}' or '{request.place_2}'"
    }},
    "pros_cons": {{
        "{request.place_1}": {{
            "pros": [
                "Specific, factual advantage 1 (with real data/examples)",
                "Specific, factual advantage 2 (with real data/examples)",
                "Specific, factual advantage 3 (with real data/examples)",
                "Specific, factual advantage 4 (with real data/examples)",
                "Specific, factual advantage 5 (with real data/examples)"
            ],
            "cons": [
                "Specific, honest limitation 1 (with real context)",
                "Specific, honest limitation 2 (with real context)",
                "Specific, honest limitation 3 (with real context)",
                "Specific, honest limitation 4 (with real context)"
            ]
        }},
        "{request.place_2}": {{
            "pros": [
                "Specific, factual advantage 1 (with real data/examples)",
                "Specific, factual advantage 2 (with real data/examples)",
                "Specific, factual advantage 3 (with real data/examples)",
                "Specific, factual advantage 4 (with real data/examples)",
                "Specific, factual advantage 5 (with real data/examples)"
            ],
            "cons": [
                "Specific, honest limitation 1 (with real context)",
                "Specific, honest limitation 2 (with real context)",
                "Specific, honest limitation 3 (with real context)",
                "Specific, honest limitation 4 (with real context)"
            ]
        }}
    }},
    "final_recommendation": {{
        "best_option": "Based on user's budget ({request.budget}), travel style ({request.travel_style}), and overall value, choose: '{request.place_1}' or '{request.place_2}'",
        "reason": "Provide 2-3 specific, data-backed sentences explaining WHY this destination is better for THIS specific user profile. Reference actual features, costs, and benefits that match their stated preferences."
    }}
}}

**CRITICAL**: 
- Your recommendation MUST be based on the user's budget level and travel style
- A budget traveler should get different recommendations than a luxury traveler
- DO NOT always recommend the same place - evaluate based on the specific comparison
- Be honest about which destination truly fits better for the user's needs
- Return ONLY valid JSON, no markdown code blocks, no explanations outside the JSON

Return the JSON now:
"""

        response = await comparison_agent_groq.arun(prompt)
        logger.info(f"Received comparison response length: {len(response)} characters")
        logger.debug(f"Raw comparison response: {response[:500]}...")
        
        # Log which destination was recommended
        if "best_option" in response:
            logger.info(f"Response contains best_option field")

        # Extract JSON from response
        try:
            # Try to find JSON object in response
            start_idx = response.find("{")
            end_idx = response.rfind("}") + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                comparison_data = json.loads(json_str)

                            # Validate and create response
                # Additional validation to ensure proper place names are used
                if comparison_data["place_1"].lower() != request.place_1.lower():
                    logger.warning(f"Place 1 mismatch: expected '{request.place_1}', got '{comparison_data['place_1']}'")
                    comparison_data["place_1"] = request.place_1
                    
                if comparison_data["place_2"].lower() != request.place_2.lower():
                    logger.warning(f"Place 2 mismatch: expected '{request.place_2}', got '{comparison_data['place_2']}'")
                    comparison_data["place_2"] = request.place_2
                
                # Validate that best_option is one of the two places
                best_option = comparison_data["final_recommendation"]["best_option"]
                place_1_lower = request.place_1.lower()
                place_2_lower = request.place_2.lower()
                best_option_lower = best_option.lower()
                
                if place_1_lower not in best_option_lower and place_2_lower not in best_option_lower:
                    logger.error(f"Invalid best_option: '{best_option}' is neither '{request.place_1}' nor '{request.place_2}'")
                    # Default to place_1 but log the error
                    comparison_data["final_recommendation"]["best_option"] = request.place_1
                    comparison_data["final_recommendation"]["reason"] = f"Both destinations offer unique experiences. {comparison_data['final_recommendation'].get('reason', 'Consider your personal preferences.')}"
                
                logger.info(f"Final recommendation: {comparison_data['final_recommendation']['best_option']}")
                
                return ComparisonResponse(
                    place_1=comparison_data["place_1"],
                    place_2=comparison_data["place_2"],
                    best_for=BestFor(**comparison_data["best_for"]),
                    pros_cons={
                        place: ProsCons(**data)
                        for place, data in comparison_data["pros_cons"].items()
                    },
                    final_recommendation=FinalRecommendation(
                        **comparison_data["final_recommendation"]
                    ),
                )
            else:
                raise ValueError("No JSON object found in response")

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Error parsing comparison response: {str(e)}")
            logger.error(f"Raw response: {response}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to parse comparison response: {str(e)}",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing destinations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compare destinations: {str(e)}",
        )
