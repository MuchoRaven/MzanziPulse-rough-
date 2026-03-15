"""
EmpowerScore Calculator
Dynamic credit score based on user's business behavior
"""

from datetime import datetime, timedelta
import os
from db import get_db


class EmpowerScoreCalculator:
    """
    Calculate EmpowerScore (0-1000) based on:
    1. Transaction Consistency (25%)
    2. Financial Health (25%)
    3. Business Growth (20%)
    4. Data Quality (15%)
    5. Affordability (15%)
    """

    def __init__(self):
        """Initialize calculator"""
        pass
    
    def calculate_score(self, user_id: int) -> dict:
        """Calculate comprehensive EmpowerScore"""
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Get business data
        cursor.execute('''
            SELECT b.business_id, b.created_at
            FROM businesses b
            WHERE b.user_id = %s
        ''', (user_id,))
        
        business = cursor.fetchone()
        
        if not business:
            conn.close()
            return {'score': 0, 'tier': 'UNSCORED', 'breakdown': {}}
        
        business_id = business['business_id']
        
        # Get wallet
        cursor.execute('''
            SELECT cw.wallet_id, cw.virtual_balance_cents, cw.cash_on_hand_cents
            FROM cash_wallets cw
            WHERE cw.business_id = %s
        ''', (business_id,))
        
        wallet = cursor.fetchone()
        
        if not wallet:
            conn.close()
            return {'score': 0, 'tier': 'UNSCORED', 'breakdown': {}}
        
        wallet_id = wallet['wallet_id']
        
        # ═══════════════════════════════════════════════════════════════
        # 1. TRANSACTION CONSISTENCY (250 points)
        # ═══════════════════════════════════════════════════════════════
        
        consistency_score = self._calculate_consistency(cursor, wallet_id)
        
        # ═══════════════════════════════════════════════════════════════
        # 2. FINANCIAL HEALTH (250 points)
        # ═══════════════════════════════════════════════════════════════
        
        health_score = self._calculate_financial_health(cursor, wallet_id, wallet)
        
        # ═══════════════════════════════════════════════════════════════
        # 3. BUSINESS GROWTH (200 points)
        # ═══════════════════════════════════════════════════════════════
        
        growth_score = self._calculate_growth(cursor, wallet_id)
        
        # ═══════════════════════════════════════════════════════════════
        # 4. DATA QUALITY (150 points)
        # ═══════════════════════════════════════════════════════════════
        
        quality_score = self._calculate_data_quality(cursor, wallet_id)
        
        # ═══════════════════════════════════════════════════════════════
        # 5. AFFORDABILITY (150 points)
        # ═══════════════════════════════════════════════════════════════
        
        affordability_score = self._calculate_affordability(cursor, wallet_id)
        
        # ═══════════════════════════════════════════════════════════════
        # TOTAL SCORE
        # ═══════════════════════════════════════════════════════════════
        
        total_score = int(
            consistency_score['score'] +
            health_score['score'] +
            growth_score['score'] +
            quality_score['score'] +
            affordability_score['score']
        )
        
        # Determine tier
        tier = self._get_tier(total_score)
        
        conn.close()
        
        return {
            'score': total_score,
            'tier': tier,
            'breakdown': {
                'consistency': consistency_score,
                'financialHealth': health_score,
                'growth': growth_score,
                'dataQuality': quality_score,
                'affordability': affordability_score
            },
            'maxScore': 1000
        }
    
    def _calculate_consistency(self, cursor, wallet_id: int) -> dict:
        """Transaction consistency score (0-250 points)"""
        
        # Count transactions in last 30 days
        cursor.execute('''
            SELECT COUNT(*) as count
            FROM cash_transactions
            WHERE wallet_id = %s
            AND transaction_date >= CURRENT_DATE - INTERVAL '30 days'
        ''', (wallet_id,))
        
        count = cursor.fetchone()['count']
        
        # Count active days (days with at least 1 transaction)
        cursor.execute('''
            SELECT COUNT(DISTINCT DATE(transaction_date)) as active_days
            FROM cash_transactions
            WHERE wallet_id = %s
            AND transaction_date >= CURRENT_DATE - INTERVAL '30 days'
        ''', (wallet_id,))
        
        active_days = cursor.fetchone()['active_days']
        
        # Score calculation
        score = 0
        
        # Base points for having transactions
        if count > 0:
            score += 50
        
        # Points for frequency (max 100)
        frequency_score = min(count * 2, 100)
        score += frequency_score
        
        # Points for consistency (max 100)
        if active_days > 0:
            consistency_rate = (active_days / 30) * 100
            consistency_score = min(consistency_rate, 100)
            score += consistency_score
        
        return {
            'score': score,
            'maxScore': 250,
            'transactionCount': count,
            'activeDays': active_days,
            'consistency': round((active_days / 30 * 100), 1) if active_days > 0 else 0
        }
    
    def _calculate_financial_health(self, cursor, wallet_id: int, wallet) -> dict:
        """Financial health score (0-250 points)"""
        
        # Get revenue and expenses
        cursor.execute('''
            SELECT 
                SUM(CASE WHEN transaction_type IN ('CASH_IN', 'DIGITAL_IN') 
                    THEN amount_cents ELSE 0 END) as revenue,
                SUM(CASE WHEN transaction_type = 'CASH_OUT' 
                    THEN amount_cents ELSE 0 END) as expenses
            FROM cash_transactions
            WHERE wallet_id = %s
            AND transaction_date >= CURRENT_DATE - INTERVAL '30 days'
        ''', (wallet_id,))
        
        row = cursor.fetchone()
        revenue = (row['revenue'] or 0) / 100.0
        expenses = (row['expenses'] or 0) / 100.0
        profit = revenue - expenses
        
        score = 0
        
        # Points for profitability (max 100)
        if profit > 0:
            score += 100
        elif profit > -500:
            score += 50
        
        # Points for revenue (max 100)
        if revenue >= 5000:
            score += 100
        elif revenue >= 2000:
            score += 70
        elif revenue >= 500:
            score += 40
        elif revenue > 0:
            score += 20
        
        # Points for positive balance (max 50)
        balance = wallet['virtual_balance_cents'] / 100.0
        if balance >= 1000:
            score += 50
        elif balance >= 500:
            score += 30
        elif balance > 0:
            score += 15
        
        return {
            'score': score,
            'maxScore': 250,
            'revenue': revenue,
            'expenses': expenses,
            'profit': profit,
            'balance': balance
        }
    
    def _calculate_growth(self, cursor, wallet_id: int) -> dict:
        """Business growth score (0-200 points)"""
        
        # Compare last 15 days vs previous 15 days
        cursor.execute('''
            SELECT 
                SUM(CASE WHEN transaction_date >= CURRENT_DATE - INTERVAL '15 days'
                    AND transaction_type IN ('CASH_IN', 'DIGITAL_IN')
                    THEN amount_cents ELSE 0 END) as recent_revenue,
                SUM(CASE WHEN transaction_date >= CURRENT_DATE - INTERVAL '30 days'
                    AND transaction_date < CURRENT_DATE - INTERVAL '15 days'
                    AND transaction_type IN ('CASH_IN', 'DIGITAL_IN')
                    THEN amount_cents ELSE 0 END) as previous_revenue
            FROM cash_transactions
            WHERE wallet_id = %s
        ''', (wallet_id,))
        
        row = cursor.fetchone()
        recent = (row['recent_revenue'] or 0) / 100.0
        previous = (row['previous_revenue'] or 0) / 100.0
        
        score = 0
        growth_rate = 0
        
        if previous > 0:
            growth_rate = ((recent - previous) / previous) * 100
            
            if growth_rate >= 20:
                score += 200  # Excellent growth
            elif growth_rate >= 10:
                score += 150
            elif growth_rate >= 0:
                score += 100  # Stable
            elif growth_rate >= -10:
                score += 50
        elif recent > 0:
            score += 100  # New business with revenue
        
        return {
            'score': score,
            'maxScore': 200,
            'recentRevenue': recent,
            'previousRevenue': previous,
            'growthRate': round(growth_rate, 1)
        }
    
    def _calculate_data_quality(self, cursor, wallet_id: int) -> dict:
        """Data quality score (0-150 points)"""
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN category IS NOT NULL AND category != '' THEN 1 ELSE 0 END) as categorized,
                SUM(CASE WHEN verified = 1 THEN 1 ELSE 0 END) as verified
            FROM cash_transactions
            WHERE wallet_id = %s
            AND transaction_date >= CURRENT_DATE - INTERVAL '30 days'
        ''', (wallet_id,))
        
        row = cursor.fetchone()
        total = row['total'] or 0
        categorized = row['categorized'] or 0
        verified = row['verified'] or 0
        
        score = 0
        
        if total > 0:
            # Points for categorization (max 75)
            categorization_rate = (categorized / total) * 75
            score += categorization_rate
            
            # Points for verification (max 75)
            verification_rate = (verified / total) * 75
            score += verification_rate
        
        return {
            'score': int(score),
            'maxScore': 150,
            'categorizationRate': round((categorized / total * 100), 1) if total > 0 else 0,
            'verificationRate': round((verified / total * 100), 1) if total > 0 else 0
        }
    
    def _calculate_affordability(self, cursor, wallet_id: int) -> dict:
        """Affordability score based on income vs expenses (0-150 points)"""
        
        cursor.execute('''
            SELECT 
                SUM(CASE WHEN transaction_type IN ('CASH_IN', 'DIGITAL_IN') 
                    THEN amount_cents ELSE 0 END) as income,
                SUM(CASE WHEN transaction_type = 'CASH_OUT' 
                    THEN amount_cents ELSE 0 END) as expenses
            FROM cash_transactions
            WHERE wallet_id = %s
            AND transaction_date >= CURRENT_DATE - INTERVAL '30 days'
        ''', (wallet_id,))
        
        row = cursor.fetchone()
        income = (row['income'] or 0) / 100.0
        expenses = (row['expenses'] or 0) / 100.0
        
        score = 0
        affordability_ratio = 0
        
        if expenses > 0:
            affordability_ratio = (income / expenses) * 100
            
            # Healthy: Income > Expenses
            if affordability_ratio >= 150:
                score += 150  # Excellent
            elif affordability_ratio >= 120:
                score += 120
            elif affordability_ratio >= 100:
                score += 90  # Breaking even
            elif affordability_ratio >= 80:
                score += 60
            else:
                score += 30  # Struggling
        elif income > 0:
            score += 100  # Has income, no tracked expenses
        
        return {
            'score': int(score),
            'maxScore': 150,
            'income': income,
            'expenses': expenses,
            'affordabilityRatio': round(affordability_ratio, 1)
        }
    
    def _get_tier(self, score: int) -> str:
        """Determine tier based on score"""
        if score >= 800:
            return 'PRIME'
        elif score >= 650:
            return 'EXCELLENT'
        elif score >= 500:
            return 'GOOD'
        elif score >= 350:
            return 'BUILDER'
        elif score >= 200:
            return 'STARTER'
        else:
            return 'DEVELOPING'


# ════════════════════════════════════════════════════════════════════════════
# TEST
# ════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python empowerscore_calculator.py <user_id>")
        sys.exit(1)
    
    user_id = int(sys.argv[1])
    calculator = EmpowerScoreCalculator()
    result = calculator.calculate_score(user_id)
    
    print("=" * 80)
    print(f"📊 EmpowerScore for User {user_id}")
    print("=" * 80)
    print(f"\n🎯 Total Score: {result['score']}/{result['maxScore']}")
    print(f"🏆 Tier: {result['tier']}")
    print(f"\n📈 Breakdown:")
    for key, data in result['breakdown'].items():
        print(f"   {key}: {data['score']}/{data['maxScore']} points")
    print("\n" + "=" * 80)