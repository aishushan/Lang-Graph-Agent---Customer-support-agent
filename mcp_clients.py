
from typing import Dict, Any, List
import random

# ----------------------------
# COMMON MCP Server (internal)
# ----------------------------
class CommonMCPServer:
    def parse_request_text(self, text: str) -> Dict[str, Any]:
        try:
            return {
                "structured_text": text,
                "key_phrases": text.split()[:6],
                "sentiment": "negative" if any(w in text.lower() for w in ["down", "fail", "error", "urgent"]) else "neutral"
            }
        except Exception as e:
            print(f"❌ Error in parse_request_text: {e}")
            return {"error": str(e)}

    def normalize_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            normalized = data.copy()
            return normalized
        except Exception as e:
            print(f"❌ Error in normalize_fields: {e}")
            return {"error": str(e)}

    def add_flags_calculations(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            flags = {}
            if data.get("priority") in ["high", "critical"]:
                flags["sla_risk"] = True
            return flags
        except Exception as e:
            print(f"❌ Error in add_flags_calculations: {e}")
            return {"error": str(e)}

    def solution_evaluation(self, solutions: List[Dict[str, Any]]) -> int:
        try:
            best_conf = max(s.get("confidence", 0.5) for s in solutions)
            score = int(best_conf * 100)
            score = min(100, max(0, score + random.randint(-5, 5)))
            return score
        except Exception as e:
            print(f"❌ Error in solution_evaluation: {e}")
            return 60

    def response_generation(self, context: Dict[str, Any]) -> str:
        try:
            return f"Dear {context.get('customer_name', 'Customer')},\n\nWe have addressed your query: {context.get('query', 'your issue')}.\n\nBest regards,\nSupport Team"
        except Exception as e:
            print(f"❌ Error in response_generation: {e}")
            return "Error generating response"

    def execute(self, ability: str, payload: Dict[str, Any]):
        try:
            if ability == "parse_request_text":
                return self.parse_request_text(payload.get("text", ""))
            if ability == "normalize_fields":
                return self.normalize_fields(payload.get("data", {}))
            if ability == "add_flags_calculations":
                return self.add_flags_calculations(payload.get("data", {}))
            if ability == "solution_evaluation":
                return self.solution_evaluation(payload.get("solutions", []))
            if ability == "response_generation":
                return self.response_generation(payload.get("context", {}))
            return {"result": "common_mocked_result"}
        except Exception as e:
            print(f"❌ Error in COMMON execute: {e}")
            return {"error": str(e)}

# ----------------------------
# ATLAS MCP Server (external)
# ----------------------------
class AtlasMCPServer:
    def extract_entities(self, text: str) -> Dict[str, Any]:
        try:
            entities = {"products": [], "accounts": [], "dates": []}
            words = text.lower().split()
            if "account" in words:
                entities["accounts"].append("customer_account")
            if "product" in words or "login" in words or "password" in words:
                entities["products"].append("main_product")
            if "yesterday" in words or "today" in words:
                entities["dates"].append("recent_date")
            return entities
        except Exception as e:
            print(f"❌ Error in extract_entities: {e}")
            return {"error": str(e)}

    def enrich_records(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            enriched = data.copy()
            enriched["sla_days"] = 3
            enriched["historical_tickets"] = 2
            return enriched
        except Exception as e:
            print(f"❌ Error in enrich_records: {e}")
            return {"error": str(e)}

    def clarify_question(self, missing_info: str) -> str:
        try:
            return f"Can you please provide more details about: {missing_info}?"
        except Exception as e:
            print(f"❌ Error in clarify_question: {e}")
            return "Error requesting clarification"

    def extract_answer(self, ticket_id: str) -> str:
        try:
            return "Customer provided additional details about the issue."
        except Exception as e:
            print(f"❌ Error in extract_answer: {e}")
            return "Error extracting answer"

    def knowledge_base_search(self, query: str) -> List[Dict[str, Any]]:
        try:
            lower_q = query.lower()
            results = []
            if "password" in lower_q or "login" in lower_q:
                results.append({"title": "How to reset password", "url": "https://example.com/kb/123", "relevance": 0.95})
            if "down" in lower_q or "production" in lower_q:
                results.append({"title": "Production outage runbook", "url": "https://example.com/kb/999", "relevance": 0.9})
            if not results:
                results.append({"title": "Generic troubleshooting", "url": "https://example.com/kb/000", "relevance": 0.6})
            return results
        except Exception as e:
            print(f"❌ Error in knowledge_base_search: {e}")
            return []

    def escalation_decision(self, score: int) -> bool:
        try:
            return score < 90
        except Exception as e:
            print(f"❌ Error in escalation_decision: {e}")
            return True

    def update_ticket(self, ticket_id: str, updates: Dict[str, Any]) -> bool:
        try:
            print(f"[ATLAS] Updating ticket {ticket_id} with {updates}")
            return True
        except Exception as e:
            print(f"❌ Error in update_ticket: {e}")
            return False

    def close_ticket(self, ticket_id: str) -> bool:
        try:
            print(f"[ATLAS] Closing ticket {ticket_id}")
            return True
        except Exception as e:
            print(f"❌ Error in close_ticket: {e}")
            return False

    def execute_api_calls(self, actions: List[Dict[str, Any]]) -> bool:
        try:
            for a in actions:
                print(f"[ATLAS] Executing API call: {a}")
            return True
        except Exception as e:
            print(f"❌ Error in execute_api_calls: {e}")
            return False

    def trigger_notifications(self, recipient: str, message: str) -> bool:
        try:
            print(f"[ATLAS] Sending notification to {recipient}: {message}")
            return True
        except Exception as e:
            print(f"❌ Error in trigger_notifications: {e}")
            return False

    def execute(self, ability: str, payload: Dict[str, Any]):
        try:
            if ability == "extract_entities":
                return self.extract_entities(payload.get("text", ""))
            if ability == "enrich_records":
                return self.enrich_records(payload.get("data", {}))
            if ability == "clarify_question":
                return self.clarify_question(payload.get("missing_info", ""))
            if ability == "extract_answer":
                return self.extract_answer(payload.get("ticket_id", ""))
            if ability == "knowledge_base_search":
                return self.knowledge_base_search(payload.get("query", ""))
            if ability == "escalation_decision":
                return self.escalation_decision(payload.get("score", 0))
            if ability == "update_ticket":
                return self.update_ticket(payload.get("ticket_id"), payload.get("updates"))
            if ability == "close_ticket":
                return self.close_ticket(payload.get("ticket_id"))
            if ability == "execute_api_calls":
                return self.execute_api_calls(payload.get("actions", []))
            if ability == "trigger_notifications":
                return self.trigger_notifications(payload.get("recipient"), payload.get("message"))
            return {"result": "atlas_mocked_result"}
        except Exception as e:
            print(f"❌ Error in ATLAS execute: {e}")
            return {"error": str(e)}

# ----------------------------
# STATE MCP Server (internal state management)
# ----------------------------
class StateMCPServer:
    def accept_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            return payload
        except Exception as e:
            print(f"❌ Error in accept_payload: {e}")
            return {"error": str(e)}

    def store_answer(self, state: Dict[str, Any], answer: str) -> Dict[str, Any]:
        try:
            state["clarification_answer"] = answer
            return state
        except Exception as e:
            print(f"❌ Error in store_answer: {e}")
            return state

    def store_data(self, state: Dict[str, Any], data: List[Dict[str, Any]]) -> Dict[str, Any]:
        try:
            state["kb_results"] = data
            return state
        except Exception as e:
            print(f"❌ Error in store_data: {e}")
            return state

    def output_payload(self, state: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            state["final_payload"] = payload
            return state
        except Exception as e:
            print(f"❌ Error in output_payload: {e}")
            return state

    def update_payload(self, state: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        try:
            state.update(updates)
            return state
        except Exception as e:
            print(f"❌ Error in update_payload: {e}")
            return state

    def execute(self, ability: str, payload: Dict[str, Any]):
        try:
            if ability == "accept_payload":
                return self.accept_payload(payload.get("payload", {}))
            if ability == "store_answer":
                return self.store_answer(payload.get("state", {}), payload.get("answer", ""))
            if ability == "store_data":
                return self.store_data(payload.get("state", {}), payload.get("data", []))
            if ability == "output_payload":
                return self.output_payload(payload.get("state", {}), payload.get("payload", {}))
            if ability == "update_payload":
                return self.update_payload(payload.get("state", {}), payload.get("updates", {}))
            return {"result": "state_mocked_result"}
        except Exception as e:
            print(f"❌ Error in STATE execute: {e}")
            return {"error": str(e)}

# Instantiate clients for import
common_client = CommonMCPServer()
atlas_client = AtlasMCPServer()
state_client = StateMCPServer()