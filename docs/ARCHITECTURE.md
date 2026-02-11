# MzansiPulse Architecture

## System Overview

MzansiPulse uses a **hybrid architecture**:
- **Local Development:** SQLite for speed and cost-efficiency
- **Cloud Deployment:** Huawei Cloud services for scalability

---

## Database Schema

### Core Tables (7)

1. **users** - Shop owners (phone-based identity)
2. **businesses** - Spaza shop profiles
3. **transactions** - Transaction history (the gold mine!)
4. **credit_logs** - EmpowerScore snapshots
5. **grant_opportunities** - Available funding
6. **grant_matches** - Business-to-grant mapping
7. **audit_trail** - POPIA compliance logging

---

## Data Flow
```
WhatsApp Message
    ↓
Transaction Parser (multilingual)
    ↓
SQLite/GaussDB Storage
    ↓
EmpowerScore Calculator
    ↓
Grant Matcher
    ↓
Recommendations to User
```

---

## Security & Compliance

- **POPIA:** Consent tracking, data encryption, audit trails
- **Private VPC:** Database not publicly accessible
- **Offline-first:** Works with intermittent connectivity

---

## Cloud Migration Path

**Development:** SQLite (local, $0)  
**Testing:** GaussDB (2-hour rental, ~$2)  
**Production:** GaussDB + FunctionGraph + ModelArts