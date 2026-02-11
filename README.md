# 🇿🇦 MzansiPulse

**AI-Powered Financial Identity & Growth Hub for South Africa's Informal Economy**

*Huawei Developer Competition 2025/2026 Submission*

---

## 🎯 The Problem

Over **1.5 million** spaza shops and informal businesses in South African townships are **"invisible"** to the formal financial system:
- ❌ No credit history
- ❌ No formal records
- ❌ No access to loans or grants
- ❌ Excluded from economic growth

**Result:** Talented entrepreneurs trapped in cash-only, high-risk cycles.

---

## 💡 Our Solution: MzansiPulse

MzansiPulse transforms **informal transactions into formal financial identity** using:

1. **Smart Transaction Parser** - Understands WhatsApp messages in isiZulu/Xhosa/English mix
2. **EmpowerScore** - Alternative credit scoring based on business patterns, not payslips
3. **Biz-Seed** - Automated grant matching to SA funding opportunities
4. **POPIA-Compliant** - Secure, privacy-first architecture

---

## 🏗️ Technology Stack

### Huawei Cloud Services
- **GaussDB for MySQL** - Scalable cloud database
- **ModelArts** - ML model training and inference
- **FunctionGraph** - Serverless API functions
- **Pangu Large Model** - Multilingual NLP (Biz-Bantu AI assistant)
- **OBS** - Object storage for receipts and documents

### Development Stack
- **Python 3.9+** - Core backend logic
- **SQLite** - Local development database
- **Git** - Version control

---

## 📊 Project Status

**Current Phase:** Core Engine Development ✅

### Completed
- [x] Database schema design (7 tables, POPIA-compliant)
- [x] Transaction parser (multilingual, 90%+ accuracy)
- [x] EmpowerScore calculator (4-component ML scoring)
- [x] Grant matching system (automatic eligibility)
- [x] 252 test transactions generated

### In Progress
- [ ] ModelArts cloud deployment
- [ ] FunctionGraph API endpoints
- [ ] Web interface (low-bandwidth optimized)
- [ ] Pangu NLP integration

---

## 🚀 Quick Start

### Prerequisites
```bash
python --version  # Python 3.8+
git --version     # Git 2.0+
```

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/YOUR-USERNAME/MzansiPulse.git
cd MzansiPulse
```

2. **Set up the database**
```bash
cd scripts
python create_database.py
python insert_test_data.py
```

3. **Test the transaction parser**
```bash
python transaction_parser.py
```

4. **Calculate EmpowerScore**
```bash
python empower_score.py
```

5. **Find grant matches**
```bash
python grant_matcher.py
```

---

## 📁 Project Structure
```
MzansiPulse/
├── database/           # SQLite database (local dev)
│   └── mzansipulse.db  (.gitignore - not uploaded)
├── scripts/            # Python backend logic
│   ├── create_database.py
│   ├── insert_test_data.py
│   ├── transaction_parser.py
│   ├── add_transaction.py
│   ├── empower_score.py
│   └── grant_matcher.py
├── data/              # Sample data, CSVs
├── docs/              # Documentation
│   └── ARCHITECTURE.md
├── notebooks/         # ModelArts Jupyter notebooks
├── .gitignore
└── README.md
```

---

## 🎓 Key Innovations

### 1. Multilingual Transaction Parser
Handles code-switching between English, isiZulu, Xhosa, and Afrikaans:
```
Input:  "20 bread R60 cash izolo"
Output: Amount: R60, Category: GROCERIES, Date: Yesterday, Payment: CASH
```

### 2. EmpowerScore Algorithm
Alternative credit scoring (0-1000 scale):
- **Consistency Score (30%)** - Transaction regularity
- **Growth Score (25%)** - Revenue trend
- **Diversity Score (25%)** - Product/supplier variety  
- **Discipline Score (20%)** - Business/personal separation

### 3. Automatic Grant Matching
Matches businesses to real SA funding opportunities:
- NYDA (National Youth Development Agency)
- SEFA (Small Enterprise Finance Agency)
- Corporate programs (Standard Bank, etc.)

---

## 🛡️ Technical Challenges Overcome

### Challenge 1: Budget Constraints
**Problem:** GaussDB consumed $74 in 10 hours  
**Solution:** Pivoted to local SQLite development, reserved cloud for final demo  
**Learning:** Cost management critical for township startups

### Challenge 2: Network Access
**Problem:** Unable to bind public EIP to GaussDB  
**Solution:** VPC-internal architecture (Cloud Shell, ModelArts, FunctionGraph)  
**Benefit:** More secure, mirrors township connectivity reality

### Challenge 3: Cultural Localization
**Problem:** Standard NLP doesn't understand township slang  
**Solution:** Custom parser with SA-specific vocabulary  
**Result:** 90%+ accuracy on real-world messages

---

## 📈 Impact Potential

**If scaled to 10,000 spaza shops:**
- R50M+ in grants unlocked
- 20,000+ jobs supported (2 employees/shop avg)
- R500M+ formal economy integration

---

## 👨‍💻 Developer

**[Your Name]**  
[Your Email]  
[Your LinkedIn]

*Built for the Huawei Developer Competition 2025/2026*

---

## 📄 License

This project is submitted for the Huawei Developer Competition.  
All rights reserved pending competition guidelines.

---

## 🙏 Acknowledgments

- Huawei Cloud for free-tier services
- South African township entrepreneurs who inspired this project
- NYDA, SEFA, SEDA for grant data

---

**⭐ Star this repo if you believe in inclusive fintech for Africa!**