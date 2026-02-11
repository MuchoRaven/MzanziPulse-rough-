"""
MzansiPulse EmpowerScore Calculator
Alternative credit scoring for informal economy businesses
Calculates creditworthiness from transaction patterns, not credit history
"""

import sqlite3
import os
from datetime import datetime, timedelta
from typing import Dict, Tuple
import math

DB_PATH = os.path.join('..', 'database', 'mzansipulse.db')


class EmpowerScoreCalculator:
    """
    Calculates EmpowerScore (0-1000) for a business based on:
    1. Consistency Score: Transaction regularity
    2. Growth Score: Revenue trend
    3. Diversity Score: Supplier/product variety
    4. Discipline Score: Business vs personal separation
    """
    
    # Scoring weights (must sum to 1.0)
    WEIGHTS = {
        'consistency': 0.30,   # 30% - Most important (proves active business)
        'growth': 0.25,        # 25% - Shows potential
        'diversity': 0.25,     # 25% - Reduces risk
        'discipline': 0.20     # 20% - Shows maturity
    }
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
    
    def calculate_score(self, business_id: int, 
                       analysis_days: int = 30) -> Dict:
        """
        Calculate EmpowerScore for a business
        
        Args:
            business_id: ID of business to score
            analysis_days: Number of days to analyze (default 30)
        
        Returns:
            Dictionary with score breakdown
        """
        conn = sqlite3.connect(self.db_path)
        
        # Get transaction data
        transactions = self._get_transactions(conn, business_id, analysis_days)
        
        if len(transactions) < 5:
            # Not enough data to score
            conn.close()
            return {
                'empower_score': 0,
                'score_tier': 'INSUFFICIENT_DATA',
                'consistency_score': 0,
                'growth_score': 0,
                'diversity_score': 0,
                'discipline_score': 0,
                'confidence_interval': 0.0,
                'red_flags': ['Less than 5 transactions in analysis period'],
                'green_flags': [],
                'recommendation': 'Record more transactions to generate score'
            }
        
        # Calculate component scores
        consistency = self._calculate_consistency(transactions, analysis_days)
        growth = self._calculate_growth(transactions)
        diversity = self._calculate_diversity(transactions)
        discipline = self._calculate_discipline(transactions)
        
        # Calculate weighted final score (0-100 scale)
        weighted_score = (
            consistency * self.WEIGHTS['consistency'] +
            growth * self.WEIGHTS['growth'] +
            diversity * self.WEIGHTS['diversity'] +
            discipline * self.WEIGHTS['discipline']
        )
        
        # Scale to 0-1000
        empower_score = int(weighted_score * 10)
        
        # Determine tier
        tier = self._get_tier(empower_score)
        
        # Calculate confidence (based on data quantity and quality)
        confidence = self._calculate_confidence(transactions, analysis_days)
        
        # Identify red/green flags
        red_flags = self._identify_red_flags(transactions, consistency, discipline)
        green_flags = self._identify_green_flags(transactions, growth, diversity)
        
        conn.close()
        
        return {
            'empower_score': empower_score,
            'score_tier': tier,
            'consistency_score': round(consistency, 2),
            'growth_score': round(growth, 2),
            'diversity_score': round(diversity, 2),
            'discipline_score': round(discipline, 2),
            'confidence_interval': round(confidence, 2),
            'red_flags': red_flags,
            'green_flags': green_flags,
            'transaction_count': len(transactions),
            'analysis_period_days': analysis_days
        }
    
    def _get_transactions(self, conn, business_id: int, days: int) -> list:
        """Fetch transactions for analysis period"""
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                transaction_id,
                transaction_date,
                transaction_type,
                amount,
                category,
                payment_method,
                flagged_for_review,
                supplier_name
            FROM transactions
            WHERE business_id = ?
            AND transaction_date >= ?
            AND is_verified = 1
            ORDER BY transaction_date ASC
        ''', (business_id, cutoff_date))
        
        return cursor.fetchall()
    
    def _calculate_consistency(self, transactions: list, period_days: int) -> float:
        """
        Score based on transaction regularity (0-100)
        Higher score = more consistent recording
        """
        if not transactions:
            return 0.0
        
        # Count unique transaction dates
        unique_dates = set(t[1] for t in transactions)  # t[1] = transaction_date
        days_with_transactions = len(unique_dates)
        
        # Calculate consistency percentage
        consistency_pct = (days_with_transactions / period_days) * 100
        
        # Cap at 100
        return min(consistency_pct, 100.0)
    
    def _calculate_growth(self, transactions: list) -> float:
        """
        Score based on revenue growth trend (0-100)
        Compares first half vs second half of period
        """
        if len(transactions) < 10:
            return 50.0  # Neutral score for insufficient data
        
        # Split transactions into two halves
        mid_point = len(transactions) // 2
        first_half = transactions[:mid_point]
        second_half = transactions[mid_point:]
        
        # Calculate revenue for each half (SALES only, not purchases)
        first_revenue = sum(t[3] for t in first_half if t[2] == 'SALE')  # t[3] = amount
        second_revenue = sum(t[3] for t in second_half if t[2] == 'SALE')
        
        if first_revenue == 0:
            return 50.0  # Can't calculate growth
        
        # Calculate growth percentage
        growth_pct = ((second_revenue - first_revenue) / first_revenue) * 100
        
        # Score mapping:
        # -50% or worse = 0 points (declining business)
        # 0% = 50 points (stable)
        # +50% or more = 100 points (growing)
        
        if growth_pct <= -50:
            return 0.0
        elif growth_pct >= 50:
            return 100.0
        else:
            # Linear scale from -50% to +50%
            return 50 + growth_pct
    
    def _calculate_diversity(self, transactions: list) -> float:
        """
        Score based on product/supplier diversity (0-100)
        More categories and suppliers = lower risk
        """
        # Count unique categories
        categories = set(t[4] for t in transactions if t[4])  # t[4] = category
        category_count = len(categories)
        
        # Count unique suppliers (for PURCHASE transactions)
        suppliers = set(t[7] for t in transactions if t[2] == 'PURCHASE' and t[7])
        supplier_count = len(suppliers)
        
        # Category diversity score (max 50 points)
        # 1 category = 10, 2 = 20, 3 = 30, 4 = 40, 5+ = 50
        category_score = min(category_count * 10, 50)
        
        # Supplier diversity score (max 50 points)
        # 1 supplier = 10, 2 = 25, 3 = 40, 4+ = 50
        if supplier_count == 0:
            supplier_score = 25  # No supplier data = neutral
        elif supplier_count == 1:
            supplier_score = 10
        elif supplier_count == 2:
            supplier_score = 25
        elif supplier_count == 3:
            supplier_score = 40
        else:
            supplier_score = 50
        
        return category_score + supplier_score
    
    def _calculate_discipline(self, transactions: list) -> float:
        """
        Score based on financial discipline (0-100)
        Penalizes personal withdrawals, rewards verified transactions
        """
        total_transactions = len(transactions)
        
        # Count flagged transactions (personal use, suspicious amounts)
        flagged_count = sum(1 for t in transactions if t[6])  # t[6] = flagged_for_review
        
        # Calculate flagged percentage
        flagged_pct = (flagged_count / total_transactions) * 100
        
        # Score mapping:
        # 0% flagged = 100 points (excellent discipline)
        # 10% flagged = 75 points
        # 20% flagged = 50 points
        # 30%+ flagged = 0 points (poor separation)
        
        if flagged_pct == 0:
            return 100.0
        elif flagged_pct >= 30:
            return 0.0
        else:
            return 100 - (flagged_pct * 3.33)  # Linear decrease
    
    def _get_tier(self, score: int) -> str:
        """Determine score tier"""
        if score >= 601:
            return 'PRIME'
        elif score >= 301:
            return 'BUILDER'
        else:
            return 'STARTER'
    
    def _calculate_confidence(self, transactions: list, period_days: int) -> float:
        """
        Calculate confidence in the score (0.0 to 1.0)
        More data = higher confidence
        """
        transaction_count = len(transactions)
        
        # Confidence based on transaction count
        # 5-20 transactions = low confidence (0.3-0.6)
        # 21-50 transactions = medium confidence (0.6-0.8)
        # 51+ transactions = high confidence (0.8-1.0)
        
        if transaction_count < 20:
            return 0.3 + (transaction_count / 20) * 0.3
        elif transaction_count < 50:
            return 0.6 + ((transaction_count - 20) / 30) * 0.2
        else:
            return min(0.8 + ((transaction_count - 50) / 100) * 0.2, 1.0)
    
    def _identify_red_flags(self, transactions: list, 
                           consistency: float, discipline: float) -> list:
        """Identify warning signs"""
        flags = []
        
        # Low consistency
        if consistency < 30:
            flags.append("Irregular transaction recording (less than 30% of days)")
        
        # Poor discipline
        if discipline < 50:
            flags.append("High rate of flagged transactions (possible business/personal mixing)")
        
        # Too many purchases vs sales
        purchases = sum(1 for t in transactions if t[2] == 'PURCHASE')
        sales = sum(1 for t in transactions if t[2] == 'SALE')
        if sales > 0 and purchases / (sales + purchases) > 0.7:
            flags.append("High purchase-to-sale ratio (inventory concerns)")
        
        return flags
    
    def _identify_green_flags(self, transactions: list,
                             growth: float, diversity: float) -> list:
        """Identify positive indicators"""
        flags = []
        
        # Strong growth
        if growth > 70:
            flags.append("Strong revenue growth trend")
        
        # Good diversity
        if diversity > 70:
            flags.append("Good product and supplier diversity")
        
        # Consistent high-value sales
        sales = [t[3] for t in transactions if t[2] == 'SALE']
        if sales and len(sales) > 10:
            avg_sale = sum(sales) / len(sales)
            if avg_sale > 50:
                flags.append(f"Healthy average transaction value (R{avg_sale:.2f})")
        
        return flags
    
    def save_score(self, business_id: int, score_data: Dict) -> int:
        """Save calculated score to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Convert lists to JSON strings
        import json
        red_flags_json = json.dumps(score_data.get('red_flags', []))
        green_flags_json = json.dumps(score_data.get('green_flags', []))
        
        cursor.execute('''
            INSERT INTO credit_logs (
                business_id, score_date, empower_score, score_tier,
                consistency_score, growth_score, diversity_score,
                financial_discipline_score, model_version, confidence_interval
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            business_id,
            datetime.now().strftime('%Y-%m-%d'),
            score_data['empower_score'],
            score_data['score_tier'],
            score_data['consistency_score'],
            score_data['growth_score'],
            score_data['diversity_score'],
            score_data['discipline_score'],
            'v1.0_production',
            score_data['confidence_interval']
        ))
        
        log_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return log_id


