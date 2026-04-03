"""
Groq-based AI Agent System for TripCraft
Replaces OpenRouter/OpenAI with Groq LLM
Now with intelligent API key rotation and failover
"""

from groq import Groq
import os
import json
from typing import List, Dict, Any, Optional
from loguru import logger
from config.groq_key_manager import get_key_manager


class GroqAgent:
    """Base class for Groq-powered agents with intelligent key rotation"""

    def __init__(
        self,
        name: str,
        role: str,
        instructions: List[str],
        model: str = "llama-3.3-70b-versatile",
        temperature: float = 0.3,
        max_tokens: int = 3000
    ):
        self.name = name
        self.role = role
        self.instructions = instructions
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.key_manager = get_key_manager()
        self.max_retries = 4  # Try all 4 keys

    def _build_system_prompt(self) -> str:
        """Build system prompt from instructions"""
        prompt = f"You are {self.name}, a {self.role}.\n\nINSTRUCTIONS:\n"
        prompt += "\n".join(self.instructions)
        return prompt

    async def arun(self, user_message: str, context: Optional[str] = None) -> str:
        """Run agent with user message and automatic key rotation"""

        messages = [
            {"role": "system", "content": self._build_system_prompt()}
        ]

        if context:
            messages.append({"role": "system", "content": f"CONTEXT:\n{context}"})

        messages.append({"role": "user", "content": user_message})

        # Try with key rotation
        for attempt in range(self.max_retries):
            try:
                # Get client with current available key
                client = self.key_manager.get_client()

                if client is None:
                    error_response = {
                        "error": "GROQ_KEYS_EXHAUSTED",
                        "message": "All Groq API keys have reached quota or are invalid. Please add new keys or wait for cooldown to expire.",
                        "status": self.key_manager.get_status()
                    }
                    logger.error(f"[{self.name}] All Groq API keys exhausted")
                    raise Exception(json.dumps(error_response))

                current_key = self.key_manager.keys[self.key_manager.current_key_index]

                logger.info(
                    f"[{self.name}] Processing request with {self.model} (KEY_{self.key_manager.current_key_index + 1})"
                )

                response = client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )

                content = response.choices[0].message.content
                logger.info(f"[{self.name}] Response generated successfully")

                return content

            except Exception as e:
                logger.error(f"[{self.name}] Error on attempt {attempt + 1}: {str(e)}")

                # Identify current key
                current_key = self.key_manager.keys[self.key_manager.current_key_index]

                rotated = self.key_manager.handle_error(e, current_key)

                if not rotated:
                    # Try fallback model
                    if self.model == "llama-3.3-70b-versatile":
                        logger.info(f"[{self.name}] Trying fallback model: mixtral-8x7b-32768")
                        self.model = "mixtral-8x7b-32768"
                        continue
                    raise

                if attempt < self.max_retries - 1:
                    logger.info(f"[{self.name}] Retrying with next available key...")
                    continue
                else:
                    raise

        raise Exception(f"[{self.name}] Failed after {self.max_retries} attempts")


# ===========================================================
#                     AGENT DEFINITIONS
# ===========================================================

destination_agent_groq = GroqAgent(
    name="Destination Explorer",
    role="destination research specialist",
    instructions=[
        "Research destinations with focus on user preferences",
        "Provide 8-10 TOP attractions with specific, searchable names",
        "CRITICAL: Use full, official place names (e.g., 'Eiffel Tower Paris', 'Tower Bridge London', 'Taj Mahal Agra')",
        "Format each attraction as: **[Full Place Name]** - Description",
        "Include practical info: hours, fees, visit duration",
        "Avoid generic names like 'Old Town', 'City Center', 'Local Market'",
        "Use proper nouns and specific landmark names",
        "Consider seasonality and current events",
        "Format in clear Markdown with emojis for visual appeal"
    ],
    temperature=0.3
)

flight_agent_groq = GroqAgent(
    name="Flight Search Assistant",
    role="flight search specialist",
    instructions=[
        "Provide 4-5 realistic flight options with variety",
        "Include direct and connecting flights",
        "Provide: airline, flight number, times, duration, stops, estimated price",
        "Include booking URLs (Google Flights or Kayak format)",
        "Format clearly with pricing breakdown"
    ],
    temperature=0.2
)

