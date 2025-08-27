
from typing import Dict, Any, Literal, Optional, List
from pydantic import BaseModel, Field
from enum import Enum
import yaml
import json
from langgraph.graph import StateGraph, END
from pydantic import ValidationError

# Import MCP clients
from mcp_clients import common_client, atlas_client, state_client

# ----------------------------
# State schema (Pydantic)
# ----------------------------
class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SupportState(BaseModel):
    # Input fields
    customer_name: str = Field(..., description="Name of the customer")
    email: str = Field(..., description="Email address of the customer")
    query: str = Field(..., description="Customer's support query")
    priority: Priority = Field(..., description="Priority level of the ticket")
    ticket_id: str = Field(..., description="Unique identifier for the ticket")

    # Processed fields
    structured_data: Optional[Dict[str, Any]] = Field(default_factory=dict)
    extracted_entities: Optional[Dict[str, Any]] = Field(default_factory=dict)
    normalized_fields: Optional[Dict[str, Any]] = Field(default_factory=dict)
    enriched_data: Optional[Dict[str, Any]] = Field(default_factory=dict)
    flags: Optional[Dict[str, Any]] = Field(default_factory=dict)
    clarification_answer: Optional[str] = None
    kb_results: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    solution_score: Optional[int] = None
    escalation_required: Optional[bool] = False
    response_draft: Optional[str] = None
    final_payload: Optional[Dict[str, Any]] = Field(default_factory=dict)
    clarification_requests: Optional[List[str]] = Field(default_factory=list)

    # Control fields
    current_stage: str = "INIT"
    completed_stages: List[str] = Field(default_factory=list)
    needs_clarification: bool = False
    is_complete: bool = False

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SupportState':
        return cls(**data)

    def validate_state(self):
        """Validate state integrity."""
        if not self.ticket_id.startswith("TKT-"):
            raise ValidationError(f"Invalid ticket_id format: {self.ticket_id}")
        if self.current_stage not in ["INIT"] + [stage["name"] for stage in yaml.safe_load(open("config.yaml"))["stages"]]:
            raise ValidationError(f"Invalid current_stage: {self.current_stage}")

# ----------------------------
# Langie helper prints & logging
# ----------------------------
def langie(msg: str):
    print(f"🤖 Langie: {msg}")

def ability_log(ability: str, server: str, payload: Dict[str, Any]):
    print(f"  ▶ Executing ability: {ability} via {server} MCP with payload keys: {list(payload.keys())}")

