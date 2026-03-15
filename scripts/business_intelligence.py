"""
Business Intelligence Helper
Fetches and analyzes user's business data for AI context
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from db import get_db

class BusinessIntelligence:
    """
    Analyzes user's business data to provide context for AI
    PRIVACY: Only accesses data for the logged-in user
    """

    def __init__(self):
        pass
    
    def get_user_business_context(self, user_id: int) -> Dict:
        """
        Get comprehensive business context for AI
        
        PRIVACY CRITICAL: Only returns data for specified user_id
        
        Args:
            user_id: The logged-in user's ID
            
        Returns:
            dict: Complete business intelligence context
        """
        conn = get_db()
        cursor = conn.cursor()
        
        try:
            # ═══════════════════════════════════════════════════════════
            # 1. USER & BUSINESS BASIC INFO
            # ═══════════════════════════════════════════════════════════
            cursor.execute('''
                SELECT 
                    u.user_id, u.first_name, u.last_name, u.phone_number,
                    u.preferred_language, u.email,
                    b.business_id, b.business_name, b.business_type,
                    b.township, b.province, b.created_at
                FROM users u
                LEFT JOIN businesses b ON u.user_id = b.user_id
                WHERE u.user_id = %s
            ''', (user_id,))
            
            user_row = cursor.fetchone()
            if not user_row:
                return {'error': 'User not found'}
            
            business_info = {
                'userId': user_row['user_id'],
                'firstName': user_row['first_name'],
                'lastName': user_row['last_name'],
                'phone': user_row['phone_number'],
                'language': user_row['preferred_language'] or 'en',
                'businessId': user_row['business_id'],
                'businessName': user_row['business_name'],
                'businessType': user_row['business_type'],
                'location': f"{user_row['township']}, {user_row['province']}",
                'businessAge': self._calculate_business_age(user_row['created_at'])
            }
            
            # ═══════════════════════════════════════════════════════════
            # 2. WALLET INFORMATION
            # ═══════════════════════════════════════════════════════════
            cursor.execute('''
                SELECT 
                    wallet_id, virtual_balance_cents, cash_on_hand_cents,
                    digital_balance_cents, credit_given_cents,
                    total_cash_sales_cents, total_digital_sales_cents,
                    total_expenses_cents, reconciliation_count,
                    accuracy_percentage, last_reconciliation_date
                FROM cash_wallets
                WHERE business_id = %s
            ''', (business_info['businessId'],))
            
            wallet_row = cursor.fetchone()
            wallet_info = {}
            if wallet_row:
                wallet_info = {
                    'totalBalance':   round((wallet_row['virtual_balance_cents']   or 0) / 100, 2),
                    'cashBalance':    round((wallet_row['cash_on_hand_cents']      or 0) / 100, 2),
                    'digitalBalance': round((wallet_row['digital_balance_cents']   or 0) / 100, 2),
                    'creditOwed':     round((wallet_row['credit_given_cents']      or 0) / 100, 2),
                    'totalSales':     round(((wallet_row['total_cash_sales_cents'] or 0) +
                                      (wallet_row['total_digital_sales_cents']    or 0)) / 100, 2),
                    'totalExpenses':  round((wallet_row['total_expenses_cents']    or 0) / 100, 2),
                    'reconciliationAccuracy': float(wallet_row['accuracy_percentage']) if wallet_row['accuracy_percentage'] is not None else None,
                    'lastReconciliation': wallet_row['last_reconciliation_date']
                }
            
            # ═══════════════════════════════════════════════════════════
            # 3. RECENT TRANSACTIONS (Last 30 days)
            # ═══════════════════════════════════════════════════════════
            thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            cursor.execute('''
                SELECT 
                    transaction_type, amount_cents, payment_method,
                    transaction_date, source_destination
                FROM cash_transactions
                WHERE wallet_id = (
                    SELECT wallet_id FROM cash_wallets 
                    WHERE business_id = %s
                )
                AND transaction_date >= %s
                ORDER BY transaction_date DESC
                LIMIT 100
            ''', (business_info['businessId'], thirty_days_ago))
            
            transactions = []
            for row in cursor.fetchall():
                transactions.append({
                    'type': row['transaction_type'],
                    'amount': row['amount_cents'] / 100,
                    'method': row['payment_method'],
                    'date': row['transaction_date'],
                    'description': row['source_destination']
                })
            
            # ═══════════════════════════════════════════════════════════
            # 4. TRANSACTION ANALYTICS
            # ═══════════════════════════════════════════════════════════
            # ✅ UPDATED: Analytics with recent transactions
            cursor.execute('''
                SELECT 
                    COUNT(DISTINCT ct.cash_transaction_id) as transaction_count,
                    SUM(CASE WHEN ct.transaction_type IN ('CASH_IN', 'DIGITAL_IN') 
                        THEN ct.amount_cents ELSE 0 END) / 100.0 as total_revenue,
                    SUM(CASE WHEN ct.transaction_type = 'CASH_OUT' 
                        THEN ct.amount_cents ELSE 0 END) / 100.0 as total_expenses,
                    AVG(CASE WHEN ct.transaction_type IN ('CASH_IN', 'DIGITAL_IN')
                        THEN ct.amount_cents ELSE NULL END) / 100.0 as avg_sale,
                    SUM(CASE WHEN ct.payment_method = 'CASH' 
                        THEN ct.amount_cents ELSE 0 END) as cash_total,
                    SUM(CASE WHEN ct.payment_method = 'DIGITAL' 
                        THEN ct.amount_cents ELSE 0 END) as digital_total,
                    MIN(ct.transaction_date) as first_transaction,
                    MAX(ct.transaction_date) as last_transaction
                FROM cash_transactions ct
                JOIN cash_wallets cw ON ct.wallet_id = cw.wallet_id
                JOIN businesses b ON cw.business_id = b.business_id
                WHERE b.user_id = %s
                AND ct.transaction_date >= CURRENT_DATE - INTERVAL '30 days'
            ''', (user_id,))
            
            analytics_row = cursor.fetchone()
            
            # Calculate metrics — cast to float so Flask JSON serialises as numbers not Decimal strings
            transaction_count = int(analytics_row['transaction_count'] or 0)
            total_revenue     = float(analytics_row['total_revenue']  or 0)
            total_expenses    = float(analytics_row['total_expenses'] or 0)
            profit = total_revenue - total_expenses

            # Calculate daily average (based on days with data)
            if transaction_count > 0:
                cursor.execute('''
                    SELECT COUNT(DISTINCT DATE(ct.transaction_date)) as active_days
                    FROM cash_transactions ct
                    JOIN cash_wallets cw ON ct.wallet_id = cw.wallet_id
                    JOIN businesses b ON cw.business_id = b.business_id
                    WHERE b.user_id = %s
                    AND ct.transaction_date >= CURRENT_DATE - INTERVAL '30 days'
                ''', (user_id,))
                active_days    = int(cursor.fetchone()['active_days'] or 1)
                avg_daily_sales = round(total_revenue / active_days, 2)
            else:
                avg_daily_sales = 0.0

            # Cash vs Digital percentage
            cash_total    = float((analytics_row['cash_total']    or 0)) / 100.0
            digital_total = float((analytics_row['digital_total'] or 0)) / 100.0
            total_payments = cash_total + digital_total

            cash_percentage = round((cash_total / total_payments * 100), 1) if total_payments > 0 else 0.0

            analytics = {
                'transactionCount':  transaction_count,
                'averageDailySales': avg_daily_sales,
                'totalSales':        round(total_revenue, 2),
                'totalExpenses':     round(total_expenses, 2),
                'profit':            round(profit, 2),
                'cashVsDigital': {
                    'cashPercentage':    cash_percentage,
                    'digitalPercentage': round(100 - cash_percentage, 1),
                    'cashAmount':        round(cash_total, 2),
                    'digitalAmount':     round(digital_total, 2)
                },
                'incomeVsExpenses': {
                    'income':       round(total_revenue, 2),
                    'expenses':     round(total_expenses, 2),
                    'profit':       round(profit, 2),
                    'profitMargin': round((profit / total_revenue * 100), 1) if total_revenue > 0 else 0.0
                },
                'firstTransaction': str(analytics_row['first_transaction']) if analytics_row['first_transaction'] else None,
                'lastTransaction':  str(analytics_row['last_transaction'])  if analytics_row['last_transaction']  else None
            }
            
            # ═══════════════════════════════════════════════════════════
            # 5. CREDIT LEDGER (Outstanding debts)
            # ═══════════════════════════════════════════════════════════
            credit_ledger = []
            total_outstanding = 0
            overdue_count = 0
            try:
                cursor.execute('''
                    SELECT
                        customer_name, amount_owed_cents, balance_cents,
                        credit_given_date, due_date, status
                    FROM credit_ledger
                    WHERE wallet_id = (
                        SELECT wallet_id FROM cash_wallets
                        WHERE business_id = %s
                    )
                    AND status != 'FULLY_PAID'
                    ORDER BY due_date ASC
                ''', (business_info['businessId'],))

                for row in cursor.fetchall():
                    balance = row['balance_cents'] / 100
                    total_outstanding += balance

                    is_overdue = False
                    if row['due_date']:
                        due_date = datetime.strptime(str(row['due_date']), '%Y-%m-%d')
                        is_overdue = due_date < datetime.now()
                        if is_overdue:
                            overdue_count += 1

                    credit_ledger.append({
                        'customer': row['customer_name'],
                        'owed': balance,
                        'dueDate': row['due_date'],
                        'isOverdue': is_overdue,
                        'status': row['status']
                    })
            except Exception:
                # credit_ledger table may not exist yet
                conn.rollback()
            
            # ═══════════════════════════════════════════════════════════
            # 6. TOP SELLING PRODUCTS (From transaction descriptions)
            # ═══════════════════════════════════════════════════════════
            cursor.execute('''
                SELECT 
                    category, COUNT(*) as count, 
                    SUM(amount_cents) as total_cents
                FROM cash_transactions
                WHERE wallet_id = (
                    SELECT wallet_id FROM cash_wallets 
                    WHERE business_id = %s
                )
                AND transaction_type IN ('CASH_IN', 'DIGITAL_IN')
                AND transaction_date >= %s
                GROUP BY category
                ORDER BY total_cents DESC
                LIMIT 10
            ''', (business_info['businessId'], thirty_days_ago))
            
            top_products = []
            for row in cursor.fetchall():
                if row['category']:
                    top_products.append({
                        'category': row['category'],
                        'count': row['count'],
                        'revenue': row['total_cents'] / 100
                    })
            
            # ═══════════════════════════════════════════════════════════
            # 7. COMBINE ALL DATA
            # ═══════════════════════════════════════════════════════════
            return {
                **business_info,
                'wallet': wallet_info,
                'recentTransactions': transactions[:10],  # Last 10 for context
                'analytics': analytics,
                'creditLedger': {
                    'outstandingAmount': total_outstanding,
                    'overdueCount': overdue_count,
                    'customers': credit_ledger[:5]  # Top 5
                },
                'topProducts': top_products,
                'dataFetchedAt': datetime.now().isoformat()
            }
             
        finally:
            conn.close()
    
    def _analyze_transactions(self, transactions: List[Dict]) -> Dict:
        """
        Analyze transaction patterns
        """
        if not transactions:
            return {
                'averageDailySales': 0,
                'cashVsDigital': {'cash': 0, 'digital': 0},
                'incomeVsExpenses': {'income': 0, 'expenses': 0},
                'transactionCount': 0
            }
        
        cash_total = 0
        digital_total = 0
        income_total = 0
        expense_total = 0
        
        for trans in transactions:
            amount = trans['amount']
            
            # Cash vs Digital
            if trans['method'] == 'CASH':
                cash_total += amount
            else:
                digital_total += amount
            
            # Income vs Expenses
            if trans['type'] in ['CASH_IN', 'DIGITAL_IN', 'CREDIT_COLLECTED']:
                income_total += amount
            else:
                expense_total += amount
        
        # Calculate daily average
        days_span = 30  # Last 30 days
        avg_daily_sales = income_total / days_span if days_span > 0 else 0
        
        return {
            'averageDailySales': round(avg_daily_sales, 2),
            'cashVsDigital': {
                'cash': round(cash_total, 2),
                'digital': round(digital_total, 2),
                'cashPercentage': round((cash_total / (cash_total + digital_total) * 100) if (cash_total + digital_total) > 0 else 0, 1)
            },
            'incomeVsExpenses': {
                'income': round(income_total, 2),
                'expenses': round(expense_total, 2),
                'profit': round(income_total - expense_total, 2)
            },
            'transactionCount': len(transactions)
        }
    
    def _calculate_business_age(self, created_at: str) -> str:
        """Calculate how long the business has been registered"""
        if not created_at:
            return "Unknown"
        
        try:
            created = datetime.fromisoformat(created_at)
            delta = datetime.now() - created
            
            if delta.days < 30:
                return f"{delta.days} days"
            elif delta.days < 365:
                months = delta.days // 30
                return f"{months} month{'s' if months > 1 else ''}"
            else:
                years = delta.days // 365
                return f"{years} year{'s' if years > 1 else ''}"
        except:
            return "Unknown"


# ════════════════════════════════════════════════════════════════════════════
# TEST
# ════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    bi = BusinessIntelligence()
    
    # Test with user_id 1
    context = bi.get_user_business_context(1)
    
    print("=" * 80)
    print("📊 BUSINESS INTELLIGENCE TEST")
    print("=" * 80)
    print(f"\nBusiness: {context.get('businessName')}")
    print(f"Owner: {context.get('firstName')} {context.get('lastName')}")
    print(f"Balance: R{context.get('wallet', {}).get('totalBalance', 0):,.2f}")
    print(f"Recent Transactions: {len(context.get('recentTransactions', []))}")
    print(f"Average Daily Sales: R{context.get('analytics', {}).get('averageDailySales', 0):,.2f}")
    print("\n✅ Business Intelligence Working!")