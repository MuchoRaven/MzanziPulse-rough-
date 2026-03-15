"""
MzansiPulse Demo Data Seeder
Generates 5 realistic township entrepreneur profiles across the full income spectrum.
Struggling Student → Thriving Designer.

Usage:
    python scripts/seed_demo_data.py
    python scripts/seed_demo_data.py --reset   # Wipe existing demo users first

Password for all accounts: Demo123!
"""

import os
import sys
import random
import argparse
from datetime import datetime, timedelta, time as dtime
from dotenv import load_dotenv

import hashlib
import psycopg2
from psycopg2.extras import RealDictCursor

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────

load_dotenv()
SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL")
DEMO_PASSWORD   = "Demo123!"
DAYS            = 60          # Transaction history window

# Reproducible randomness (change seed to get a different but consistent dataset)
RANDOM_SEED = 42


# ─────────────────────────────────────────────────────────────────────────────
# USER PROFILES
# ─────────────────────────────────────────────────────────────────────────────

USERS = [
    # ── 1. TSHEPO ─────────────────────────────────────────────────────────────
    {
        "key":          "tshepo",
        "first_name":   "Tshepo",
        "last_name":    "Motaung",
        "email":        "tshepo.motaung@gmail.com",
        "phone":        "+27 64 234 5678",
        "id_number":    "0501125678083",
        "dob":          "2005-01-12",
        "gender":       "Male",
        "province":     "Free State",
        "township":     "Tseseng, Phuthaditjhaba",
        "language":     "st",
        "business_name":  "TK Phone Repairs",
        "business_type":  "Mobile Phone Repair",
        "operating_since": "2024-01-01",
        "employee_count":  1,
        "monthly_revenue_range": "R0-R5,000",
        "cipc_registered":  0,
        "cipc_number":      None,
        "tax_number":       None,
        "vat_registered":   0,
        # Balance in cents
        "opening_cash_cents":    13500,   # R135
        "opening_digital_cents":  1500,   # R15
        "target_balance_cents":  32000,   # R320
    },
    # ── 2. PULENG ─────────────────────────────────────────────────────────────
    {
        "key":          "puleng",
        "first_name":   "Puleng",
        "last_name":    "Mofokeng",
        "email":        "puleng.mofokeng@gmail.com",
        "phone":        "+27 71 987 6543",
        "id_number":    "8809235678092",
        "dob":          "1988-09-23",
        "gender":       "Female",
        "province":     "Free State",
        "township":     "Bethlehem",
        "language":     "st",
        "business_name":  "Puleng's Sweet Creations",
        "business_type":  "Bakery",
        "operating_since": "2021-06-01",
        "employee_count":  1,
        "monthly_revenue_range": "R5,001-R15,000",
        "cipc_registered":  0,
        "cipc_number":      None,
        "tax_number":       None,
        "vat_registered":   0,
        "opening_cash_cents":   108000,   # R1,080
        "opening_digital_cents":  72000,  # R720
        "target_balance_cents":  520000,  # R5,200
    },
    # ── 3. NTHABISENG ─────────────────────────────────────────────────────────
    {
        "key":          "nthabiseng",
        "first_name":   "Nthabiseng",
        "last_name":    "Mokoena",
        "email":        "nthabiseng.mokoena@gmail.com",
        "phone":        "+27 73 456 7890",
        "id_number":    "9205145678089",
        "dob":          "1992-05-14",
        "gender":       "Female",
        "province":     "Gauteng",
        "township":     "Soweto",
        "language":     "zu",
        "business_name":  "Nthabi's Hair Lounge",
        "business_type":  "Hair Salon",
        "operating_since": "2019-03-01",
        "employee_count":  2,
        "monthly_revenue_range": "R5,001-R15,000",
        "cipc_registered":  0,
        "cipc_number":      None,
        "tax_number":       None,
        "vat_registered":   0,
        "opening_cash_cents":   175000,   # R1,750
        "opening_digital_cents":  75000,  # R750
        "target_balance_cents":  875000,  # R8,750
    },
    # ── 4. THABO ──────────────────────────────────────────────────────────────
    {
        "key":          "thabo",
        "first_name":   "Thabo",
        "last_name":    "Mahlaba",
        "email":        "thabo.mahlaba@gmail.com",
        "phone":        "+27 82 123 4567",
        "id_number":    "0208175432101",
        "dob":          "2002-08-17",
        "gender":       "Male",
        "province":     "Free State",
        "township":     "Mangaung, Bloemfontein",
        "language":     "st",
        "business_name":  "Thabo's Mobile Mechanics",
        "business_type":  "Auto Repair",
        "operating_since": "2022-09-01",
        "employee_count":  2,
        "monthly_revenue_range": "R15,001-R50,000",
        "cipc_registered":  0,
        "cipc_number":      None,
        "tax_number":       None,
        "vat_registered":   0,
        "opening_cash_cents":   425000,   # R4,250
        "opening_digital_cents": 425000,  # R4,250
        "target_balance_cents": 2230000,  # R22,300
    },
    # ── 5. LINDA ──────────────────────────────────────────────────────────────
    {
        "key":          "linda",
        "first_name":   "Linda",
        "last_name":    "Mthembu",
        "email":        "linda.mthembu@gmail.com",
        "phone":        "+27 83 567 8901",
        "id_number":    "8503285678094",
        "dob":          "1985-03-28",
        "gender":       "Female",
        "province":     "KwaZulu-Natal",
        "township":     "Umlazi, Durban",
        "language":     "zu",
        "business_name":  "Linda's Heritage Designs",
        "business_type":  "Fashion Design",
        "operating_since": "2016-07-01",
        "employee_count":  4,
        "monthly_revenue_range": "R50,001+",
        "cipc_registered":  1,
        "cipc_number":      "2020/123456/23",
        "tax_number":       "9123456789",
        "vat_registered":   1,
        "opening_cash_cents":  1350000,   # R13,500
        "opening_digital_cents": 3150000, # R31,500
        "target_balance_cents": 7850000,  # R78,500
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# TRANSACTION TEMPLATES
# ─────────────────────────────────────────────────────────────────────────────
# Each template defines:
#   income  - list of income transaction types (description, rand range, category)
#   expenses - list of expense types
#   cash_split  - fraction of income that is CASH (rest is DIGITAL)
#   pattern     - controls day-level generation logic

TEMPLATES = {

    # ── TSHEPO ─ very irregular, tiny amounts ─────────────────────────────────
    "tshepo": {
        "income": [
            {"desc": "Screen replacement - Samsung A{m}",   "lo": 8000,  "hi": 15000, "w": 2, "cat": "PHONE_REPAIR"},
            {"desc": "Battery replacement - iPhone 6",       "lo": 6000,  "hi": 10000, "w": 2, "cat": "PHONE_REPAIR"},
            {"desc": "Phone unlocking - Vodacom",            "lo": 5000,  "hi":  8000, "w": 2, "cat": "PHONE_REPAIR"},
            {"desc": "Software fix / virus removal",         "lo": 3000,  "hi":  5000, "w": 3, "cat": "PHONE_REPAIR"},
            {"desc": "Phone case sale",                      "lo": 2000,  "hi":  6000, "w": 5, "cat": "PHONE_REPAIR"},
            {"desc": "Charger / cable sale",                 "lo": 1500,  "hi":  3500, "w": 4, "cat": "PHONE_REPAIR"},
            {"desc": "Screen protector fitting",             "lo": 3000,  "hi":  5000, "w": 3, "cat": "PHONE_REPAIR"},
        ],
        "expenses": [
            {"desc": "Phone parts from wholesaler",          "lo": 20000, "hi": 40000, "w": 2, "cat": "PHONE_PARTS"},
            {"desc": "Taxi to Phuthaditjhaba for parts",     "lo":  4000, "hi":  8000, "w": 4, "cat": "TRANSPORT"},
            {"desc": "Airtime for customer calls",           "lo":  2000, "hi":  5000, "w": 6, "cat": "COMMUNICATION"},
            {"desc": "Monthly rent contribution",            "lo": 20000, "hi": 20000, "w": 1, "cat": "PERSONAL"},
            {"desc": "Screwdriver set / opening tools",      "lo":  8000, "hi": 25000, "w": 1, "cat": "PHONE_PARTS"},
        ],
        "cash_split": 0.90,
        "pattern": "very_irregular",
        # Target net profit over 60 days (in cents) to guide generation
        "target_net": 32000 - 15000,   # R170
    },

    # ── PULENG ─ weekend peaks, medium volume ─────────────────────────────────
    "puleng": {
        "income": [
            {"desc": "Birthday cake - small ({n})",          "lo": 25000, "hi": 45000, "w": 5, "cat": "BAKING_SERVICES"},
            {"desc": "Birthday cake - large ({n})",          "lo": 50000, "hi": 80000, "w": 3, "cat": "BAKING_SERVICES"},
            {"desc": "Wedding cake order",                   "lo":150000, "hi":350000, "w": 1, "cat": "BAKING_SERVICES"},
            {"desc": "Cupcake order (dozen)",                "lo": 12000, "hi": 18000, "w": 6, "cat": "BAKING_SERVICES"},
            {"desc": "Custom dessert tray",                  "lo": 20000, "hi": 40000, "w": 3, "cat": "BAKING_SERVICES"},
            {"desc": "Cookies batch sale",                   "lo":  8000, "hi": 15000, "w": 4, "cat": "BAKING_SERVICES"},
        ],
        "expenses": [
            {"desc": "Baking supplies (flour, sugar, eggs)", "lo": 60000, "hi": 90000, "w": 2, "cat": "BAKING_SUPPLIES"},
            {"desc": "Decorating supplies - fondant/colour", "lo": 20000, "hi": 35000, "w": 2, "cat": "BAKING_SUPPLIES"},
            {"desc": "Electricity bill - oven usage",        "lo": 30000, "hi": 40000, "w": 1, "cat": "UTILITIES"},
            {"desc": "Cake boxes and packaging",             "lo": 10000, "hi": 20000, "w": 2, "cat": "PACKAGING"},
            {"desc": "Transport - cake deliveries",          "lo": 15000, "hi": 25000, "w": 3, "cat": "TRANSPORT"},
            {"desc": "Instagram boost / marketing",          "lo":  8000, "hi": 15000, "w": 2, "cat": "MARKETING"},
        ],
        "cash_split": 0.60,
        "pattern": "weekend_peaks",
        "target_net": 520000 - 180000,  # R3,400
    },

    # ── NTHABISENG ─ Fri-Sun heavy, weekday moderate ──────────────────────────
    "nthabiseng": {
        "income": [
            {"desc": "Hair braiding - box braids",           "lo": 15000, "hi": 35000, "w": 5, "cat": "HAIR_SERVICES"},
            {"desc": "Hair braiding - knotless braids",      "lo": 25000, "hi": 45000, "w": 4, "cat": "HAIR_SERVICES"},
            {"desc": "Wash, blow dry & style",               "lo":  8000, "hi": 12000, "w": 6, "cat": "HAIR_SERVICES"},
            {"desc": "Deep conditioning treatment",          "lo": 20000, "hi": 40000, "w": 3, "cat": "HAIR_SERVICES"},
            {"desc": "Full weave installation",              "lo": 50000, "hi":120000, "w": 2, "cat": "HAIR_SERVICES"},
            {"desc": "Relaxer / texturiser service",         "lo": 18000, "hi": 28000, "w": 3, "cat": "HAIR_SERVICES"},
            {"desc": "Product sale - hair oils & gels",      "lo":  5000, "hi": 15000, "w": 4, "cat": "HAIR_SERVICES"},
        ],
        "expenses": [
            {"desc": "Hair products restock",                "lo": 40000, "hi": 75000, "w": 2, "cat": "SALON_SUPPLIES"},
            {"desc": "Salon rent - monthly",                 "lo":250000, "hi":250000, "w": 1, "cat": "RENT"},
            {"desc": "Electricity",                          "lo": 25000, "hi": 25000, "w": 1, "cat": "UTILITIES"},
            {"desc": "Water",                                "lo": 10000, "hi": 10000, "w": 1, "cat": "UTILITIES"},
            {"desc": "Flyers & social media marketing",      "lo": 10000, "hi": 20000, "w": 2, "cat": "MARKETING"},
            {"desc": "Transport - supplies pickup",          "lo": 15000, "hi": 25000, "w": 2, "cat": "TRANSPORT"},
        ],
        "cash_split": 0.70,
        "pattern": "salon_pattern",   # Fri-Sun heavy
        "target_net": 875000 - 250000,  # R6,250
    },

    # ── THABO ─ consistent, high-value jobs ───────────────────────────────────
    "thabo": {
        "income": [
            {"desc": "Full service - oil, filters, plugs",   "lo": 40000, "hi": 80000, "w": 5, "cat": "AUTO_REPAIR"},
            {"desc": "Brake pad & disc replacement",         "lo":120000, "hi":250000, "w": 3, "cat": "AUTO_REPAIR"},
            {"desc": "Engine diagnostics",                   "lo": 80000, "hi":150000, "w": 4, "cat": "AUTO_REPAIR"},
            {"desc": "Clutch replacement",                   "lo":350000, "hi":800000, "w": 1, "cat": "AUTO_REPAIR"},
            {"desc": "Gearbox repair",                       "lo":400000, "hi":700000, "w": 1, "cat": "AUTO_REPAIR"},
            {"desc": "Tyre rotation & balance",              "lo": 60000, "hi":120000, "w": 4, "cat": "AUTO_REPAIR"},
            {"desc": "Alternator / starter replacement",     "lo":180000, "hi":350000, "w": 2, "cat": "AUTO_REPAIR"},
            {"desc": "Radiator flush & coolant",             "lo": 55000, "hi": 90000, "w": 3, "cat": "AUTO_REPAIR"},
        ],
        "expenses": [
            {"desc": "Spare parts - filters, pads, oils",    "lo":150000, "hi":250000, "w": 3, "cat": "SPARE_PARTS"},
            {"desc": "Tools & workshop equipment",           "lo": 75000, "hi":150000, "w": 2, "cat": "TOOLS"},
            {"desc": "Fuel for mobile callouts",             "lo": 60000, "hi": 90000, "w": 4, "cat": "FUEL"},
            {"desc": "Facebook & WhatsApp ads",              "lo": 15000, "hi": 30000, "w": 2, "cat": "MARKETING"},
            {"desc": "Workshop rent - backyard",             "lo": 80000, "hi": 80000, "w": 1, "cat": "RENT"},
            {"desc": "Assistant wages",                      "lo":200000, "hi":200000, "w": 1, "cat": "WAGES"},
        ],
        "cash_split": 0.50,
        "pattern": "consistent",
        "target_net": 2230000 - 850000,  # R13,800
    },

    # ── LINDA ─ high-value, very consistent, professional ─────────────────────
    "linda": {
        "income": [
            {"desc": "Wedding attire - bride & groom set",   "lo": 800000, "hi":2500000, "w": 2, "cat": "FASHION_DESIGN"},
            {"desc": "Bridesmaid outfits (set of 6)",        "lo":1200000, "hi":2000000, "w": 2, "cat": "FASHION_DESIGN"},
            {"desc": "Traditional ceremony outfit",          "lo": 350000, "hi": 800000, "w": 5, "cat": "FASHION_DESIGN"},
            {"desc": "Custom design - individual client",    "lo": 250000, "hi": 600000, "w": 6, "cat": "FASHION_DESIGN"},
            {"desc": "Ready-to-wear - Heritage collection",  "lo":  80000, "hi": 250000, "w": 8, "cat": "FASHION_DESIGN"},
            {"desc": "Corporate uniform order",              "lo":1500000, "hi":4500000, "w": 1, "cat": "FASHION_DESIGN"},
            {"desc": "Matric farewell attire set",           "lo": 450000, "hi": 900000, "w": 3, "cat": "FASHION_DESIGN"},
        ],
        "expenses": [
            {"desc": "Fabric & materials - high quality",    "lo":1500000, "hi":2500000, "w": 3, "cat": "FABRIC_MATERIALS"},
            {"desc": "Seamstress wages (3 staff)",           "lo":1800000, "hi":1800000, "w": 1, "cat": "WAGES"},
            {"desc": "Studio rent - Umlazi",                 "lo": 650000, "hi": 650000, "w": 1, "cat": "RENT"},
            {"desc": "Electricity",                          "lo": 120000, "hi": 120000, "w": 1, "cat": "UTILITIES"},
            {"desc": "Instagram, magazine & web marketing",  "lo": 250000, "hi": 400000, "w": 2, "cat": "MARKETING"},
            {"desc": "Fabric supplier - credit payment",     "lo": 500000, "hi": 800000, "w": 2, "cat": "FABRIC_MATERIALS"},
            {"desc": "Transport - deliveries & fabric",      "lo": 150000, "hi": 250000, "w": 3, "cat": "TRANSPORT"},
            {"desc": "Sewing machine maintenance",           "lo":  50000, "hi": 150000, "w": 1, "cat": "EQUIPMENT"},
            {"desc": "Accountant fee",                       "lo": 180000, "hi": 180000, "w": 1, "cat": "PROFESSIONAL_SERVICES"},
            {"desc": "Business insurance",                   "lo":  85000, "hi":  85000, "w": 1, "cat": "PROFESSIONAL_SERVICES"},
        ],
        "cash_split": 0.30,
        "pattern": "consistent",
        "target_net": 7850000 - 4500000,  # R33,500
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def hash_password(pw: str) -> str:
    """SHA-256 — matches auth_api.py verify_password()."""
    return hashlib.sha256(pw.encode()).hexdigest()


def weighted_choice(rng, items: list) -> dict:
    """Pick one item from a list of dicts that have a 'w' weight key."""
    weights = [it["w"] for it in items]
    total   = sum(weights)
    r = rng.random() * total
    cumul = 0
    for it in items:
        cumul += it["w"]
        if r < cumul:
            return it
    return items[-1]


def random_time(rng, hour_start=8, hour_end=20) -> dtime:
    hour   = rng.randint(hour_start, hour_end - 1)
    minute = rng.randint(0, 59)
    second = rng.randint(0, 59)
    return dtime(hour, minute, second)


def rand_amount(rng, lo: int, hi: int) -> int:
    """Return a random amount in cents, rounded to nearest R5 (500 cents)."""
    raw = rng.randint(lo, hi)
    return round(raw / 500) * 500 or lo


def format_desc(template: str, rng) -> str:
    """Fill placeholders like {n} (name initial), {m} (model code)."""
    return (
        template
        .replace("{n}", rng.choice(["A", "B", "C", "S", "N"]))
        .replace("{m}", str(rng.randint(10, 52)))
    )


# ─────────────────────────────────────────────────────────────────────────────
# TRANSACTION GENERATION
# ─────────────────────────────────────────────────────────────────────────────

def _day_weight(day_of_week: int, pattern: str) -> float:
    """
    Return a relative activity multiplier for the given day (0=Mon … 6=Sun).
    """
    if pattern == "very_irregular":
        # Mimics student cash-flow: better mid-week after allowances, dead on weekends
        return [0.4, 0.7, 1.0, 1.0, 0.6, 0.2, 0.1][day_of_week]

    if pattern == "weekend_peaks":
        # Baker: orders baked Friday/Saturday, odd weekday order
        return [0.5, 0.6, 0.7, 0.8, 1.0, 1.5, 0.4][day_of_week]

    if pattern == "salon_pattern":
        # Salon: busy Thu-Sat, very slow Mon-Tue
        return [0.3, 0.4, 0.7, 1.0, 1.3, 1.6, 1.0][day_of_week]

    # consistent / default: slight end-of-week + month-end bump handled separately
    return [0.8, 0.9, 1.0, 1.0, 1.1, 1.2, 0.6][day_of_week]


def _month_end_bonus(date: datetime.date) -> float:
    """Extra weight for the last 5 days of each month (payday effect)."""
    import calendar
    last_day = calendar.monthrange(date.year, date.month)[1]
    if date.day >= last_day - 4:
        return 1.3
    if date.day <= 5:
        return 0.85   # Post-payday lull
    return 1.0


def generate_transactions(rng, tpl: dict, opening_cash: int, opening_digital: int,
                           target_balance: int, days: int = 60) -> list:
    """
    Produce a list of transaction dicts for one business.
    Balances income vs expenses to land close to target_balance.
    """
    pattern    = tpl["pattern"]
    cash_split = tpl["cash_split"]
    incomes    = tpl["income"]
    expenses   = tpl["expenses"]
    target_net = tpl["target_net"]   # cents

    today      = datetime.now().date()
    start_date = today - timedelta(days=days - 1)

    cash_bal    = opening_cash
    digital_bal = opening_digital
    total_income  = 0
    total_expense = 0

    txns = []

    # ── Pre-calculate needed income/expense totals ─────────────────────────────
    # We want:  total_income - total_expense ≈ target_net
    # Strategy: generate a raw set of transactions, then scale income to hit target.
    # We do two passes: first collect events, then scale.

    raw_events = []   # (date, kind, template_item)

    for day_offset in range(days):
        current_date = start_date + timedelta(days=day_offset)
        dow          = current_date.weekday()       # 0=Mon … 6=Sun
        day_w        = _day_weight(dow, pattern) * _month_end_bonus(current_date)

        # ── Determine how many income events today ──────────────────────────
        if pattern == "very_irregular":
            # Some weeks have NO income at all
            week_num   = day_offset // 7
            dead_weeks = {1, 3}   # weeks 1 and 3 (0-indexed) are dead
            if week_num in dead_weeks:
                income_events = 0
            else:
                income_events = rng.choices(
                    [0, 1, 2, 3],
                    weights=[
                        max(0, 1 - day_w),
                        day_w * 1.5,
                        day_w * 0.5,
                        day_w * 0.2,
                    ]
                )[0]
        elif pattern == "weekend_peaks":
            income_events = rng.choices(
                [0, 1, 2, 3, 4],
                weights=[
                    max(0.1, 1 - day_w),
                    day_w,
                    day_w * 0.8,
                    day_w * 0.4,
                    day_w * 0.2,
                ]
            )[0]
        elif pattern == "salon_pattern":
            income_events = rng.choices(
                [0, 1, 2, 3, 4, 5],
                weights=[
                    max(0.05, 0.8 - day_w),
                    day_w * 0.8,
                    day_w,
                    day_w * 0.8,
                    day_w * 0.4,
                    day_w * 0.1,
                ]
            )[0]
        else:   # consistent
            income_events = rng.choices(
                [0, 1, 2, 3, 4],
                weights=[0.05, 0.3, 0.4, 0.2, 0.05]
            )[0]

        for _ in range(income_events):
            raw_events.append((current_date, "income", weighted_choice(rng, incomes)))

        # ── Expense events (less frequent, batch-like) ─────────────────────
        if pattern == "very_irregular":
            # Only buy parts when has money (roughly once a week, random)
            if rng.random() < 0.12 * day_w:
                raw_events.append((current_date, "expense", weighted_choice(rng, expenses)))
            # Small expenses (airtime, transport) more often
            if rng.random() < 0.25:
                raw_events.append((current_date, "expense", weighted_choice(
                    rng,
                    [e for e in expenses if e["lo"] < 10000] or expenses
                )))
        elif pattern in ("consistent",):
            # 1-2 expense events per day, sometimes 0
            n_exp = rng.choices([0, 1, 2], weights=[0.3, 0.5, 0.2])[0]
            for _ in range(n_exp):
                raw_events.append((current_date, "expense", weighted_choice(rng, expenses)))
        else:
            n_exp = rng.choices([0, 1, 2], weights=[0.4, 0.45, 0.15])[0]
            for _ in range(n_exp):
                raw_events.append((current_date, "expense", weighted_choice(rng, expenses)))

    # ── Calculate raw totals ────────────────────────────────────────────────
    raw_income  = sum(rand_amount(rng, e["lo"], e["hi"]) for d, k, e in raw_events if k == "income")
    raw_expense = sum(rand_amount(rng, e["lo"], e["hi"]) for d, k, e in raw_events if k == "expense")
    raw_net     = raw_income - raw_expense

    # ── Scale income so net ≈ target_net ───────────────────────────────────
    # income_scale: multiply every income amount by this factor
    if raw_income > 0:
        income_scale = (target_net + raw_expense) / raw_income
        # Clamp to avoid absurd values; if clamped, final balance will be approximate
        income_scale = max(0.5, min(2.5, income_scale))
    else:
        income_scale = 1.0

    # ── Build final transaction list ────────────────────────────────────────
    # Sort events by date and assign random times
    raw_events.sort(key=lambda x: x[0])

    for current_date, kind, item in raw_events:
        base_amt = rand_amount(rng, item["lo"], item["hi"])

        if kind == "income":
            amt = int(base_amt * income_scale)
            amt = max(item["lo"], amt)   # Never below minimum
            is_cash = rng.random() < cash_split
            txn_type = "CASH_IN" if is_cash else "DIGITAL_IN"
            payment_method = "CASH" if is_cash else "DIGITAL"
        else:
            amt = base_amt
            # Expenses mostly cash for lower-income users, more digital for formal ones
            is_cash_expense = rng.random() < cash_split
            txn_type = "CASH_OUT"
            payment_method = "CASH" if is_cash_expense else "DIGITAL"

        txn_time = random_time(rng)

        bal_before = cash_bal + digital_bal

        if kind == "income":
            if payment_method == "CASH":
                cash_bal    += amt
            else:
                digital_bal += amt
            total_income += amt
        else:
            # Deduct from appropriate pot; if insufficient, pull from other
            if payment_method == "CASH":
                if cash_bal >= amt:
                    cash_bal -= amt
                else:
                    shortfall   = amt - cash_bal
                    cash_bal    = 0
                    digital_bal = max(0, digital_bal - shortfall)
            else:
                if digital_bal >= amt:
                    digital_bal -= amt
                else:
                    shortfall   = amt - digital_bal
                    digital_bal = 0
                    cash_bal    = max(0, cash_bal - shortfall)
            total_expense += amt

        bal_after = cash_bal + digital_bal

        txns.append({
            "date":           current_date,
            "time":           txn_time,
            "transaction_type":  txn_type,
            "payment_method": payment_method,
            "amount_cents":   amt,
            "balance_before_cents": bal_before,
            "balance_after_cents":  bal_after,
            "source_destination":   format_desc(item["desc"], rng),
            "category":       item["cat"],
            "verified":       1 if rng.random() < 0.75 else 0,
        })

    return txns, cash_bal, digital_bal, total_income, total_expense


# ─────────────────────────────────────────────────────────────────────────────
# DATABASE OPERATIONS
# ─────────────────────────────────────────────────────────────────────────────

def insert_user(cur, u: dict) -> int:
    cur.execute("""
        INSERT INTO users (
            first_name, last_name, email, phone_number, password_hash,
            id_number, date_of_birth, gender, province, township,
            preferred_language, kyc_status, is_active,
            consent_data_processing, consent_credit_check, consent_timestamp,
            created_at
        ) VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s,
            %s
        )
        RETURNING user_id
    """, (
        u["first_name"], u["last_name"], u["email"], u["phone"],
        hash_password(DEMO_PASSWORD),
        u["id_number"], u["dob"], u["gender"], u["province"], u["township"],
        u["language"], "VERIFIED", 1,
        1, 1, datetime.now().isoformat(),
        datetime.now(),
    ))
    return cur.fetchone()["user_id"]


def insert_business(cur, user_id: int, u: dict) -> int:
    cur.execute("""
        INSERT INTO businesses (
            user_id, business_name, business_type,
            province, township, operating_since,
            employee_count, monthly_revenue_range,
            cipc_registered, cipc_registration_number,
            tax_number, vat_registered,
            verification_status, created_at
        ) VALUES (
            %s, %s, %s,
            %s, %s, %s,
            %s, %s,
            %s, %s,
            %s, %s,
            %s, %s
        )
        RETURNING business_id
    """, (
        user_id, u["business_name"], u["business_type"],
        u["province"], u["township"], u.get("operating_since"),
        u.get("employee_count", 1), u.get("monthly_revenue_range"),
        u["cipc_registered"], u.get("cipc_number"),
        u.get("tax_number"), u["vat_registered"],
        "VERIFIED" if u["cipc_registered"] else "UNVERIFIED",
        datetime.now(),
    ))
    return cur.fetchone()["business_id"]


def insert_wallet(cur, business_id: int, opening_cash: int,
                  opening_digital: int) -> int:
    total = opening_cash + opening_digital
    cur.execute("""
        INSERT INTO cash_wallets (
            business_id,
            virtual_balance_cents, cash_on_hand_cents, digital_balance_cents,
            wallet_status, created_at
        ) VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING wallet_id
    """, (
        business_id,
        total, opening_cash, opening_digital,
        "ACTIVE", datetime.now().isoformat(),
    ))
    return cur.fetchone()["wallet_id"]


def bulk_insert_transactions(cur, wallet_id: int, txns: list):
    """Insert all transactions for one wallet in one executemany call."""
    rows = []
    for t in txns:
        rows.append((
            wallet_id,
            t["transaction_type"],
            t["amount_cents"],
            t["payment_method"],
            t["source_destination"],
            t["balance_before_cents"],
            t["balance_after_cents"],
            t["category"],
            t["verified"],
            t["date"],
            t["time"],
            datetime.combine(t["date"], t["time"]),
            "MANUAL",
        ))

    cur.executemany("""
        INSERT INTO cash_transactions (
            wallet_id,
            transaction_type, amount_cents, payment_method,
            source_destination,
            balance_before_cents, balance_after_cents,
            category, verified,
            transaction_date, transaction_time, recorded_at,
            entry_method
        ) VALUES (
            %s,
            %s, %s, %s,
            %s,
            %s, %s,
            %s, %s,
            %s, %s, %s,
            %s
        )
    """, rows)


def update_wallet_totals(cur, wallet_id: int, final_cash: int,
                         final_digital: int, total_income: int,
                         total_expense: int, cash_income: int,
                         digital_income: int):
    """Stamp final aggregate figures onto the wallet row."""
    cur.execute("""
        UPDATE cash_wallets SET
            virtual_balance_cents   = %s,
            cash_on_hand_cents      = %s,
            digital_balance_cents   = %s,
            total_cash_sales_cents  = %s,
            total_digital_sales_cents = %s,
            total_expenses_cents    = %s,
            last_updated            = NOW()
        WHERE wallet_id = %s
    """, (
        final_cash + final_digital,
        final_cash,
        final_digital,
        cash_income,
        digital_income,
        total_expense,
        wallet_id,
    ))


def delete_demo_users(cur):
    """Remove existing demo users (and cascade to businesses/wallets/transactions)."""
    emails = [u["email"] for u in USERS]
    cur.execute(
        "SELECT user_id FROM users WHERE email = ANY(%s)", (emails,)
    )
    ids = [r["user_id"] for r in cur.fetchall()]
    if not ids:
        return 0

    # Walk the FK chain manually (no ON DELETE CASCADE assumption)
    cur.execute(
        "SELECT business_id FROM businesses WHERE user_id = ANY(%s)", (ids,)
    )
    biz_ids = [r["business_id"] for r in cur.fetchall()]

    if biz_ids:
        cur.execute(
            "SELECT wallet_id FROM cash_wallets WHERE business_id = ANY(%s)",
            (biz_ids,)
        )
        wallet_ids = [r["wallet_id"] for r in cur.fetchall()]

        if wallet_ids:
            cur.execute(
                "DELETE FROM cash_transactions WHERE wallet_id = ANY(%s)",
                (wallet_ids,)
            )
        cur.execute(
            "DELETE FROM cash_wallets WHERE business_id = ANY(%s)", (biz_ids,)
        )
        cur.execute(
            "DELETE FROM businesses WHERE user_id = ANY(%s)", (ids,)
        )

    cur.execute("DELETE FROM users WHERE user_id = ANY(%s)", (ids,))
    return len(ids)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Seed MzansiPulse demo data")
    parser.add_argument("--reset", action="store_true",
                        help="Delete existing demo users before seeding")
    args = parser.parse_args()

    print("=" * 72)
    print("  MzansiPulse Demo Seeder")
    print("  Full Spectrum: Struggling Student -> Thriving Designer")
    print("=" * 72)

    if not SUPABASE_DB_URL:
        print("\n  ERROR: SUPABASE_DB_URL not set in .env — aborting.")
        sys.exit(1)

    conn = psycopg2.connect(SUPABASE_DB_URL, cursor_factory=RealDictCursor)
    conn.autocommit = False
    cur = conn.cursor()

    # ── Optional reset ──────────────────────────────────────────────────────
    if args.reset:
        n = delete_demo_users(cur)
        conn.commit()
        print(f"\n  Reset: removed {n} existing demo user(s).\n")

    # ── Seed each user ──────────────────────────────────────────────────────
    summary_rows = []

    for idx, u in enumerate(USERS, 1):
        key = u["key"]
        tpl = TEMPLATES[key]

        rng = random.Random(RANDOM_SEED + idx * 1000)   # deterministic per user

        print(f"\n  [{idx}/5]  {u['first_name']} {u['last_name']}")
        print(f"           {u['business_name']}  |  {u['township']}")

        # User + business + wallet
        user_id     = insert_user(cur, u)
        business_id = insert_business(cur, user_id, u)
        wallet_id   = insert_wallet(
            cur, business_id,
            u["opening_cash_cents"],
            u["opening_digital_cents"],
        )
        print(f"           User ID {user_id}  |  Business ID {business_id}  |  Wallet ID {wallet_id}")

        # Generate transactions
        txns, final_cash, final_digital, total_income, total_expense = generate_transactions(
            rng, tpl,
            u["opening_cash_cents"],
            u["opening_digital_cents"],
            u["target_balance_cents"],
            days=DAYS,
        )

        # Split income by payment method for wallet totals
        cash_income    = sum(t["amount_cents"] for t in txns
                             if t["transaction_type"] == "CASH_IN")
        digital_income = sum(t["amount_cents"] for t in txns
                             if t["transaction_type"] == "DIGITAL_IN")

        bulk_insert_transactions(cur, wallet_id, txns)
        update_wallet_totals(
            cur, wallet_id,
            final_cash, final_digital,
            total_income, total_expense,
            cash_income, digital_income,
        )

        conn.commit()

        opening = u["opening_cash_cents"] + u["opening_digital_cents"]
        closing = final_cash + final_digital
        net     = closing - opening

        income_txn_count  = sum(1 for t in txns if t["transaction_type"] in ("CASH_IN", "DIGITAL_IN"))
        expense_txn_count = sum(1 for t in txns if t["transaction_type"] == "CASH_OUT")

        print(f"           {len(txns)} transactions  ({income_txn_count} income  /  {expense_txn_count} expense)")
        print(f"           Opening R{opening/100:,.2f}  ->  Closing R{closing/100:,.2f}  (net {'+' if net>=0 else ''}R{net/100:,.2f})")

        summary_rows.append({
            "name":    f"{u['first_name']} {u['last_name']}",
            "email":   u["email"],
            "closing": closing,
            "txns":    len(txns),
        })

    cur.close()
    conn.close()

    # ── Final summary ───────────────────────────────────────────────────────
    print("\n" + "=" * 72)
    print("  ALL 5 DEMO USERS SEEDED SUCCESSFULLY")
    print("=" * 72)
    print(f"\n  Password for all accounts: {DEMO_PASSWORD}\n")
    for i, row in enumerate(summary_rows, 1):
        print(f"  {i}. {row['email']:<38}  R{row['closing']/100:>10,.2f}  ({row['txns']} txns)")
    print()


if __name__ == "__main__":
    main()
