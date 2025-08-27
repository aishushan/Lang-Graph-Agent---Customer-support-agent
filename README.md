# Lang-Graph-Agent---Customer-support-agent
<img width="1674" height="788" alt="image" src="https://github.com/user-attachments/assets/bc3b4d61-a9d0-481f-8268-76f18a80e2bd" />


A sophisticated customer support workflow automation system built with LangGraph, MCP (Model Context Protocol) servers, and Gradio for interactive demonstration.

🚀 Features
Multi-stage Workflow: 11 distinct stages for comprehensive ticket processing

MCP Integration: Three specialized MCP servers (COMMON, ATLAS, STATE)

Interactive Visualization: PyVis-generated workflow graph with stage modes

Gradio UI: Web interface for testing and demonstration

Smart Decision Making: AI-powered escalation and resolution logic

Knowledge Base Integration: Automated solution retrieval

📋 Workflow Stages
INTAKE - Accept and validate incoming support tickets

UNDERSTAND - Parse requests and extract entities

PREPARE - Normalize, enrich data, and add flags

ASK - Determine if clarification is needed

WAIT - Handle clarification responses

RETRIEVE - Search knowledge base for solutions

DECIDE - Evaluate solutions and make escalation decisions

UPDATE - Update or close tickets based on decisions

CREATE - Generate response drafts

DO - Execute API calls and send notifications

COMPLETE - Output final payload and results

🛠️ Installation
1. Clone the repository:
git clone <your-repo-url>
cd customer-support-agent

2. Install dependencies:
pip install -r requirements.txt

📁 Project Structure
customer-support-agent/
├── agent.py              # Main LangGraph agent implementation
├── mcp_clients.py        # MCP server clients (COMMON, ATLAS, STATE)
├── state_schema.py       # Pydantic models and type definitions
├── config.yaml           # Workflow configuration
├── app.py                # Gradio web interface
├── requirements.txt      # Python dependencies
└── README.md             # This file

🚦 Quick Start
Option 1: Web Interface
python app.py
Then open http://localhost:7860 in your browser.

<img width="1592" height="585" alt="image" src="https://github.com/user-attachments/assets/da123801-f255-41ab-b96b-bb38b38caf19" />


Option 2: Command Line
python agent.py


🔧 Configuration
The config.yaml file defines:

Workflow stages and their execution modes

Ability mappings to MCP servers

Input schema validation rules

🔌 MCP Servers
COMMON Server
Text parsing and normalization
Solution evaluation
Response generation

ATLAS Server
Entity extraction
Knowledge base search
Escalation decisions
API execution

STATE Server
State management
Payload storage and updates
Final output generation

RUN DEMO CASES 
<img width="1763" height="743" alt="image" src="https://github.com/user-attachments/assets/36a822ce-128e-4ed4-abf1-5548604e3da9" />