# ----------------------------
# Agent Implementation
# ----------------------------
class LangGraphCustomerSupportAgent:
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self.load_config(config_path) if config_path else self.default_config()
        self.graph = self.build_graph()

    def default_config(self) -> Dict[str, Any]:
        return {
            "version": 1,
            "name": "CustomerSupportAgent",
            "description": "Lang Graph Agent for Customer Support Workflows",
        }

    def load_config(self, config_path: str) -> Dict[str, Any]:
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            # Validate config schema
            required_fields = ["version", "name", "description", "input_schema", "stages"]
            if not all(field in config for field in required_fields):
                raise ValueError(f"Config missing required fields: {required_fields}")
            return config
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            return self.default_config()

    def build_graph(self) -> StateGraph:
        workflow = StateGraph(SupportState)

        workflow.add_node("intake", self.intake_stage)
        workflow.add_node("understand", self.understand_stage)
        workflow.add_node("prepare", self.prepare_stage)
        workflow.add_node("ask", self.ask_stage)
        workflow.add_node("wait", self.wait_stage)
        workflow.add_node("retrieve", self.retrieve_stage)
        workflow.add_node("decide", self.decide_stage)
        workflow.add_node("update", self.update_stage)
        workflow.add_node("create", self.create_stage)
        workflow.add_node("do", self.do_stage)
        workflow.add_node("complete", self.complete_stage)

        workflow.set_entry_point("intake")
        workflow.add_edge("intake", "understand")
        workflow.add_edge("understand", "prepare")
        workflow.add_edge("prepare", "ask")
        workflow.add_edge("ask", "wait")
        workflow.add_edge("wait", "retrieve")
        workflow.add_edge("retrieve", "decide")

        workflow.add_conditional_edges(
            "decide",
            self.should_escalate,
            {
                "escalate": "update",
                "continue": "create"
            }
        )

        workflow.add_edge("update", "create")
        workflow.add_edge("create", "do")
        workflow.add_edge("do", "complete")
        workflow.add_edge("complete", END)

        return workflow.compile()

    def should_escalate(self, state: SupportState) -> Literal["escalate", "continue"]:
        if state.escalation_required:
            return "escalate"
        return "continue"

    # ----------------------------
    # Stage implementations (call abilities via MCP clients)
    # ----------------------------
    def intake_stage(self, state: SupportState) -> Dict[str, Any]:
        langie("🔹 Stage 1: INTAKE - Accepting payload")
        try:
            state.validate_state()
            state_dict = state.model_dump()
            state_dict["current_stage"] = "INTAKE"
            state_dict["completed_stages"] = state_dict.get("completed_stages", []) + ["INTAKE"]
            state_dict["needs_clarification"] = False
            state_dict["is_complete"] = False

            ability_log("accept_payload", "STATE", {"payload": state_dict})
            state_dict = state_client.execute("accept_payload", {"payload": state_dict})
            print(f"✅ Received ticket {state_dict['ticket_id']} from {state_dict['customer_name']}")
            return state_dict
        except Exception as e:
            print(f"❌ Error in INTAKE stage: {e}")
            return state.model_dump()

    def understand_stage(self, state: SupportState) -> Dict[str, Any]:
        langie("🔹 Stage 2: UNDERSTAND - Parsing request and extracting entities")
        try:
            state_dict = state.model_dump()

            ability_log("parse_request_text", "COMMON", {"text": state.query})
            structured = common_client.execute("parse_request_text", {"text": state.query})

            ability_log("extract_entities", "ATLAS", {"text": state.query})
            entities = atlas_client.execute("extract_entities", {"text": state.query})

            state_dict["structured_data"] = structured
            state_dict["extracted_entities"] = entities
            state_dict["current_stage"] = "UNDERSTAND"
            state_dict["completed_stages"] = state_dict.get("completed_stages", []) + ["UNDERSTAND"]

            print(f"✅ Parsed request: {structured}")
            print(f"✅ Extracted entities: {entities}")
            return state_dict
        except Exception as e:
            print(f"❌ Error in UNDERSTAND stage: {e}")
            return state.model_dump()

    def prepare_stage(self, state: SupportState) -> Dict[str, Any]:
        langie("🔹 Stage 3: PREPARE - Normalizing, enriching, and adding flags")
        try:
            state_dict = state.model_dump()
            structured = state_dict.get("structured_data", {})

            ability_log("normalize_fields", "COMMON", {"data": structured})
            normalized = common_client.execute("normalize_fields", {"data": structured})

            ability_log("enrich_records", "ATLAS", {"data": structured})
            enriched = atlas_client.execute("enrich_records", {"data": structured})

            ability_log("add_flags_calculations", "COMMON", {"data": structured, "priority": state.priority.value})
            flags = common_client.execute("add_flags_calculations", {"data": {"priority": state.priority.value}})

            state_dict["normalized_fields"] = normalized
            state_dict["enriched_data"] = enriched
            state_dict["flags"] = flags
            state_dict["current_stage"] = "PREPARE"
            state_dict["completed_stages"] = state_dict.get("completed_stages", []) + ["PREPARE"]

            print(f"✅ Normalized data: {normalized}")
            print(f"✅ Enriched data: {enriched}")
            print(f"✅ Flags: {flags}")
            return state_dict
        except Exception as e:
            print(f"❌ Error in PREPARE stage: {e}")
            return state.model_dump()

    def ask_stage(self, state: SupportState) -> Dict[str, Any]:
        langie("🔹 Stage 4: ASK - Determine if clarification is required")
        try:
            state_dict = state.model_dump()
            entities = state_dict.get("extracted_entities", {})
            # Dynamic heuristic: clarification needed if key entities are missing or query is too short
            needs_clarification = (
                len(state.query.split()) < 5 or
                not entities.get("products") or
                not entities.get("accounts")
            )

            if needs_clarification:
                ability_log("clarify_question", "ATLAS", {"missing_info": "Please provide more details about your issue"})
                clarification = atlas_client.execute("clarify_question", {"missing_info": "Please provide more details about your issue"})
                print(f"❓ Clarification needed: {clarification}")
                state_dict["needs_clarification"] = True
                state_dict.setdefault("clarification_requests", []).append(clarification)
            else:
                print("✅ No clarification needed")
                state_dict["needs_clarification"] = False

            state_dict["current_stage"] = "ASK"
            state_dict["completed_stages"] = state_dict.get("completed_stages", []) + ["ASK"]
            return state_dict
        except Exception as e:
            print(f"❌ Error in ASK stage: {e}")
            return state.model_dump()

    def wait_stage(self, state: SupportState) -> Dict[str, Any]:
        langie("🔹 Stage 5: WAIT - If clarification requested, extract answer")
        try:
            state_dict = state.model_dump()

            if state.needs_clarification:
                ability_log("extract_answer", "ATLAS", {"ticket_id": state.ticket_id})
                answer = atlas_client.execute("extract_answer", {"ticket_id": state.ticket_id})
                ability_log("store_answer", "STATE", {"answer": answer})
                state_dict = state_client.execute("store_answer", {"state": state_dict, "answer": answer})
                print(f"✅ Received answer: {answer}")
                state_dict["needs_clarification"] = False
            else:
                print("✅ No waiting needed")

            state_dict["current_stage"] = "WAIT"
            state_dict["completed_stages"] = state_dict.get("completed_stages", []) + ["WAIT"]
            return state_dict
        except Exception as e:
            print(f"❌ Error in WAIT stage: {e}")
            return state.model_dump()

    def retrieve_stage(self, state: SupportState) -> Dict[str, Any]:
        langie("🔹 Stage 6: RETRIEVE - Searching knowledge base")
        try:
            state_dict = state.model_dump()

            ability_log("knowledge_base_search", "ATLAS", {"query": state.query})
            kb_results = atlas_client.execute("knowledge_base_search", {"query": state.query})

            ability_log("store_data", "STATE", {"data": kb_results})
            state_dict = state_client.execute("store_data", {"state": state_dict, "data": kb_results})

            state_dict["current_stage"] = "RETRIEVE"
            state_dict["completed_stages"] = state_dict.get("completed_stages", []) + ["RETRIEVE"]

            print(f"✅ Retrieved {len(kb_results)} KB results")
            return state_dict
        except Exception as e:
            print(f"❌ Error in RETRIEVE stage: {e}")
            return state.model_dump()

    def decide_stage(self, state: SupportState) -> Dict[str, Any]:
        langie("🔹 Stage 7: DECIDE - Evaluating solutions and making decisions")
        try:
            state_dict = state.model_dump()

            potential = [
                {"solution": "Standard troubleshooting", "confidence": 0.7},
                {"solution": "Advanced resolution", "confidence": 0.8}
            ]
            ability_log("solution_evaluation", "COMMON", {"solutions": potential})
            eval_result = common_client.execute("solution_evaluation", {"solutions": potential})

            if isinstance(eval_result, dict) and "score" in eval_result:
                base_score = int(eval_result["score"])
            elif isinstance(eval_result, int):
                base_score = int(eval_result)
            else:
                kbs = state_dict.get("kb_results", [])
                if kbs:
                    base_score = int(max(r.get("relevance", 0.6) * 100 if isinstance(r.get("relevance"), float) else r.get("relevance", 60) for r in kbs))
                else:
                    base_score = 60

            if base_score <= 1:
                base_score = int(base_score * 100)

            priority = state.priority.value
            sentiment = state_dict.get("structured_data", {}).get("sentiment", "neutral")
            kb_relevance = max([r.get("relevance", 0.6) for r in state_dict.get("kb_results", [])], default=0.6)

            # Dynamic scoring adjustment
            base_score += int(kb_relevance * 10)  # Boost score if KB results are highly relevant
            if priority in ["high", "critical"]:
                base_score -= 10
            if sentiment == "negative":
                base_score -= 5

            solution_score = max(0, min(100, int(base_score)))
            ability_log("escalation_decision", "ATLAS", {"score": solution_score})
            escalation_required = atlas_client.execute("escalation_decision", {"score": solution_score})

            ability_log("update_payload", "STATE", {"solution_score": solution_score, "escalation_required": escalation_required})
            state_dict = state_client.execute("update_payload", {
                "state": state_dict,
                "updates": {"solution_score": solution_score, "escalation_required": bool(escalation_required)}
            })

            state_dict["current_stage"] = "DECIDE"
            state_dict["completed_stages"] = state_dict.get("completed_stages", []) + ["DECIDE"]

            print(f"✅ Solution score: {solution_score}")
            print(f"✅ Escalation required: {escalation_required}")
            return state_dict
        except Exception as e:
            print(f"❌ Error in DECIDE stage: {e}")
            return state.model_dump()

    def update_stage(self, state: SupportState) -> Dict[str, Any]:
        langie("🔹 Stage 8: UPDATE - Update or close ticket")
        try:
            state_dict = state.model_dump()

            if state.escalation_required:
                updates = {"status": "escalated", "priority": "high", "assigned_to": "senior_support"}
                ability_log("update_ticket", "ATLAS", {"ticket_id": state.ticket_id, "updates": updates})
                atlas_client.execute("update_ticket", {"ticket_id": state.ticket_id, "updates": updates})
                print("✅ Ticket escalated to senior support")
            else:
                ability_log("close_ticket", "ATLAS", {"ticket_id": state.ticket_id})
                atlas_client.execute("close_ticket", {"ticket_id": state.ticket_id})
                print("✅ Ticket closed")

            state_dict["current_stage"] = "UPDATE"
            state_dict["completed_stages"] = state_dict.get("completed_stages", []) + ["UPDATE"]
            return state_dict
        except Exception as e:
            print(f"❌ Error in UPDATE stage: {e}")
            return state.model_dump()

    def create_stage(self, state: SupportState) -> Dict[str, Any]:
        langie("🔹 Stage 9: CREATE - Generating response")
        try:
            state_dict = state.model_dump()

            ability_log("response_generation", "COMMON", {"context": state_dict})
            response = common_client.execute("response_generation", {"context": state_dict})

            state_dict["response_draft"] = response
            state_dict["current_stage"] = "CREATE"
            state_dict["completed_stages"] = state_dict.get("completed_stages", []) + ["CREATE"]

            print(f"✅ Response draft created: {str(response)[:120]}...")
            return state_dict
        except Exception as e:
            print(f"❌ Error in CREATE stage: {e}")
            return state.model_dump()

    def do_stage(self, state: SupportState) -> Dict[str, Any]:
        langie("🔹 Stage 10: DO - Executing API calls and notifications")
        try:
            state_dict = state.model_dump()

            api_actions = [
                {"action": "log_ticket", "ticket_id": state.ticket_id},
                {"action": "update_crm", "customer": state.customer_name}
            ]
            ability_log("execute_api_calls", "ATLAS", {"actions": api_actions})
            atlas_client.execute("execute_api_calls", {"actions": api_actions})

            if not state.escalation_required:
                message = f"Your ticket {state.ticket_id} has been resolved."
                ability_log("trigger_notifications", "ATLAS", {"recipient": state.email, "message": message})
                atlas_client.execute("trigger_notifications", {"recipient": state.email, "message": message})
                print("✅ Notification sent to customer")

            state_dict["current_stage"] = "DO"
            state_dict["completed_stages"] = state_dict.get("completed_stages", []) + ["DO"]
            return state_dict
        except Exception as e:
            print(f"❌ Error in DO stage: {e}")
            return state.model_dump()

    def complete_stage(self, state: SupportState) -> Dict[str, Any]:
        langie("🔹 Stage 11: COMPLETE - Outputting final payload")
        try:
            state.validate_state()
            final_payload = {
                "ticket_id": state.ticket_id,
                "customer_name": state.customer_name,
                "email": state.email,
                "status": "escalated" if state.escalation_required else "resolved",
                "solution_score": state.solution_score,
                "response": state.response_draft,
                "kb_articles_found": len(state.kb_results),
                "completed_stages": state.completed_stages
            }

            state_dict = state.model_dump()
            ability_log("output_payload", "STATE", {"payload": final_payload})
            state_dict = state_client.execute("output_payload", {"state": state_dict, "payload": final_payload})

            state_dict["current_stage"] = "COMPLETE"
            state_dict["completed_stages"] = state_dict.get("completed_stages", []) + ["COMPLETE"]
            state_dict["is_complete"] = True

            print("✅ Final payload generated")
            print(f"📦 Final Payload: {final_payload}")
            return state_dict
        except Exception as e:
            print(f"❌ Error in COMPLETE stage: {e}")
            return state.model_dump()

    # ----------------------------
    # Run method
    # ----------------------------
    def run(self, input_data: Dict[str, Any]) -> SupportState:
        langie("🚀 Starting Customer Support Agent Workflow")
        print("=" * 60)

        try:
            initial_state = SupportState(**input_data)
            initial_state.validate_state()
            final_state_dict = self.graph.invoke(initial_state)
            final_state = SupportState.from_dict(final_state_dict)
        except Exception as e:
            print(f"❌ Error running workflow: {e}")
            return SupportState(**input_data)

        print("=" * 60)
        langie("🎉 Workflow completed successfully!")
        return final_state

