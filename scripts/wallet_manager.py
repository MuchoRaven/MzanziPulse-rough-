"""
Cash Wallet Manager for MzansiPulse
Handles balance tracking, transactions, reconciliation, and analytics
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional


class InsufficientBalanceError(Exception):
    """Raised when balance is insufficient for a transaction"""
    pass


class InvalidPaymentMethodError(Exception):
    """Raised when payment method is not recognised"""
    pass


class NegativeAmountError(Exception):
    """Raised when amount is zero or negative"""
    pass


VALID_PAYMENT_METHODS = {'CASH', 'DIGITAL', 'CREDIT'}

# Maps incoming API payment_method values to DB column names
PAYMENT_METHOD_COLUMN = {
    'CASH':    'cash_on_hand_cents',
    'DIGITAL': None,   # derived: virtual_balance - cash_on_hand
    'CREDIT':  None,   # credit transactions never affect wallet balance
}

INCOME_TYPES  = {'CASH_IN', 'DIGITAL_IN', 'CREDIT_COLLECTED'}
EXPENSE_TYPES = {'CASH_OUT', 'CREDIT_GIVEN'}


class WalletManager:
    """Manages wallet operations with multi-payment method support"""

    def __init__(self, db_connection):
        self.conn = db_connection

    # ═══════════════════════════════════════════════════════════════
    # BALANCE
    # ═══════════════════════════════════════════════════════════════

    def get_wallet_balance(self, user_id: int) -> Dict:
        """
        Get complete wallet balance breakdown for a user.
        Returns amounts in Rands (float).
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT
                cw.wallet_id,
                cw.virtual_balance_cents,
                cw.cash_on_hand_cents,
                COALESCE(SUM(CASE WHEN ct.transaction_type = 'CREDIT_GIVEN'
                                  THEN ct.amount_cents ELSE 0 END), 0)       AS credit_given_cents,
                COALESCE(SUM(CASE WHEN ct.transaction_type = 'CREDIT_COLLECTED'
                                  THEN ct.amount_cents ELSE 0 END), 0)       AS credit_collected_cents
            FROM cash_wallets cw
            JOIN businesses b ON cw.business_id = b.business_id
            LEFT JOIN cash_transactions ct ON ct.wallet_id = cw.wallet_id
            WHERE b.user_id = %s
            GROUP BY cw.wallet_id, cw.virtual_balance_cents, cw.cash_on_hand_cents
        ''', (user_id,))
        row = cursor.fetchone()
        if not row:
            return {'error': 'Wallet not found'}

        total     = float(row['virtual_balance_cents'] or 0) / 100
        cash      = float(row['cash_on_hand_cents']    or 0) / 100
        digital   = max(0.0, total - cash)
        cg_cents  = float(row['credit_given_cents']     or 0)
        cc_cents  = float(row['credit_collected_cents'] or 0)
        outstanding_credit = max(0.0, (cg_cents - cc_cents) / 100)

        return {
            'wallet_id':         row['wallet_id'],
            'total_balance':     round(total, 2),
            'cash_on_hand':      round(cash, 2),
            'digital_balance':   round(digital, 2),
            'credit_given':      round(cg_cents / 100, 2),
            'credit_received':   round(cc_cents / 100, 2),
            'outstanding_credit': round(outstanding_credit, 2),
            'available_cash':    round(cash, 2),
            'available_digital': round(digital, 2),
        }

    def check_sufficient_balance(self, wallet_id: int, amount: float,
                                  payment_method: str) -> bool:
        """Return True if the wallet can cover the given expense."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT virtual_balance_cents, cash_on_hand_cents
            FROM cash_wallets WHERE wallet_id = %s
        ''', (wallet_id,))
        row = cursor.fetchone()
        if not row:
            return False

        amount_cents = int(amount * 100)
        if payment_method == 'CASH':
            return int(row['cash_on_hand_cents'] or 0) >= amount_cents
        elif payment_method == 'DIGITAL':
            digital = max(0, int(row['virtual_balance_cents'] or 0) - int(row['cash_on_hand_cents'] or 0))
            return digital >= amount_cents
        # CREDIT transactions are always allowed
        return True

    # ═══════════════════════════════════════════════════════════════
    # TRANSACTIONS
    # ═══════════════════════════════════════════════════════════════

    def add_transaction(self, wallet_id: int, transaction_data: Dict) -> Dict:
        """
        Add a new transaction with balance validation.
        transaction_data keys:
            type            - 'INCOME' or 'EXPENSE'
            amount          - Rands (float)
            payment_method  - 'CASH' | 'DIGITAL' | 'CREDIT'
            description     - str
            category        - str (default 'OTHER')
            date            - 'YYYY-MM-DD' (default today)
            time            - 'HH:MM:SS' (default now)
        """
        amount = float(transaction_data.get('amount', 0))
        if amount <= 0:
            raise NegativeAmountError('Amount must be greater than zero')

        payment_method = (transaction_data.get('payment_method') or 'CASH').upper()
        if payment_method not in VALID_PAYMENT_METHODS:
            raise InvalidPaymentMethodError(f'Invalid payment method: {payment_method}')

        tx_type_raw = (transaction_data.get('type') or '').upper()

        # Map INCOME/EXPENSE to the correct transaction_type
        if tx_type_raw == 'INCOME':
            tx_type = 'CASH_IN' if payment_method == 'CASH' else (
                      'CREDIT_COLLECTED' if payment_method == 'CREDIT' else 'DIGITAL_IN')
        elif tx_type_raw == 'EXPENSE':
            tx_type = 'CREDIT_GIVEN' if payment_method == 'CREDIT' else 'CASH_OUT'
        else:
            # Allow raw transaction_type strings through
            tx_type = tx_type_raw if tx_type_raw in (INCOME_TYPES | EXPENSE_TYPES) else 'CASH_IN'

        is_income  = tx_type in INCOME_TYPES
        is_expense = tx_type in EXPENSE_TYPES

        cursor = self.conn.cursor()

        # Get current balances
        cursor.execute(
            'SELECT virtual_balance_cents, cash_on_hand_cents FROM cash_wallets WHERE wallet_id = %s',
            (wallet_id,)
        )
        wallet = cursor.fetchone()
        if not wallet:
            return {'success': False, 'error': 'Wallet not found'}

        balance_before_cents = int(wallet['virtual_balance_cents'] or 0)
        cash_before_cents    = int(wallet['cash_on_hand_cents']    or 0)
        amount_cents         = int(amount * 100)

        # Validate sufficient balance for expenses
        if is_expense and payment_method != 'CREDIT':
            if not self.check_sufficient_balance(wallet_id, amount, payment_method):
                raise InsufficientBalanceError(
                    f'Insufficient {payment_method.lower()} balance. '
                    f'Available: R{(cash_before_cents if payment_method == "CASH" else max(0, balance_before_cents - cash_before_cents)) / 100:.2f}'
                )

        # Date / time
        tx_date = transaction_data.get('date') or datetime.now().strftime('%Y-%m-%d')
        tx_time = transaction_data.get('time') or datetime.now().strftime('%H:%M:%S')
        recorded_at = f'{tx_date}T{tx_time}'

        # Insert transaction
        cursor.execute('''
            INSERT INTO cash_transactions (
                wallet_id, transaction_type, amount_cents, payment_method,
                source_destination, category, transaction_date,
                entry_method, verified, recorded_at, recorded_method
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING cash_transaction_id
        ''', (
            wallet_id,
            tx_type,
            amount_cents,
            payment_method,
            transaction_data.get('description', ''),
            (transaction_data.get('category') or 'OTHER').upper(),
            tx_date,
            transaction_data.get('entry_method', 'MANUAL'),
            True,
            recorded_at,
            'WEB_APP',
        ))
        transaction_id = cursor.fetchone()['cash_transaction_id']

        # Update wallet balances (CREDIT_GIVEN / CREDIT_COLLECTED don't affect wallet)
        if is_income and tx_type != 'CREDIT_COLLECTED':
            new_virtual = balance_before_cents + amount_cents
            new_cash    = cash_before_cents + (amount_cents if payment_method == 'CASH' else 0)
        elif is_expense and tx_type != 'CREDIT_GIVEN':
            new_virtual = balance_before_cents - amount_cents
            new_cash    = cash_before_cents - (amount_cents if payment_method == 'CASH' else 0)
        else:
            new_virtual = balance_before_cents
            new_cash    = cash_before_cents

        cursor.execute('''
            UPDATE cash_wallets
            SET virtual_balance_cents = %s,
                cash_on_hand_cents    = %s,
                last_updated          = NOW()
            WHERE wallet_id = %s
        ''', (new_virtual, new_cash, wallet_id))

        self.conn.commit()

        balance_after = new_virtual / 100
        return {
            'success':        True,
            'transaction_id': transaction_id,
            'balance_before': round(balance_before_cents / 100, 2),
            'balance_after':  round(balance_after, 2),
            'cash_balance':   round(new_cash / 100, 2),
            'digital_balance': round(max(0, new_virtual - new_cash) / 100, 2),
            'message':        'Transaction added successfully',
        }

    def get_transaction_history(self, wallet_id: int,
                                 filters: Optional[Dict] = None) -> List[Dict]:
        """
        Get filtered transaction history, newest first.
        Amounts returned in Rands.
        """
        filters = filters or {}
        limit   = int(filters.get('limit', 50))

        conditions = ['ct.wallet_id = %s']
        params     = [wallet_id]

        if filters.get('start_date'):
            conditions.append('ct.transaction_date >= %s')
            params.append(filters['start_date'])
        if filters.get('end_date'):
            conditions.append('ct.transaction_date <= %s')
            params.append(filters['end_date'])
        if filters.get('payment_method'):
            conditions.append('ct.payment_method = %s')
            params.append(filters['payment_method'].upper())
        if filters.get('category'):
            conditions.append('ct.category = %s')
            params.append(filters['category'].upper())
        if filters.get('type'):
            raw = filters['type'].upper()
            if raw == 'INCOME':
                conditions.append("ct.transaction_type IN ('CASH_IN','DIGITAL_IN','CREDIT_COLLECTED')")
            elif raw == 'EXPENSE':
                conditions.append("ct.transaction_type IN ('CASH_OUT','CREDIT_GIVEN')")
            else:
                conditions.append('ct.transaction_type = %s')
                params.append(raw)
        if filters.get('min_amount'):
            conditions.append('ct.amount_cents >= %s')
            params.append(int(float(filters['min_amount']) * 100))
        if filters.get('max_amount'):
            conditions.append('ct.amount_cents <= %s')
            params.append(int(float(filters['max_amount']) * 100))

        where = ' AND '.join(conditions)
        cursor = self.conn.cursor()
        cursor.execute(f'''
            SELECT
                ct.cash_transaction_id  AS transaction_id,
                ct.transaction_date     AS date,
                ct.recorded_at,
                ct.transaction_type,
                ct.amount_cents,
                ct.payment_method,
                ct.source_destination   AS description,
                ct.category,
                ct.verified,
                ct.entry_method
            FROM cash_transactions ct
            WHERE {where}
            ORDER BY ct.transaction_date DESC, ct.recorded_at DESC
            LIMIT %s
        ''', params + [limit])

        rows = cursor.fetchall()
        result = []
        for r in rows:
            tx_type = r['transaction_type']
            amount  = float(r['amount_cents'] or 0) / 100

            # Normalise date
            raw_date = r['date']
            date_str = raw_date.isoformat() if hasattr(raw_date, 'isoformat') else str(raw_date)[:10]

            # Normalise recorded_at
            raw_rec = r['recorded_at']
            if raw_rec is None:
                time_str = ''
            elif hasattr(raw_rec, 'strftime'):
                time_str = raw_rec.strftime('%H:%M:%S')
            else:
                parts = str(raw_rec).replace('T', ' ').split(' ')
                time_str = parts[1][:8] if len(parts) > 1 else ''

            result.append({
                'transaction_id': r['transaction_id'],
                'date':           date_str,
                'time':           time_str,
                'type':           'INCOME' if tx_type in INCOME_TYPES else 'EXPENSE',
                'transaction_type': tx_type,
                'amount':         round(amount, 2),
                'payment_method': r['payment_method'],
                'description':    r['description'] or '',
                'category':       r['category'] or 'OTHER',
                'verified':       bool(r['verified']),
                'entry_method':   r['entry_method'] or 'MANUAL',
            })
        return result

    def delete_transaction(self, transaction_id: int, wallet_id: int) -> Dict:
        """Delete a transaction and reverse its effect on wallet balance."""
        cursor = self.conn.cursor()

        cursor.execute('''
            SELECT transaction_type, amount_cents, payment_method
            FROM cash_transactions
            WHERE cash_transaction_id = %s AND wallet_id = %s
        ''', (transaction_id, wallet_id))
        tx = cursor.fetchone()
        if not tx:
            return {'success': False, 'error': 'Transaction not found'}

        tx_type      = tx['transaction_type']
        amount_cents = int(tx['amount_cents'] or 0)
        pay_method   = tx['payment_method']

        # Reverse balance effect
        if tx_type in INCOME_TYPES and tx_type != 'CREDIT_COLLECTED':
            delta_virtual = -amount_cents
            delta_cash    = -amount_cents if pay_method == 'CASH' else 0
        elif tx_type in EXPENSE_TYPES and tx_type != 'CREDIT_GIVEN':
            delta_virtual = +amount_cents
            delta_cash    = +amount_cents if pay_method == 'CASH' else 0
        else:
            delta_virtual = 0
            delta_cash    = 0

        cursor.execute('DELETE FROM cash_transactions WHERE cash_transaction_id = %s', (transaction_id,))
        cursor.execute('''
            UPDATE cash_wallets
            SET virtual_balance_cents = virtual_balance_cents + %s,
                cash_on_hand_cents    = cash_on_hand_cents    + %s,
                last_updated          = NOW()
            WHERE wallet_id = %s
        ''', (delta_virtual, delta_cash, wallet_id))

        self.conn.commit()
        return {'success': True, 'message': 'Transaction deleted and balances updated'}

    # ═══════════════════════════════════════════════════════════════
    # RECONCILIATION
    # ═══════════════════════════════════════════════════════════════

    def reconcile_cash(self, wallet_id: int, actual_cash: float) -> Dict:
        """Compare physical cash count with system records."""
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT cash_on_hand_cents FROM cash_wallets WHERE wallet_id = %s',
            (wallet_id,)
        )
        row = cursor.fetchone()
        if not row:
            return {'error': 'Wallet not found'}

        expected    = float(row['cash_on_hand_cents'] or 0) / 100
        difference  = actual_cash - expected
        diff_pct    = (difference / expected * 100) if expected > 0 else 0.0

        if abs(difference) < 0.01:
            status = 'MATCH'
        elif abs(diff_pct) < 2:
            status = 'MINOR_DISCREPANCY'
        else:
            status = 'MAJOR_DISCREPANCY'

        suggestions = []
        if difference < 0:
            suggestions += [
                'Check for unrecorded cash expenses',
                'Review your last 10 cash transactions for any that were missed',
                'Verify no cash sales were made without being logged',
            ]
            if abs(diff_pct) >= 5:
                suggestions.append('Consider discussing with staff if someone else handles cash')
        elif difference > 0:
            suggestions += [
                'You may have unrecorded income — check if all sales were logged',
                'Verify a loan repayment has not been missed in the records',
            ]

        # Update last reconciliation timestamp
        cursor.execute('''
            UPDATE cash_wallets SET last_updated = NOW() WHERE wallet_id = %s
        ''', (wallet_id,))
        self.conn.commit()

        return {
            'expected_cash':         round(expected, 2),
            'actual_cash':           round(actual_cash, 2),
            'difference':            round(difference, 2),
            'difference_percentage': round(diff_pct, 2),
            'status':                status,
            'suggestions':           suggestions,
        }

    # ═══════════════════════════════════════════════════════════════
    # ANALYTICS
    # ═══════════════════════════════════════════════════════════════

    def get_analytics(self, wallet_id: int, period: str = '30days') -> Dict:
        """Get wallet analytics for a period: '7days','30days','90days','all'."""
        period_map = {
            '7days':  7,
            '30days': 30,
            '90days': 90,
            'all':    None,
        }
        days = period_map.get(period, 30)

        cursor = self.conn.cursor()
        date_condition = ''
        params_base    = [wallet_id]
        if days:
            date_condition = f"AND ct.transaction_date >= CURRENT_DATE - INTERVAL '{days} days'"

        cursor.execute(f'''
            SELECT
                COALESCE(SUM(CASE WHEN ct.transaction_type IN ('CASH_IN','DIGITAL_IN','CREDIT_COLLECTED')
                                  THEN ct.amount_cents ELSE 0 END), 0)                        AS income_cents,
                COALESCE(SUM(CASE WHEN ct.transaction_type IN ('CASH_OUT','CREDIT_GIVEN')
                                  THEN ct.amount_cents ELSE 0 END), 0)                        AS expense_cents,
                COUNT(*)                                                                        AS tx_count,
                COUNT(CASE WHEN ct.transaction_type IN ('CASH_IN','DIGITAL_IN','CREDIT_COLLECTED') THEN 1 END) AS income_count,
                COUNT(CASE WHEN ct.transaction_type IN ('CASH_OUT','CREDIT_GIVEN') THEN 1 END) AS expense_count,
                AVG(ct.amount_cents)                                                            AS avg_tx_cents,
                AVG(CASE WHEN ct.transaction_type IN ('CASH_IN','DIGITAL_IN','CREDIT_COLLECTED')
                          THEN ct.amount_cents END)                                             AS avg_income_cents,
                AVG(CASE WHEN ct.transaction_type IN ('CASH_OUT','CREDIT_GIVEN')
                          THEN ct.amount_cents END)                                             AS avg_expense_cents,
                COUNT(DISTINCT ct.transaction_date)                                             AS active_days,
                COUNT(CASE WHEN ct.payment_method = 'CASH'    THEN 1 END)                     AS cash_count,
                COUNT(CASE WHEN ct.payment_method = 'DIGITAL' THEN 1 END)                     AS digital_count
            FROM cash_transactions ct
            WHERE ct.wallet_id = %s {date_condition}
        ''', params_base)
        row = cursor.fetchone()

        income_cents  = float(row['income_cents']  or 0)
        expense_cents = float(row['expense_cents'] or 0)
        tx_count      = int(row['tx_count'] or 0)
        income_count  = int(row['income_count']  or 0)
        expense_count = int(row['expense_count'] or 0)
        active_days   = int(row['active_days'] or 1)

        income  = income_cents  / 100
        expense = expense_cents / 100
        profit  = income - expense
        margin  = (profit / income * 100) if income > 0 else 0.0

        # Top categories
        cursor.execute(f'''
            SELECT category, transaction_type,
                   SUM(amount_cents) AS total_cents
            FROM cash_transactions
            WHERE wallet_id = %s {date_condition}
              AND category IS NOT NULL
            GROUP BY category, transaction_type
            ORDER BY total_cents DESC
        ''', params_base)
        cat_rows = cursor.fetchall()

        top_income_cat  = None
        top_expense_cat = None
        income_cats     = {}
        expense_cats    = {}
        for cr in cat_rows:
            cat    = cr['category']
            cents  = float(cr['total_cents'] or 0)
            tx_t   = cr['transaction_type']
            if tx_t in INCOME_TYPES:
                income_cats[cat] = income_cats.get(cat, 0) + cents
            else:
                expense_cats[cat] = expense_cats.get(cat, 0) + cents

        if income_cats:
            top_income_cat = max(income_cats, key=income_cats.get)
        if expense_cats:
            top_expense_cat = max(expense_cats, key=expense_cats.get)

        # Payment method breakdown
        cash_income   = 0.0
        digital_income= 0.0
        cash_expense  = 0.0
        digital_expense = 0.0
        cursor.execute(f'''
            SELECT payment_method, transaction_type, SUM(amount_cents) AS total
            FROM cash_transactions
            WHERE wallet_id = %s {date_condition}
            GROUP BY payment_method, transaction_type
        ''', params_base)
        for pr in cursor.fetchall():
            amt = float(pr['total'] or 0) / 100
            pm  = pr['payment_method']
            ttype = pr['transaction_type']
            if ttype in INCOME_TYPES:
                if pm == 'CASH':    cash_income    += amt
                else:               digital_income += amt
            else:
                if pm == 'CASH':    cash_expense   += amt
                else:               digital_expense += amt

        trend = 'POSITIVE' if profit > 0 else ('NEGATIVE' if profit < 0 else 'STABLE')

        return {
            'period':                   period,
            'total_income':             round(income, 2),
            'total_expenses':           round(expense, 2),
            'net_profit':               round(profit, 2),
            'profit_margin':            round(margin, 1),
            'transaction_count':        tx_count,
            'income_count':             income_count,
            'expense_count':            expense_count,
            'avg_transaction':          round(float(row['avg_tx_cents'] or 0) / 100, 2),
            'avg_income':               round(float(row['avg_income_cents'] or 0) / 100, 2),
            'avg_expense':              round(float(row['avg_expense_cents'] or 0) / 100, 2),
            'top_income_category':      top_income_cat,
            'top_expense_category':     top_expense_cat,
            'payment_method_breakdown': {
                'CASH':    {'income': round(cash_income, 2),    'expense': round(cash_expense, 2)},
                'DIGITAL': {'income': round(digital_income, 2), 'expense': round(digital_expense, 2)},
            },
            'daily_average_income':     round(income / active_days, 2),
            'daily_average_expense':    round(expense / active_days, 2),
            'active_days':              active_days,
            'cash_flow_trend':          trend,
        }

    def get_daily_summary(self, wallet_id: int, date: str) -> Dict:
        """Get income/expense/net for a specific day."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT
                COALESCE(SUM(CASE WHEN transaction_type IN ('CASH_IN','DIGITAL_IN','CREDIT_COLLECTED')
                                  THEN amount_cents ELSE 0 END), 0) AS income_cents,
                COALESCE(SUM(CASE WHEN transaction_type IN ('CASH_OUT','CREDIT_GIVEN')
                                  THEN amount_cents ELSE 0 END), 0) AS expense_cents,
                COUNT(*) AS tx_count
            FROM cash_transactions
            WHERE wallet_id = %s AND transaction_date = %s
        ''', (wallet_id, date))
        row = cursor.fetchone()

        income  = float(row['income_cents']  or 0) / 100
        expense = float(row['expense_cents'] or 0) / 100

        # Opening balance = current balance minus today's net
        cursor.execute(
            'SELECT virtual_balance_cents FROM cash_wallets WHERE wallet_id = %s',
            (wallet_id,)
        )
        wr = cursor.fetchone()
        closing   = float(wr['virtual_balance_cents'] or 0) / 100 if wr else 0.0
        opening   = closing - (income - expense)

        return {
            'date':              date,
            'income':            round(income, 2),
            'expense':           round(expense, 2),
            'net':               round(income - expense, 2),
            'transaction_count': int(row['tx_count'] or 0),
            'opening_balance':   round(opening, 2),
            'closing_balance':   round(closing, 2),
        }
