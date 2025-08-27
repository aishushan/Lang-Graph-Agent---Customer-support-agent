
from typing import TypedDict, Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SupportStateTyped(TypedDict):
    customer_name: str
    email: str
    query: str
    priority: Priority
    ticket_id: str
    structured_data: Optional[Dict[str, Any]]
    extracted_entities: Optional[Dict[str, Any]]
    normalized_fields: Optional[Dict[str, Any]]
    enriched_data: Optional[Dict[str, Any]]
    flags: Optional[Dict[str, Any]]
    clarification_answer: Optional[str]
    kb_results: Optional[List[Dict[str, Any]]]
    solution_score: Optional[int]
    escalation_required: Optional[bool]
    response_draft: Optional[str]
    final_payload: Optional[Dict[str, Any]]
    clarification_requests: Optional[List[str]]
    current_stage: str
    completed_stages: List[str]
    needs_clarification: bool
    is_complete: bool