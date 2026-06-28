"""
Search Assistant - AI-powered search enhancement and recommendations.
"""

import logging
from typing import List, Dict, Any, Optional

from services.ai.provider_factory import ProviderFactory

logger = logging.getLogger(__name__)


class SearchAssistant:
    """Enhances search with AI recommendations."""
    
    def __init__(self):
        """Initialize search assistant."""
        self.provider = ProviderFactory.get_provider("groq")
    
    async def refine_query(self, user_query: str) -> str:
        """Use AI to refine search query."""
        if not self.provider:
            return user_query
        
        prompt = f"""Refine this movie/TV search query to be more specific:
Query: {user_query}

Return ONLY the refined query, nothing else."""
        
        try:
            response = await self.provider.generate(
                prompt=prompt,
                max_tokens=50,
                temperature=0.3
            )
            return response.content.strip()
        except Exception as e:
            logger.error(f"Query refinement error: {e}")
            return user_query
    
    async def get_recommendations(
        self,
        search_results: List[Dict[str, Any]],
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Get AI recommendations based on search results."""
        if not self.provider or not search_results:
            return search_results
        
        results_text = self._format_results(search_results[:10])
        prefs_text = self._format_preferences(user_preferences) if user_preferences else ""
        
        prompt = f"""Based on these search results{' and user preferences' if user_preferences else ''}:

{results_text}
{prefs_text}

Rank these results by relevance and provide brief reasoning."""
        
        try:
            response = await self.provider.generate(
                prompt=prompt,
                max_tokens=256,
                temperature=0.5
            )
            
            # Parse recommendations and reorder results
            ranked_indices = self._parse_rankings(response.content, len(search_results))
            return [search_results[i] for i in ranked_indices if i < len(search_results)]
        except Exception as e:
            logger.error(f"Recommendation error: {e}")
            return search_results
    
    def _format_results(self, results: List[Dict[str, Any]]) -> str:
        """Format results for AI analysis."""
        lines = []
        for i, r in enumerate(results, 1):
            title = r.get("title", "Unknown")
            year = r.get("year", "")
            score = r.get("rating", 0)
            lines.append(f"{i}. {title} ({year}) - Rating: {score}/10")
        return "\n".join(lines)
    
    def _format_preferences(self, prefs: Dict[str, Any]) -> str:
        """Format user preferences for analysis."""
        lines = ["User Preferences:"]
        if prefs.get("genres"):
            lines.append(f"- Preferred genres: {', '.join(prefs['genres'])}")
        if prefs.get("year_from"):
            lines.append(f"- From {prefs['year_from']} onwards")
        if prefs.get("min_rating"):
            lines.append(f"- Minimum rating: {prefs['min_rating']}")
        return "\n".join(lines)
    
    def _parse_rankings(self, response: str, total: int) -> List[int]:
        """Extract ranking order from AI response."""
        # Simple extraction of numbers from response
        import re
        numbers = re.findall(r'\b([1-9]\d?)\b', response)
        return [int(n) - 1 for n in numbers if int(n) <= total]
