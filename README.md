# MzansiPulse

**AI-Powered Financial Platform for South African Township Entrepreneurs**

Huawei Developer Competition 2025/2026

---

## What It Does

MzansiPulse helps informal township business owners track money, access funding, and build a financial identity. Key features:

- **Cash Wallet** — track cash, bank, and mobile money separately with balance validation
- **Transaction Ledger** — full bank-statement-style history with filters and pagination
- **EmpowerScore** — alternative credit score built from transaction patterns, not payslips
- **Biz-Bantu** — AI business advisor (DeepSeek/Qwen via OpenRouter) in English, isiZulu, Sesotho, isiXhosa
- **Biz-Seed** — personalised grant/loan matching + supply chain analytics
- **Receipt OCR** — scan paper receipts using Huawei Cloud OCR or Tesseract fallback

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.10+, Flask, psycopg2 |
| Database | Supabase (PostgreSQL) |
| Frontend | Vue 3, Vite, Tailwind CSS, Pinia, vue-i18n |
| AI / Chat | OpenRouter API — DeepSeek (chat + analysis), Qwen (intent detection), Gemini (African languages) |
| OCR | Huawei Cloud General Text Recognition / Tesseract |
| Storage | Huawei OBS (optional, for DB backups) |
| Auth | Custom bcrypt password hashing |

---

## Project Structure

```
MzansiPulse/
├── scripts/                  # Flask backend (run from here)
│   ├── auth_api.py           # Main Flask app + all API endpoints
│   ├── bizseed_api.py        # Biz-Seed blueprint (grants, market analysis)
│   ├── wallet_manager.py     # Cash wallet logic (balances, reconciliation)
│   ├── business_intelligence.py  # Analytics queries
│   ├── empowerscore_calculator.py
│   ├── openrouter_helper.py  # AI chat (Biz-Bantu + investment insights)
│   ├── huawei_ocr_helper.py  # OCR (Huawei Cloud + Tesseract fallback)
│   ├── compliance_helper.py
│   ├── db.py                 # Supabase DB connection
│   ├── .env                  # Environment variables (never commit this)
│   └── .env.example          # Template for required env vars
├── frontend/vue-project/     # Vue 3 frontend
│   ├── src/
│   │   ├── views/            # Dashboard, Wallet, Ledger, BizBantu, BizSeed
│   │   ├── components/       # Reusable UI components
│   │   ├── stores/auth.js    # Pinia auth store
│   │   ├── router/index.js
│   │   └── locales/          # i18n translations (en, zu, st, xh)
│   └── package.json
└── docs/
    └── ARCHITECTURE.md
```

---

## Prerequisites