# ----------------------------
# Demo / CLI run
# ----------------------------
if __name__ == "__main__":
    # Example that triggers escalation (critical)
    input_critical = {
        "customer_name": "Emma Brown",
        "email": "emma.b@example.com",
        "query": "Our production system is completely down since yesterday and we are losing customers",
        "priority": "critical",
        "ticket_id": "TKT-10005"
    }

    # Example that triggers clarification (short query)
    input_clarify = {
        "customer_name": "Alice Smith",
        "email": "alice.smith@example.com",
        "query": "Login issue",
        "priority": "low",
        "ticket_id": "TKT-10006"
    }

    # Example that resolves without escalation
    input_resolved = {
        "customer_name": "Bob Johnson",
        "email": "bob.j@example.com",
        "query": "How to reset my password for the main product?",
        "priority": "medium",
        "ticket_id": "TKT-10007"
    }

    agent = LangGraphCustomerSupportAgent()
    print("\n--- Running critical sample ---\n")
    res1 = agent.run(input_critical)

    print("\n--- Running clarification sample ---\n")
    res2 = agent.run(input_clarify)

    print("\n--- Running resolved sample ---\n")
    res3 = agent.run(input_resolved)

    print("\n\n📊 Demo finished. Final payloads:")
    print("\nCritical case:")
    print(json.dumps(res1.final_payload, indent=2))
    print("\nClarification case:")
    print(json.dumps(res2.final_payload, indent=2))
    print("\nResolved case:")
    print(json.dumps(res3.final_payload, indent=2))