hotel_agent_groq = GroqAgent(
    name="Hotel Search Assistant",
    role="accommodation specialist",
    instructions=[
        "Provide 4-5 hotels with variety (budget, mid-range, luxury)",
        "Include: name, address, rating, price, key amenities, description",
        "Include booking URLs (Booking.com or Hotels.com format)",
        "Consider location relative to attractions",
        "Format with clear sections"
    ],
    temperature=0.3
)

dining_agent_groq = GroqAgent(
    name="Culinary Guide",
    role="dining specialist",
    instructions=[
        "Provide 4-5 restaurants with variety (budget, mid-range, fine dining)",
        "Include: name, location, cuisine, price range, description, popular dishes",
        "Include website or Google Maps URLs",
        "Highlight local specialties",
        "Format with emojis and clear price indicators ($, $$, $$$)"
    ],
    temperature=0.3
)

budget_agent_groq = GroqAgent(
    name="Budget Optimizer",
    role="travel budget specialist",
    instructions=[
        "Calculate costs by category: transport, accommodation, food, activities",
        "Suggest cost-saving alternatives",
        "Include hidden costs and contingencies",
        "Calculate daily spending estimates",
        "Format with clear tables and totals"
    ],
    temperature=0.2
)

itinerary_agent_groq = GroqAgent(
    name="Itinerary Planner",
    role="day-by-day itinerary specialist",
    instructions=[
        "Create detailed day-by-day itineraries with CLEAR structure:",
        "- Each day must have: Day number, Morning activities, Afternoon activities, Evening activities",
        "- Use format: '## Day X' for each day header",
        "- Under each day, use '**Morning:**', '**Afternoon:**', '**Evening:**' sections",
        "- CRITICAL: Use specific, full place names",
        "- Include specific timing (e.g., 9:00 AM, 2:00 PM)",
        "- Balance activities with rest periods",
        "- Consider travel time between locations",
        "- Add practical tips at the end of each day",
        "- Keep descriptions concise",
        "- Ensure place names match those from destination research"
    ],
    temperature=0.3,
    max_tokens=2000
)

product_agent_groq = GroqAgent(
    name="Travel Essentials Advisor",
    role="travel product recommendation specialist",
    instructions=[
        "Recommend essential travel products based on destination and activities",
        "Consider weather, terrain, and cultural requirements",
        "Suggest 6-8 practical items travelers should bring",
        "Include categories: clothing, gadgets, accessories, health & safety",
        "Provide specific product recommendations",
        "Explain why each product is needed",
        "Include approximate price ranges",
        "Format with product name, category, reason, and estimated price",
        "Output in JSON format for easy parsing"
    ],
    temperature=0.4,
    max_tokens=2500
)


# ===========================================================
#            PRODUCT RECOMMENDATION GENERATOR
# ===========================================================

async def generate_product_recommendations(
    destination: str,
    travel_plan: str,
    activities: str
) -> List[Dict[str, Any]]:
    """
    Generate product recommendations for a trip
    Returns list of products with name, category, reason, price
    """

    prompt = f"""
    Generate 6-8 essential travel product recommendations for this trip:

    Destination: {destination}
    Duration & Budget: {travel_plan[:300]}
    Activities: {activities[:300]}

    For each product, provide:
    - name
    - category
    - reason
    - price_range
    - priority
    - search_term

    Return ONLY valid JSON array.
    """

    response = await product_agent_groq.arun(prompt)

    try:
        start_idx = response.find('[')
        end_idx = response.rfind(']') + 1

        if start_idx != -1 and end_idx > start_idx:
            json_str = response[start_idx:end_idx]
            products = json.loads(json_str)

            # Add Amazon links
            for product in products:
                search_term = product.get("search_term", product.get("name", ""))
                query = search_term.replace(" ", "+")
                product["amazon_url"] = f"https://www.amazon.com/s?k={query}"

            logger.info(f"Generated {len(products)} product recommendations")
            return products

    except Exception as e:
        logger.error(f"Error parsing product recommendations: {e}")

    return []