- Python 3.10+
- Node.js 18+ and npm
- A [Supabase](https://supabase.com) project with the database tables created
- An [OpenRouter](https://openrouter.ai) API key

---

## Setup

### 1. Clone

```bash
git clone <repo-url>
cd MzansiPulse
```

### 2. Backend environment

Create `scripts/.env` from the example:

```bash
cp scripts/.env.example scripts/.env
```

Fill in all required values:

```env
# Required — Supabase PostgreSQL connection string
SUPABASE_DB_URL=postgresql://postgres:<password>@<host>:5432/postgres

# Required — OpenRouter API key
# Powers Biz-Bantu chat and investment insights via DeepSeek and Qwen models
# Get your key at https://openrouter.ai
# Models used:
#   deepseek/deepseek-chat-v3.1  — main chat + investment analysis
#   qwen/qwen3.5-flash-02-23     — fast intent detection
#   google/gemini-2.0-flash-001  — Sesotho/isiXhosa language support
OPENROUTER_API_KEY=sk-or-...

# Optional — Huawei Cloud OCR (falls back to Tesseract if not set)
HUAWEI_AK=
HUAWEI_SK=
HUAWEI_PROJECT_ID=
HUAWEI_REGION=af-south-1

# Optional — Force local Tesseract OCR instead of Huawei
OCR_PROVIDER=tesseract

# Optional — Huawei OBS backup (set USE_OBS=true to enable)
USE_OBS=false
OBS_ACCESS_KEY=
OBS_SECRET_KEY=
OBS_BUCKET_NAME=mzansipulse-data

# Flask
FLASK_ENV=development
FLASK_DEBUG=True
```

### 3. Install Python dependencies

```bash
cd scripts
pip install flask flask-cors psycopg2-binary python-dotenv requests bcrypt
```

If using Tesseract OCR locally, also install:
```bash
pip install Pillow pytesseract
# and install Tesseract binary: https://github.com/UB-Mannheim/tesseract/wiki
```

### 4. Install frontend dependencies

```bash
cd frontend/vue-project
npm install
```

---

## Running the App

You need two terminals running simultaneously.

**Terminal 1 — Backend (Flask API):**
```bash
cd scripts
python auth_api.py
# Runs on http://localhost:5000
```

**Terminal 2 — Frontend (Vite dev server):**
```bash
cd frontend/vue-project
npm run dev
# Runs on http://localhost:5173
```

Open `http://localhost:5173` in your browser.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/signup` | Register a new business owner |
| POST | `/api/login` | Login (returns user + walletId) |
| GET | `/api/dashboard/<user_id>` | Dashboard data (wallet, analytics, EmpowerScore) |
| GET | `/api/transactions?userId=<id>` | Transaction list |
| POST | `/api/transactions` | Add transaction (existing endpoint) |
| POST | `/api/transactions/ocr` | Scan receipt image |
| GET | `/api/ledger/<user_id>` | Full ledger with filters and pagination |
| GET | `/api/wallet/<user_id>/balance` | Wallet balance breakdown |
| GET/POST | `/api/wallet/<wallet_id>/transactions` | Get or add transactions via WalletManager |
| DELETE | `/api/wallet/transactions/<id>?walletId=<id>` | Delete transaction + reverse balance |
| POST | `/api/wallet/<wallet_id>/reconcile` | Cash reconciliation |
| GET | `/api/wallet/<wallet_id>/analytics` | Analytics (period: 7days/30days/90days/all) |
| GET | `/api/wallet/<wallet_id>/daily-summary` | Today's income/expense/net |
| POST | `/api/chat` | Biz-Bantu AI chat |
| GET | `/api/bizseed/dashboard/<user_id>` | Full Biz-Seed investment readiness |
| GET | `/api/bizseed/grants/matches/<user_id>` | Personalised grant matching |
| GET | `/api/bizseed/market/analysis/<user_id>` | Supply chain analytics |

---

## App Routes

| Path | Page |
|---|---|
| `/` | Dashboard |
| `/wallet` | Cash Wallet |
| `/ledger` | Transaction Ledger |
| `/biz-bantu` | AI Business Advisor |
| `/biz-seed` | Grants & Growth Hub |
| `/login` | Login |
| `/signup` | Sign Up |

---

## Demo Users

Seed accounts are created via `scripts/seed_demo_data.py`. Check that file for usernames/passwords used in development.

---

## Production Build

```bash
cd frontend/vue-project
npm run build
# Output in frontend/vue-project/dist/
```

Serve `dist/` with any static host (Nginx, Vercel, Huawei OBS static hosting).
Point the Flask backend to a production WSGI server (e.g. Gunicorn).

---

## Environment Notes

- All amounts are stored in **cents** (integers) in the database and converted to Rands in the API responses.
- The `SUPABASE_DB_URL` must point to a PostgreSQL instance with the full schema applied. See `docs/ARCHITECTURE.md` for the schema.
- If `OPENROUTER_API_KEY` is missing, AI features (Biz-Bantu chat and investment insights) will return an error but the rest of the app works.
- If Huawei OCR credentials are missing, receipt scanning falls back to local Tesseract automatically.
