"""
AI API Routes - REST endpoints for dashboard and bot integration.
"""

import logging
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)


async def handle_ai_request(method: str, path: str, params: dict = None, body: dict = None, db_client=None):
    """Handle AI-related API requests."""
    
    from services.ai.service import CINEAIService
    
    ai_service = CINEAIService(db_client)
    params = params or {}
    body = body or {}
    
    # Query endpoint
    if method == "POST" and path == "/api/ai/query":
        user_id = body.get("user_id")
        query = body.get("query")
        use_streaming = body.get("streaming", False)
        
        if not user_id or not query:
            return {"error": "Missing user_id or query", "status": 400}
        
        result = await ai_service.answer_query(user_id, query, use_streaming)
        return {**result, "status": 200 if "error" not in result else 400}
    
    # Search enhancement
    elif method == "POST" and path == "/api/ai/search":
        user_id = body.get("user_id")
        query = body.get("query")
        search_results = body.get("results", [])
        
        if not user_id or not query:
            return {"error": "Missing parameters", "status": 400}
        
        result = await ai_service.search_with_ai(user_id, query, search_results)
        return {**result, "status": 200 if "error" not in result else 400}
    
    # User statistics
    elif method == "GET" and path.startswith("/api/ai/stats/"):
        user_id = path.split("/")[-1]
        stats = await ai_service.moderation.get_user_stats(user_id)
        return {**stats, "status": 200}
    
    # Admin report
    elif method == "GET" and path == "/api/ai/admin/report":
        report = await ai_service.get_admin_report()
        return {**report, "status": 200 if "error" not in report else 400}
    
    # Models info
    elif method == "GET" and path == "/api/ai/models":
        from services.ai.models_config import MODELS, RECOMMENDED_MODELS
        
        models_list = [
            {
                "id": name,
                "name": config.name,
                "provider": config.provider.value,
                "context_window": config.context_window,
                "cost_input": config.cost_per_1k_input,
                "cost_output": config.cost_per_1k_output,
            }
            for name, config in MODELS.items()
        ]
        
        return {
            "models": models_list,
            "recommended": RECOMMENDED_MODELS,
            "status": 200
        }
    
    # Usage history
    elif method == "GET" and path.startswith("/api/ai/usage/"):
        user_id = path.split("/")[-1]
        
        try:
            usage = await db_client.cine3600.ai_costs.find(
                {"user_id": user_id}
            ).sort("timestamp", -1).limit(100).to_list(None)
            
            return {
                "usage": [
                    {
                        "model": u["model"],
                        "tokens": u["tokens_used"],
                        "cost": u["cost"],
                        "timestamp": u["timestamp"].isoformat(),
                    }
                    for u in usage
                ],
                "status": 200
            }
        except Exception as e:
            logger.error(f"Error fetching usage: {e}")
            return {"error": str(e), "status": 500}
    
    else:
        return {"error": "Endpoint not found", "status": 404}
