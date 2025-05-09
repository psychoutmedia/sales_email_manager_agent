from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import Agent, Runner, trace, function_tool, OpenAIChatCompletionsModel
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
import asyncio
import os
import csv
import datetime
from datetime import timezone
import re

# ── Load env and CSV settings ───────────────────────────────────
# load_dotenv reads your .env file and sets environment variables accordingly
load_dotenv(override=True)
USAGE_LOG_FILE = os.getenv("CSV_LOG_FILE", "usage_log.csv")

# ── Check for API keys ───────────────────────────────────────────
for name, var in [("OpenAI", "OPENAI_API_KEY"),
                  ("Google", "GOOGLE_API_KEY"),
                  ("DeepSeek", "DEEPSEEK_API_KEY"),
                  ("Groq", "GROQ_API_KEY")]:
    val = os.getenv(var)
    if val:
        print(f"{name} API Key exists and begins {val[:8]}")
    else:
        print(f"{name} API Key not set{' (optional)' if name in ['Google','DeepSeek','Groq'] else ''}")

# ── Cold-email persona instructions ──────────────────────────────
instructions1 = ("You are a sales agent for ComplAI, writing professional, serious cold emails.")
instructions2 = ("You are a humorous, engaging sales agent for ComplAI, writing witty cold emails.")
instructions3 = ("You are a busy sales agent for ComplAI, writing concise, to-the-point cold emails.")

# ── Configure alternative LLM endpoints ─────────────────────────
GEMINI_BASE_URL   = "https://generativelanguage.googleapis.com/v1beta/openai/"
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
GROQ_BASE_URL     = "https://api.groq.com/openai/v1"

deepseek_client = AsyncOpenAI(base_url=DEEPSEEK_BASE_URL, api_key=os.getenv("DEEPSEEK_API_KEY"))
gemini_client   = AsyncOpenAI(base_url=GEMINI_BASE_URL, api_key=os.getenv("GOOGLE_API_KEY"))
groq_client     = AsyncOpenAI(base_url=GROQ_BASE_URL, api_key=os.getenv("GROQ_API_KEY"))

deepseek_model = OpenAIChatCompletionsModel("deepseek-chat", openai_client=deepseek_client)
gemini_model   = OpenAIChatCompletionsModel("gemini-2.0-flash", openai_client=gemini_client)
llama3_model   = OpenAIChatCompletionsModel("llama-3.3-70b-versatile", openai_client=groq_client)

# ── Instantiate your 12 sales-agent personas ─────────────────────
sales_agent1  = Agent("Professional Sales Agent", instructions1, model="gpt-4o-mini")
sales_agent2  = Agent("Engaging Sales Agent",    instructions2, model="gpt-4o-mini")
sales_agent3  = Agent("Busy Sales Agent",        instructions3, model="gpt-4o-mini")

sales_agent4  = Agent("Professional Sales Agent", instructions1, model=deepseek_model)
sales_agent5  = Agent("Engaging Sales Agent",    instructions2, model=deepseek_model)
sales_agent6  = Agent("Busy Sales Agent",        instructions3, model=deepseek_model)

sales_agent7  = Agent("Professional Sales Agent", instructions1, model=gemini_model)
sales_agent8  = Agent("Engaging Sales Agent",    instructions2, model=gemini_model)
sales_agent9  = Agent("Busy Sales Agent",        instructions3, model=gemini_model)

sales_agent10 = Agent("Professional Sales Agent", instructions1, model=llama3_model)
sales_agent11 = Agent("Engaging Sales Agent",    instructions2, model=llama3_model)
sales_agent12 = Agent("Busy Sales Agent",        instructions3, model=llama3_model)

all_sales_agents = [
    sales_agent1, sales_agent2, sales_agent3,
    sales_agent4, sales_agent5, sales_agent6,
    sales_agent7, sales_agent8, sales_agent9,
    sales_agent10, sales_agent11, sales_agent12,
]