# ============================================================================
# DEMONSTRATION FUNCTION
# ============================================================================

def demo():
    """Demonstrate EmpowerScore calculation"""
    
    print("=" * 80)
    print("🧠 MzansiPulse EmpowerScore Calculator - DEMO")
    print("=" * 80)
    
    calculator = EmpowerScoreCalculator()
    
    # Calculate score for Mama Thandi's business (ID = 1)
    business_id = 1
    
    print(f"\n📊 Calculating EmpowerScore for Business ID: {business_id}")
    print("   (Mama Thandi's Spaza Shop)")
    print("\n" + "-" * 80)
    
    # Calculate score
    score_data = calculator.calculate_score(business_id, analysis_days=30)
    
    # Display results
    print("\n🎯 EMPOWERSCORE RESULTS")
    print("=" * 80)
    print(f"\n   FINAL SCORE:          {score_data['empower_score']}/1000")
    print(f"   TIER:                 {score_data['score_tier']}")
    print(f"   CONFIDENCE:           {score_data['confidence_interval']:.0%}")
    print(f"   TRANSACTIONS ANALYZED: {score_data['transaction_count']}")
    print(f"   PERIOD:               {score_data['analysis_period_days']} days")
    
    print("\n" + "-" * 80)
    print("📈 COMPONENT BREAKDOWN")
    print("-" * 80)
    print(f"   Consistency Score:    {score_data['consistency_score']:.1f}/100")
    print(f"      (Weight: {EmpowerScoreCalculator.WEIGHTS['consistency']:.0%})")
    print(f"      → Contribution: {score_data['consistency_score'] * EmpowerScoreCalculator.WEIGHTS['consistency']:.1f} points")
    
    print(f"\n   Growth Score:         {score_data['growth_score']:.1f}/100")
    print(f"      (Weight: {EmpowerScoreCalculator.WEIGHTS['growth']:.0%})")
    print(f"      → Contribution: {score_data['growth_score'] * EmpowerScoreCalculator.WEIGHTS['growth']:.1f} points")
    
    print(f"\n   Diversity Score:      {score_data['diversity_score']:.1f}/100")
    print(f"      (Weight: {EmpowerScoreCalculator.WEIGHTS['diversity']:.0%})")
    print(f"      → Contribution: {score_data['diversity_score'] * EmpowerScoreCalculator.WEIGHTS['diversity']:.1f} points")
    
    print(f"\n   Discipline Score:     {score_data['discipline_score']:.1f}/100")
    print(f"      (Weight: {EmpowerScoreCalculator.WEIGHTS['discipline']:.0%})")
    print(f"      → Contribution: {score_data['discipline_score'] * EmpowerScoreCalculator.WEIGHTS['discipline']:.1f} points")
    
    # Red flags
    print("\n" + "-" * 80)
    print("🚩 RED FLAGS (Risk Indicators)")
    print("-" * 80)
    if score_data['red_flags']:
        for flag in score_data['red_flags']:
            print(f"   ⚠️  {flag}")
    else:
        print("   ✅ No red flags detected")
    
    # Green flags
    print("\n" + "-" * 80)
    print("🟢 GREEN FLAGS (Positive Indicators)")
    print("-" * 80)
    if score_data['green_flags']:
        for flag in score_data['green_flags']:
            print(f"   ✅ {flag}")
    else:
        print("   ℹ️  No exceptional positive indicators")
    
    # Score interpretation
    print("\n" + "=" * 80)
    print("💡 SCORE INTERPRETATION")
    print("=" * 80)
    
    tier = score_data['score_tier']
    score = score_data['empower_score']
    
    if tier == 'PRIME':
        print(f"\n   🌟 PRIME TIER ({score}/1000)")
        print("   → Eligible for: Standard bank loans, equipment financing")
        print("   → Recommended grants: SEFA loans (R100k-R3M), IDC funding")
        print("   → Risk assessment: LOW - established, growing business")
    elif tier == 'BUILDER':
        print(f"\n   📈 BUILDER TIER ({score}/1000)")
        print("   → Eligible for: Micro-loans, mentorship programs")
        print("   → Recommended grants: NYDA grants (R10k-R100k), Township Fund")
        print("   → Risk assessment: MODERATE - developing business")
    else:
        print(f"\n   🌱 STARTER TIER ({score}/1000)")
        print("   → Eligible for: Micro-grants, training programs")
        print("   → Recommended grants: SEDA support, NYDA micro-enterprise")
        print("   → Risk assessment: MODERATE-HIGH - needs support")
    
    # Save to database
    print("\n" + "-" * 80)
    log_id = calculator.save_score(business_id, score_data)
    print(f"✅ Score saved to database (Credit Log ID: {log_id})")
    
    print("\n" + "=" * 80)
    print("🎉 EmpowerScore calculation complete!")
    print("=" * 80)
    print("\n💡 TIP: View the score in DB Browser → credit_logs table")
    print("=" * 80)


if __name__ == "__main__":
    demo()