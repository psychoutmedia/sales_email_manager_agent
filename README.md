[![Tests](https://github.com/your-org/sales-email-manager/actions/workflows/tests.yml/badge.svg)](https://github.com/your-org/sales-email-manager/actions/workflows/tests.yml)
[![CodeQL](https://github.com/your-org/sales-email-manager/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/your-org/sales-email-manager/actions/workflows/codeql-analysis.yml)

# Sales Email Manager Agent

A powerful Python tool that leverages OpenAI agents and SendGrid to automate cold email outreach, enforce budget limits, and capture detailed usage analytics for recruiters and development teams.

> **Elevator pitch:** A robust AI-driven sales email manager that crafts, sends, and monitors outreach with built-in budget control and usage analytics.

---

## 🔍 Key Features Demonstrated

* **Modular Agent Framework**: Utilizes multiple GPT-4o-mini personas (Professional, Engaging, Busy) orchestrated by a manager agent to generate optimized email copy.
* **Intelligent Agent Orchestration**: The Sales Manager agent invokes each persona tool, compares their generated emails, and picks the single most suitable message to send out.
* **Automated Sending**: Integrated SendGrid function-tool handles email dispatch, complete with error handling and retry logic.
* **Budget Enforcement**: Reads per-email cost and cumulative spend, automatically skipping sends when a GBP budget cap is reached.
* **Usage Logging**: Logs core ML usage metrics—prompt tokens, completion tokens, total tokens, and cost in GBP—into a CSV (`usage_log.csv`) for auditing and forecasting.
* **Timezone-aware Timestamps**: Employs Python’s `datetime.now(timezone.utc)` to generate precise UTC ISO8601 timestamps.
* **Resilient Data Extraction**: Gracefully handles variations in the usage object structure, ensuring robust token and cost tracking across SDK changes.

---

## 🚀 Getting Started

### Prerequisites

* Python 3.10+
* An OpenAI account with API access
* SendGrid account and verified sender email

### Installation

```bash
# Clone repository
git clone https://github.com/your-org/sales-email-manager.git
cd sales-email-manager

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\\Scripts\\activate  # Windows

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
```

---

## 🏃‍♂️ Usage

Run the agent manager to craft and send a cold email:

```bash
python sales_email_manager_agent.py
```

* **Script**: `sales_email_manager_agent.py`
* **Output**: Final email content printed to console and usage metrics appended to `usage_log.csv`.

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

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