# ── Helper to sanitize tool names ────────────────────────────────
def sanitize(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]", "_", name)

# ── Email-formatter & sender (HTML) pipeline ────────────────────
subject_instructions = (
    "Write a concise, response-provoking subject for the given cold-email body."
)
html_instructions = (
    "Convert the plain-text cold-email body (may contain markdown) into a clean HTML email body."
)

subject_writer = Agent("Email Subject Writer", subject_instructions, model="gpt-4o-mini")
html_converter = Agent("HTML Email Converter", html_instructions, model="gpt-4o-mini")

subject_tool = subject_writer.as_tool("subject_writer", "Generate email subject")
html_tool    = html_converter.as_tool("html_converter", "Convert text to HTML email body")

@function_tool
def send_html_email(subject: str, html_body: str) -> dict:
    sg = sendgrid.SendGridAPIClient(api_key=os.getenv("SENDGRID_API_KEY"))
    mail = Mail(
        from_email=Email("stephensonmark1@gmail.com"),
        to_emails=To("stephensonmark1@gmail.com"),
        subject=subject,
        html_content=Content("text/html", html_body)
    ).get()
    sg.client.mail.send.post(request_body=mail)
    return {"status": "success"}

email_tools = [subject_tool, html_tool, send_html_email]

email_manager = Agent(
    name="Email Manager",
    instructions=(
        "Use subject_writer to craft a subject, then html_converter to make the HTML body, "
        "and finally call send_html_email(subject, html_body)."
    ),
    tools=email_tools,
    model="gpt-4o-mini"
)

# ── Build only the 12 cold-email generator tools ─────────────────
description = "Generate a cold sales email body"
sales_tools = []
for idx, agent in enumerate(all_sales_agents, start=1):
    raw = getattr(agent.model, "model", str(agent.model))
    tag = sanitize(raw)
    tool_name = f"sales_agent{idx}_{tag}"
    sales_tools.append(agent.as_tool(tool_name, description))

# ── Sales Manager with handoff to Email Manager ────────────────
manager_instructions = (
    "You are a sales manager at ComplAI. Invoke each sales_agent tool once to draft cold emails, "
    "select the single best draft, then hand off to the Email Manager agent with that draft."
)
sales_manager = Agent(
    name="Sales Manager",
    instructions=manager_instructions,
    tools=sales_tools,
    handoffs=[email_manager],
    handoff_description="Handoff chosen body to Email Manager",
    model="gpt-4o-mini"
)

# ── Runner + usage logging ──────────────────────────────────────
async def main():
    message = "Send a cold sales email addressed to 'Dear CEO' from Mark Stephenson"
    with trace("Automated SDR"):
        result = await Runner.run(sales_manager, message)

    print("\nFINAL OUTPUT:\n", result.final_output)

    # Extract usage
    raw   = result.raw_responses[-1]
    usage = getattr(raw, "usage", raw)

    def _get(u, *keys, default=0):
        for k in keys:
            if hasattr(u, k): return getattr(u, k)
            if isinstance(u, dict) and k in u: return u[k]
        return default

    p_tokens = _get(usage, "prompt_tokens", "prompt_token_count")
    c_tokens = _get(usage, "completion_tokens", "completion_token_count")
    total    = _get(usage, "total_tokens", "total_token_count", default=p_tokens + c_tokens)
    cost     = _get(usage, "cost_gbp", "total_cost", default=0.0)

    ts    = datetime.datetime.now(timezone.utc).isoformat()
    month = ts[:7]
    model = sales_manager.model

    new = not os.path.exists(USAGE_LOG_FILE)
    with open(USAGE_LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if new:
            writer.writerow(["timestamp","month","model","prompt_tokens","completion_tokens","total_tokens","cost_gbp"])
        writer.writerow([ts, month, model, p_tokens, c_tokens, total, cost])

if __name__ == "__main__":
    asyncio.run(main())
