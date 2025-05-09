[![Tests](https://github.com/psychoutmedia/sales_email_manager_agent/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/psychoutmedia/sales_email_manager_agent/actions/workflows/tests.yml)
[![CodeQL](https://github.com/psychoutmedia/sales_email_manager_agent/actions/workflows/codeql-analysis.yml/badge.svg?branch=main)](https://github.com/psychoutmedia/sales_email_manager_agent/actions/workflows/codeql-analysis.yml)

# Sales Email Manager Agent

A powerful Python tool that leverages OpenAI agents, custom agent tools, and seamless handoff orchestration to automate cold email outreach, enforce budget limits, and capture detailed usage analytics for recruiters and development teams.

> **Elevator pitch:** A robust AI-driven sales email manager that crafts, sends, and monitors outreach with built-in budget control, usage analytics, multi-model support, and pluggable persona tools.

---

## 🔍 Key Features Demonstrated

* **Modular Agent Framework**: Utilizes multiple GPT-4o-mini personas (Professional, Engaging, Busy) orchestrated by a manager agent to generate optimized email copy.
* **Multi-Model LLM Tools**: Side-by-side integration with five backends—including OpenAI GPT-4o-mini, Google Gemini 2.0 Flash, DeepSeek Chat, and Groq Llama‑3.3—so you can compare performance and pick the best responder.
* **Multi-Model Support**: Integrates with **five** LLM backends—OpenAI GPT-4o-mini, Google Gemini 2.0 Flash, DeepSeek Chat, Groq Llama‑3.3‑70b, and more—for side-by-side performance comparisons and best-response selection.
* **Agent Tools Ecosystem**: Three specialized sales agent tools—`ColdEmailPersonaPro`, `ColdEmailPersonaEngage`, and `ColdEmailPersonaBusy`—each optimized for different tones and buyer profiles.
* **Intelligent Tool Orchestration & Handoffs**: The Sales Manager agent automatically invokes each persona tool in sequence, evaluates their outputs, and selects the best-performing email. Once chosen, it hands off to the **Email Manager** agent for formatting, dispatch, and delivery tracking.
* **Automated Sending**: Integrated SendGrid function-tool handles email dispatch, complete with error handling, retry logic, and delivery status callbacks.
* **Budget Enforcement**: Monitors per-email cost against a configurable GBP budget cap; suspends sending when the limit is reached.
* **Usage Logging & Analytics**: Logs core ML usage metrics—prompt tokens, completion tokens, total tokens, and cost in GBP—into a CSV (`usage_log.csv`) for auditing, forecasting, and dashboarding.
* **Timezone-aware Timestamps**: Employs Python’s `datetime.now(timezone.utc)` to generate precise UTC ISO8601 timestamps, ensuring consistent logs across regions.
* **Resilient Data Extraction**: Adapts to any changes in the OpenAI SDK’s usage response format, guaranteeing accurate token and cost tracking even after API updates.

---

## 🆕 What's New in This Release

* **Multi-Model Handoff**: Sales Manager now dynamically distributes prompts across five distinct LLM tools for broad coverage and selects the top-performing response.
* **Custom Agent Tools**: Three pluggable tools (`ColdEmailPersonaPro`, `ColdEmailPersonaEngage`, `ColdEmailPersonaBusy`) specializing in tone and industry messaging.
* **Agent-to-Agent Handoff Architecture**: Streamlined pipeline—Sales Manager → Email Manager—decouples content generation from formatting and dispatch.
* **Enhanced Configuration**: Opt into new LLM endpoints and persona tools via `.env` flags; easily extend with new tools without editing core logic.
* **Extensible Tool Registry**: Auto-discover new agent tools by subclassing `YourToolBaseClass`—no manual main-script updates needed.

---

## 🚀 Getting Started

### Prerequisites

* Python 3.10+
* An OpenAI account with API access
* SendGrid account and verified sender email

### Installation

```bash
# Clone repository
git clone https://github.com/psychoutmedia/sales-email-manager.git
cd sales-email-manager

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\\Scripts\\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Copy the `.env.example` to `.env` and update the following variables:

```ini
SENDGRID_API_KEY=your_sendgrid_api_key
USD_TO_GBP=0.80
MAX_BUDGET_GBP=10.0
CSV_LOG_FILE=usage_log.csv
AGENT_TOOLS=ColdEmailPersonaPro,ColdEmailPersonaEngage,ColdEmailPersonaBusy
HANDOFF_EMAIL_MANAGER=true
```  

---

## 🏃‍♂️ Usage

Run the agent manager to craft and send a cold email:

```bash
python sales_email_manager_agent.py
```

* **Script**: `sales_email_manager_agent.py`
* **Output**: Final email content printed to console, sent via SendGrid, and usage metrics appended to `usage_log.csv`.

---

## 🛠️ Agent Tools & Handoffs

1. **Sales Manager Agent** (`sales_manager`)  
   - Invokes each persona tool listed in `AGENT_TOOLS`, compares generated drafts, and picks the winner.
   - Hands off payload to **Email Manager Agent**.

2. **Email Manager Agent** (`email_manager`)  
   - Formats the selected draft into HTML, populates recipient data, and calls the SendGrid tool.
   - Logs delivery status back to the manager.

3. **Persona Tools**  
   - `ColdEmailPersonaPro`: Formal, consultative tone.  
   - `ColdEmailPersonaEngage`: Conversational, benefit-led tone.  
   - `ColdEmailPersonaBusy`: Short, to-the-point, high-level executive summary.

Adding a new persona tool is as simple as subclassing `YourToolBaseClass` and including it in the `AGENT_TOOLS` list.

---

## 📊 Logs & Metrics

The CSV log (`usage_log.csv`) captures:

| Column              | Description                              |
| ------------------- | ---------------------------------------- |
| `timestamp`         | ISO8601 UTC when the request completed   |
| `month`             | Year-month for easy grouping (`YYYY-MM`) |
| `model`             | Agent model name (e.g., `gpt-4o-mini`)   |
| `prompt_tokens`     | Number of prompt tokens consumed         |
| `completion_tokens` | Number of completion tokens returned     |
| `total_tokens`      | Sum of prompt + completion tokens        |
| `cost_gbp`          | Calculated cost in GBP                   |

Use these metrics for budgeting, forecasting, and performance reviews.

---

## 🛠️ Continuous Integration

Your CI workflows live in the repository under `.github/workflows/`:

* `tests.yml`: Runs your test suite on every push and pull request.  
* `codeql-analysis.yml`: Executes GitHub CodeQL analysis on every push.

To trigger these workflows, simply **push** or **create a pull request** to `main`. You should then see the badges update on your README once the runs complete.

---

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests. If you add a new persona tool or handoff logic, please update this README section.

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
