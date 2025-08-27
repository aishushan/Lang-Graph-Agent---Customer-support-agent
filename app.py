

import gradio as gr
import yaml
import json
from agent import LangGraphCustomerSupportAgent, SupportState, Priority
import io
from contextlib import redirect_stdout

# Function to run the agent
def run_agent(customer_name, email, query, priority, ticket_id):
    input_data = {
        "customer_name": customer_name,
        "email": email,
        "query": query,
        "priority": priority,
        "ticket_id": ticket_id
    }
    try:
        agent = LangGraphCustomerSupportAgent()
        log_stream = io.StringIO()
        with redirect_stdout(log_stream):
            result = agent.run(input_data)
        logs = log_stream.getvalue()
        payload = json.dumps(result.final_payload, indent=2)
        return logs, payload, ""
    except Exception as e:
        print(f"DEBUG: Error running agent: {str(e)}")
        return "", "", f"Error running agent: {str(e)}"

# Function to run demo test cases
def run_demo_cases():
    demo_inputs = [
        {
            "customer_name": "Emma Brown",
            "email": "emma.b@example.com",
            "query": "Our production system is completely down since yesterday and we are losing customers",
            "priority": "critical",
            "ticket_id": "TKT-10005"
        },
        {
            "customer_name": "Alice Smith",
            "email": "alice.smith@example.com",
            "query": "Login issue",
            "priority": "low",
            "ticket_id": "TKT-10006"
        },
        {
            "customer_name": "Bob Johnson",
            "email": "bob.j@example.com",
            "query": "How to reset my password for the main product?",
            "priority": "medium",
            "ticket_id": "TKT-10007"
        }
    ]
    results = []
    for i, input_data in enumerate(demo_inputs, 1):
        try:
            agent = LangGraphCustomerSupportAgent()
            log_stream = io.StringIO()
            with redirect_stdout(log_stream):
                result = agent.run(input_data)
            logs = log_stream.getvalue()
            payload = json.dumps(result.final_payload, indent=2)
            results.extend([logs, payload, ""])
            print(f"DEBUG: Demo Case {i} completed successfully")
        except Exception as e:
            print(f"DEBUG: Error in Demo Case {i}: {str(e)}")
            results.extend(["", "", f"Error in Demo Case {i}: {str(e)}"])
    return results

# Gradio interface
with gr.Blocks(title="Customer Support Agent", theme=gr.themes.Soft(), css=".error-box {background-color: #ffe6e6; border: 2px solid red; padding: 10px;}") as app:
    gr.Markdown("# Customer Support Agent Workflow")
    gr.Markdown("Enter a customer support query to run the Lang Graph agent. View results below or run demo test cases.")

    # Input form
    gr.Markdown("## Submit a Support Query")
    with gr.Row():
        customer_name = gr.Textbox(label="Customer Name", value="John Doe")
        email = gr.Textbox(label="Email", value="john.doe@example.com")
    query = gr.Textbox(label="Query", lines=3, value="How to reset my password for the main product?")
    priority = gr.Dropdown(label="Priority", choices=[e.value for e in Priority], value="medium")
    ticket_id = gr.Textbox(label="Ticket ID", value="TKT-10008")
    submit_button = gr.Button("Run Agent")

    # Output for custom query
    logs_output = gr.Textbox(label="Execution Logs", lines=10, interactive=False)
    payload_output = gr.JSON(label="Final Payload")
    error_output = gr.Textbox(label="Errors", lines=3, interactive=False, elem_classes="error-box")
    submit_button.click(
        fn=run_agent,
        inputs=[customer_name, email, query, priority, ticket_id],
        outputs=[logs_output, payload_output, error_output]
    )

    # Demo test cases
    gr.Markdown("## Run Demo Test Cases")
    demo_button = gr.Button("Run Demo Cases")
    with gr.Group():
        demo_outputs = []
        for i in range(1, 4):
            gr.Markdown(f"### Demo Case {i}")
            logs = gr.Textbox(label=f"Logs (Case {i})", lines=5, interactive=False)
            payload = gr.JSON(label=f"Payload (Case {i})")
            error = gr.Textbox(label=f"Errors (Case {i})", lines=3, interactive=False, elem_classes="error-box")
            demo_outputs.extend([logs, payload, error])
    demo_button.click(fn=run_demo_cases, outputs=demo_outputs)

app.launch()