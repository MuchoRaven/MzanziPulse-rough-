# MzansiPulse — Architecture

## Mission

MzansiPulse is a financial empowerment platform built specifically for **South African youth and women entrepreneurs** in township economies. It provides the tools, identity, and funding access that formal institutions have historically denied them — turning informal hustle into a traceable, investable business.

---

## System Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Vue 3 Frontend                      │
│         (Vite · Tailwind CSS · Pinia · vue-i18n)    │
│                 localhost:5173                       │
└─────────────────────┬───────────────────────────────┘
                      │ HTTP / REST
┌─────────────────────▼───────────────────────────────┐
│              Flask API Backend                       │
│              auth_api.py  +  bizseed_api.py          │
│                 localhost:5000                       │
└──────┬─────────────┬──────────────┬─────────────────┘
       │             │              │
┌──────▼──────┐ ┌────▼──────┐ ┌────▼──────────────────┐
│  Supabase   │ │OpenRouter │ │  Huawei Cloud          │
│ PostgreSQL  │ │    API    │ │  OCR (receipt scan)    │
│  (live DB)  │ │ DeepSeek  │ │  OBS (DB backups)      │
└─────────────┘ │   Qwen    │ └────────────────────────┘
                │  Gemini   │
                └───────────┘
```

---

## Database — Supabase PostgreSQL

All amounts stored in **cents** (integers). Converted to Rands in API responses.

### Tables

**`users`**
- `user_id`, `first_name`, `last_name`, `email`, `phone_number`
- `password_hash` (bcrypt)
- `date_of_birth`, `gender` — used for grant eligibility (youth ≤35, women-owned)
- `is_active`, `last_login`, `created_at`

**`businesses`**
- `business_id`, `user_id` (FK), `business_name`, `business_type`
- `township`, `province`
- `cipc_registered`, `tax_number`, `vat_registered`, `b_bbee_level`
- `employee_count`, `operating_since`, `verification_status`

**`cash_wallets`**
- `wallet_id`, `business_id` (FK)
- `virtual_balance_cents` — total balance
- `cash_on_hand_cents` — physical cash portion
- `total_cash_sales_cents`, `total_digital_sales_cents`, `total_expenses_cents`
- `wallet_status`, `last_updated`

**`cash_transactions`**
- `cash_transaction_id`, `wallet_id` (FK)
- `transaction_type` — `CASH_IN | DIGITAL_IN | CASH_OUT | CREDIT_GIVEN | CREDIT_COLLECTED`
- `amount_cents`, `payment_method` — `CASH | DIGITAL | CREDIT`
- `source_destination` (description), `category`, `transaction_date`, `recorded_at`
- `entry_method` — `MANUAL | OCR | WEB_APP`
- `verified`, `receipt_image_path`, `ocr_raw_text`

---

## Backend — Flask API (`scripts/`)

### Core files

| File | Responsibility |
|---|---|
| `auth_api.py` | Main Flask app. Auth (signup/login), dashboard, transactions, ledger, wallet endpoints, chat |
| `bizseed_api.py` | Biz-Seed blueprint — grant matching, market analysis, investment readiness dashboard |
| `wallet_manager.py` | `WalletManager` class — balance tracking, transaction validation, reconciliation, analytics |
| `business_intelligence.py` | Complex analytics queries — sales trends, category breakdowns, EmpowerScore inputs |
| `empowerscore_calculator.py` | EmpowerScore calculation (consistency, growth, diversity, discipline) |
| `openrouter_helper.py` | AI integration — Biz-Bantu chat, investment insight narratives |
| `huawei_ocr_helper.py` | Receipt OCR — Huawei Cloud primary, Tesseract fallback |
| `compliance_helper.py` | CIPC, SARS, B-BBEE, POPIA status checks |
| `db.py` | Supabase PostgreSQL connection via psycopg2 |

### Key design decisions

- **Cents everywhere** — all money stored as integers in the DB to avoid floating point errors
- **No ORM** — raw psycopg2 with `RealDictCursor` for explicit, readable SQL
- **Blueprint separation** — Biz-Seed has its own Flask blueprint (`bizseed_bp`) registered in `auth_api.py`
- **Graceful degradation** — Huawei OCR falls back to Tesseract; AI features fail cleanly if API key missing

---

## Frontend — Vue 3 (`frontend/vue-project/src/`)

### Pages (views)

| Route | View | Description |
|---|---|---|
| `/` | `Dashboard.vue` | Wallet balance, EmpowerScore, quick actions, transactions, grants |
| `/wallet` | `Wallet.vue` | Full cash wallet — balance, daily summary, analytics, history, reconciliation |
| `/ledger` | `Ledger.vue` | Bank-statement-style ledger with date filters, pagination, export |
| `/biz-bantu` | `BizBantu.vue` | AI business advisor chat |
| `/biz-seed` | `BizSeed.vue` | Investment readiness — 4 pillars + AI analysis |
| `/login` | `Login.vue` | Email + password login |
| `/signup` | `Signup.vue` | Business registration |

### Key components

| Component | Purpose |
|---|---|
| `CashWallet.vue` | Full wallet UI — balance cards, income/expense modals, analytics, reconciliation |
| `TransactionsList.vue` | Transaction feed (10 shown, expand/collapse) |
| `AddTransactionModal.vue` | OCR receipt scan + manual entry |
| `EmpowerScoreCard.vue` | Score display with tier and breakdown |
| `GrantCard.vue` | Single funding opportunity card (live API data) |
| `bizseed/ComplianceTracker.vue` | CIPC / SARS / B-BBEE / POPIA status |
| `bizseed/InvestorVault.vue` | Document readiness for investors |
| `bizseed/GrantMatcher.vue` | Personalised grant & loan matching |
| `bizseed/MarketAccess.vue` | Supply chain analytics, supplier directory, growth opportunities |

### State management

- **Pinia** — `stores/auth.js` holds the authenticated user object (id, businessId, walletId, businessType, etc.)
- **vue-i18n** — 4 languages: English, isiZulu, Sesotho, isiXhosa

---

## AI Layer — OpenRouter

All AI calls route through OpenRouter. No direct API integration with individual providers.

| Model | Used For |
|---|---|
| `deepseek/deepseek-chat-v3.1` | Biz-Bantu chat (English/Zulu) + investment readiness narratives |
| `qwen/qwen3.5-flash-02-23` | Fast intent classification for chat routing |
| `google/gemini-2.0-flash-001` | Biz-Bantu chat in Sesotho and isiXhosa (better African language coverage) |

### Biz-Bantu chat flow
1. User sends message → `POST /api/chat`
2. `openrouter_helper.py` fetches real business data (wallet, analytics, top products)
3. Builds a language-locked system prompt with actual financial figures
4. Routes to DeepSeek (en/zu) or Gemini (st/xh)
5. Returns response + follow-up suggestions

### Investment insights flow
1. Biz-Seed dashboard triggers `GET /api/bizseed/dashboard/<user_id>`
2. Backend computes 4 pillar scores (compliance, vault, funding, market)
3. Fetches live market context (revenue trend, top category, digital %, supply chain score)
4. Passes all data to `get_investment_insights()` → DeepSeek
5. Returns 3-sentence narrative + 3 concrete weekly actions

---

## Biz-Seed — Investment Readiness System

The core differentiator for youth and women entrepreneurs who have never had a financial identity.

### 4 Pillars

| Pillar | Score | What it measures |
|---|---|---|
| **Compliance** | 0–100 | CIPC registration (30pts), SARS tax (30pts), B-BBEE (20pts), POPIA (20pts) |
| **Investor Vault** | 0–100 | Transaction history depth, profitability, consistency |
| **Funding Access** | 0–100 | Revenue existence, profitability, formalisation |
| **Market Access** | 0–100 | Sales regularity, transaction volume, margin, revenue scale |

### Grant Matching

Personalised eligibility checks against 11 verified SA funding programmes (2025/2026):
- **Youth grants** — NYDA (R1k–R200k, age ≤35)
- **Women-focused** — NEF Women Empowerment Fund (R250k–R75M)
- **Township traders** — DSBD Spaza Shop Support Fund (R40k non-repayable)
- **Growth capital** — NEF Imbewu (R250k–R10M), Business Partners (R500k–R50M)
- **Revenue advances** — Yoco Capital (no CIPC required)
- **International** — Tony Elumelu Foundation (USD $5k, Jan 2027 cycle)

Eligibility is rule-based (no AI guessing) using the user's actual age, gender, township status, CIPC/tax registration, and 12-month turnover from transactions.

### Supply Chain Analytics

7 real-time PostgreSQL queries powering `MarketAccess.vue`:
- Revenue trend (this month vs last month)
- Day-of-week performance (best trading day)
- Category breakdown (top revenue streams)
- Transaction quality (cash vs digital split)
- Revenue consistency (standard deviation)
- Trading history length
- Supply chain readiness score (0–100)

Supplier recommendations are filtered strictly by the user's business type — a hair salon only sees salon wholesalers; a bakery only sees flour and ingredient suppliers.

---

## EmpowerScore

Alternative credit scoring for entrepreneurs with no formal credit history.

| Component | Weight | Measures |
|---|---|---|
| Consistency | 30% | How regularly transactions are recorded |
| Growth | 25% | Revenue trend over time |
| Diversity | 25% | Range of product/income categories |
| Discipline | 20% | Business vs personal expense separation |

Score range: **0–100**. Tiers: DEVELOPING → GROWING → ESTABLISHED → PRIME

---

## OCR — Receipt Scanning

1. User photographs a receipt in `AddTransactionModal.vue`
2. Image posted to `POST /api/transactions/ocr`
3. `huawei_ocr_helper.py` attempts Huawei Cloud General Text Recognition
4. Falls back to Tesseract (local) if Huawei credentials missing or request fails
5. SA receipt parser extracts: merchant, total amount, date, line items
6. Pre-fills the transaction form — user confirms and saves

---

## Security

- Passwords hashed with **bcrypt**
- No plain-text credentials stored anywhere
- `SUPABASE_DB_URL` and all API keys held in `scripts/.env` (gitignored)
- POPIA-aligned: users only access their own data (all queries filter by `user_id`)
- Wallet balance cannot go negative — `WalletManager.check_sufficient_balance()` blocks the transaction before any DB write
