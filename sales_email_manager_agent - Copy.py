from dotenv import load_dotenv
from agents import Agent, Runner, trace, function_tool
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
import asyncio
import os
import csv
import datetime
from datetime import timezone

# ── Load environment & CSV settings ─────────────────────────────
load_dotenv(override=True)
USAGE_LOG_FILE = os.getenv("CSV_LOG_FILE", "usage_log.csv")

# ── Agent personas ───────────────────────────────────────────────
instructions1 = (
    "You are a sales agent working for ComplAI, a company that provides a SaaS "
    "tool for ensuring SOC2 compliance and preparing for audits, powered by AI. "
    "You write professional, serious cold emails."
)
instructions2 = (
    "You are a humorous, engaging sales agent working for ComplAI, a company "
    "that provides a SaaS tool for ensuring SOC2 compliance and preparing for "
    "audits, powered by AI. You write witty, engaging cold emails that are "
    "likely to get a response."
)
instructions3 = (
    "You are a busy sales agent working for ComplAI, a company that provides a "
    "SaaS tool for ensuring SOC2 compliance and preparing for audits, powered "
    "by AI. You write concise, to-the-point cold emails."
)

sales_agent1 = Agent(
    name="Professional Sales Agent", instructions=instructions1, model="gpt-4o-mini"
)
sales_agent2 = Agent(
    name="Engaging Sales Agent", instructions=instructions2, model="gpt-4o-mini"
)
sales_agent3 = Agent(
    name="Busy Sales Agent", instructions=instructions3, model="gpt-4o-mini"
)


# ── SendGrid function-tool (unchanged) ────────────────────────────
@function_tool
def send_email(body: str):
    """Send out an email with the given body to all sales prospects."""
    sg = sendgrid.SendGridAPIClient(api_key=os.environ["SENDGRID_API_KEY"])
    from_email = Email("stephensonmark1@gmail.com")
    to_email = To("stephensonmark1@gmail.com")
    content = Content("text/plain", body)
    mail = Mail(from_email, to_email, "Sales email", content).get()
    sg.client.mail.send.post(request_body=mail)
    return {"status": "success"}


# ── Build tools list via loop ─────────────────────────────────────
description = "Write a cold sales email"
sales_agents = [sales_agent1, sales_agent2, sales_agent3]

tools = [
    *(
        agent.as_tool(f"sales_agent{i}", description)
        for i, agent in enumerate(sales_agents, 1)
    ),
    send_email,
]

# ── Sales-manager agent ───────────────────────────────────────────
manager_instructions = (
    "You are a sales manager at ComplAI. You **never** write emails yourself; "
    "you must use the tools provided. Try each sales_agent tool once, pick the "
    "single best email, then call send_email exactly once with that email."
)

sales_manager = Agent(
    name="Sales Manager",
    instructions=manager_instructions,
    tools=tools,
    model="gpt-4o-mini",
)


# ── Runner + USAGE logging ────────────────────────────────────────
async def main():
    message = "Send a cold sales email addressed to 'Dear CEO'"
    with trace("Sales manager"):
        result = await Runner.run(sales_manager, message)

    print("\nFINAL OUTPUT:\n", result.final_output)

    # — Extract the last LLM response’s usage —
    raw = result.raw_responses[-1]
    usage = getattr(
        raw, "usage", raw
    )  # if raw.usage missing, assume raw is a dict-like

    # Helper to fetch either attr or dict key
    def _get(u, *names, default=0):
        for name in names:
            if hasattr(u, name):
                return getattr(u, name)
            if isinstance(u, dict) and name in u:
                return u[name]
        return default

    prompt_tokens = _get(usage, "prompt_tokens", "prompt_token_count")
    completion_tokens = _get(usage, "completion_tokens", "completion_token_count")
    total_tokens = _get(
        usage,
        "total_tokens",
        "total_token_count",
        default=prompt_tokens + completion_tokens,
    )
    cost_gbp = _get(usage, "cost_gbp", "cost", "total_cost", default=0.0)

    # — Prepare log row —
    timestamp = datetime.datetime.now(timezone.utc).isoformat()
    month = timestamp[:7]  # "YYYY-MM"
    model = sales_manager.model  # "gpt-4o-mini"

    # — Append to CSV (with header if new) —
    file_exists = os.path.isfile(USAGE_LOG_FILE)
    with open(USAGE_LOG_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(
                [
                    "timestamp",
                    "month",
                    "model",
                    "prompt_tokens",
                    "completion_tokens",
                    "total_tokens",
                    "cost_gbp",
                ]
            )
        writer.writerow(
            [
                timestamp,
                month,
                model,
                prompt_tokens,
                completion_tokens,
                total_tokens,
                cost_gbp,
            ]
        )


if __name__ == "__main__":
    asyncio.run(main())
