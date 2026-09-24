# ⚡ RequestFlow AI — Autonomous Intake & Cross-Platform Triage System

An autonomous, privacy-first AI automation system that ingests incoming customer support and request forms from Google Forms, uses a local LLM to classify urgency and category, automatically routes tickets to organized Trello boards, and dispatches real-time alerts to Slack.

---

## 📌 The Business Problem
In small to mid-sized organizations, manual intake of customer support and internal request forms creates operational bottlenecks:
- **Delayed Incident Response**: Critical production bugs or payment failures sit in spreadsheet rows unnoticed for hours.
- **Manual Overhead**: Team members waste valuable time reading, categorizing, and manually copying form submissions into project management tools.
- **Data Privacy Risks**: Forwarding sensitive customer inquiries to third-party cloud LLM APIs introduces compliance and data leakage concerns.

---

## 💡 The Solution
**RequestFlow AI** replaces manual triage with a 100% autonomous, cross-platform pipeline:
1. **Real-Time Ingestion**: Continuously monitors Google Sheets linked to Google Forms for new submissions via `gspread` & Service Account credentials.
2. **Local AI Triage Engine**: Routes submission text through a local LLM (`qwen2.5-coder:7b` via Ollama) to output structured JSON containing Category (`Technical` / `Billing` / `General`), Urgency (`High` / `Medium` / `Low`), and a 1-sentence summary.
3. **Automated Trello Board Routing**: Dynamically creates a new card on a dedicated Trello board in the matching list with color-coded urgency indicators.
4. **Instant Slack Alerts**: Dispatches interactive Slack Block Kit messages featuring urgency badges and a direct link button to the newly created Trello card.
5. **Deduplication & Persistence**: Generates a unique MD5 hash per request stored in SQLite3 to prevent redundant processing.

---

## 🏗️ System Architecture
[ Google Forms ] ──► [ Google Sheets ]
│
▼ (gspread / Service Account)
[ app/main.py ] (Polling Loop)
│
▼
[ app/database.py ] ──► (MD5 Hash Dedup Check)
│
├─── IF Processed ──► Skip
│
└─── IF New Submission
│
▼
[ app/classifier.py ] ◄──► [ Local Ollama LLM ]
│
├── Category: Technical / Billing / General
└── Urgency: High / Medium / Low
│
▼
[ app/trello_handler.py ] ──► Create Card on Trello Board
│
▼
[ app/slack_notifier.py ] ──► Post Interactive Alert to Slack

text


---

## 🛠️ Tech Stack & Tools

| Component | Technology | Description |
|---|---|---|
| **Language** | Python 3.10+ | Core application runtime |
| **Form & Ingestion** | Google Forms & Google Sheets API | Cloud form intake & spreadsheet persistence |
| **Auth & Access** | `gspread` & `google-auth` | Service Account JSON-based authentication |
| **AI / LLM Engine** | Ollama (`qwen2.5-coder:7b`) | Privacy-first local LLM inference |
| **Task Management** | Trello REST API | Automated card creation across dynamic lists |
| **Team Alerts** | Slack Incoming Webhooks | Interactive Block Kit notifications with CTA buttons |
| **Database** | SQLite3 | Local storage for request hash deduplication |
| **Environment** | python-dotenv | Secure secret & API key management |

---

## 🚀 Quick Start & Installation

### Prerequisites
- Python 3.10 or higher
- [Ollama](https://ollama.com/) installed and running locally
- Google Cloud Console Service Account with Sheets & Drive APIs enabled
- Trello Board with API Key & Token
- Slack Channel Webhook URL

### 1. Clone & Setup Virtual Environment

```bash
# Clone the repository
git clone https://github.com/nimasharifiniko/requestflow-ai.git
cd requestflow-ai

# Create and activate virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
2. Pull Local AI Model
Ensure Ollama is running on your machine:

Bash

ollama pull qwen2.5-coder:7b
3. Add Google Service Account Credentials
Place your Google Cloud Service Account JSON file in:

text

credentials/google_service_account.json
(Make sure to Share your Google Sheet with the client_email found in this JSON file as an Editor).

4. Configure Environment Variables
Create a .env file in the root folder:

env

GOOGLE_SHEET_NAME=RequestFlow Intake Form (Responses)
GOOGLE_CREDENTIALS_PATH=credentials/google_service_account.json

TRELLO_API_KEY=your_trello_api_key
TRELLO_TOKEN=your_trello_token
TRELLO_BOARD_NAME=RequestFlow Operations

SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

OLLAMA_BASE_URL=http://localhost:11434/v1
AI_MODEL_NAME=qwen2.5-coder:7b
POLL_INTERVAL_SECONDS=30
5. Run the Autonomous Agent
Bash

python app/main.py
👤 Author
Developed by Nima Sharifi Niko as part of an advanced AI Automation Engineering portfolio.

GitHub: github.com/nimasharifiniko
LinkedIn: linkedin.com/in/nimasharifiniko