"""
Weekly Cash Reconciliation Demo
Simulates the trust-building weekly check-in
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join('..', 'database', 'mzansipulse.db')

class ReconciliationSystem:
    """
    Weekly cash counting and reconciliation
    """
    
    def __init__(self):
        self.tolerance_percentage = 5.0  # 5% tolerance for accuracy
    
    def perform_reconciliation(self, wallet_id: int, 
                              declared_balance_cents: int,
                              reason_if_different: str = None) -> dict:
        """
        Reconcile user's declared balance with system balance
        
        Args:
            wallet_id: Wallet to reconcile
            declared_balance_cents: What user counted (in cents)
            reason_if_different: User's explanation if there's a discrepancy
        
        Returns:
            Reconciliation result
        """
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get current system balance
        cursor.execute('''
            SELECT virtual_balance_cents, cash_on_hand_cents,
                   reconciliation_count, accurate_reconciliations
            FROM cash_wallets
            WHERE wallet_id = ?
        ''', (wallet_id,))
        
        wallet_data = cursor.fetchone()
        system_balance, cash_balance, recon_count, accurate_count = wallet_data
        
        # Calculate difference
        difference = declared_balance_cents - system_balance
        difference_pct = abs((difference / system_balance) * 100) if system_balance > 0 else 0
        
        # Determine if accurate (within tolerance)
        is_accurate = difference_pct <= self.tolerance_percentage
        
        # Save reconciliation record
        cursor.execute('''
            INSERT INTO reconciliations (
                wallet_id, system_balance_cents, declared_balance_cents,
                difference_cents, difference_percentage, is_accurate,
                discrepancy_reason, correction_made, reconciliation_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            wallet_id,
            system_balance,
            declared_balance_cents,
            difference,
            difference_pct,
            1 if is_accurate else 0,
            reason_if_different,
            1 if reason_if_different else 0,
            datetime.now().strftime('%Y-%m-%d')
        ))
        
        # Update wallet stats
        new_recon_count = recon_count + 1
        new_accurate_count = accurate_count + (1 if is_accurate else 0)
        new_accuracy_pct = (new_accurate_count / new_recon_count) * 100
        
        cursor.execute('''
            UPDATE cash_wallets
            SET reconciliation_count = ?,
                accurate_reconciliations = ?,
                accuracy_percentage = ?,
                last_reconciliation_date = ?
            WHERE wallet_id = ?
        ''', (
            new_recon_count,
            new_accurate_count,
            new_accuracy_pct,
            datetime.now().strftime('%Y-%m-%d'),
            wallet_id
        ))
        
        # If user provided reason, adjust balance
        if reason_if_different and not is_accurate:
            cursor.execute('''
                UPDATE cash_wallets
                SET virtual_balance_cents = ?,
                    cash_on_hand_cents = ?
                WHERE wallet_id = ?
            ''', (declared_balance_cents, declared_balance_cents, wallet_id))
        
        conn.commit()
        conn.close()
        
        return {
            'system_balance': system_balance / 100,
            'declared_balance': declared_balance_cents / 100,
            'difference': difference / 100,
            'difference_percentage': difference_pct,
            'is_accurate': is_accurate,
            'accuracy_rating': new_accuracy_pct,
            'reconciliation_count': new_recon_count
        }


# ============================================================================
# DEMO: Friday Reconciliation
# ============================================================================

def demo_reconciliation():
    """
    Simulate Friday cash counting
    """
    print("=" * 80)
    print("📊 FRIDAY RECONCILIATION - DEMO")
    print("=" * 80)
    
    reconciler = ReconciliationSystem()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get wallets
    cursor.execute('''
        SELECT w.wallet_id, b.business_name, u.first_name,
               w.virtual_balance_cents
        FROM cash_wallets w
        JOIN businesses b ON w.business_id = b.business_id
        JOIN users u ON b.user_id = u.user_id
    ''')
    
    wallets = cursor.fetchall()
    conn.close()
    
    # ========================================================================
    # MAMA THANDI'S RECONCILIATION (Has discrepancy!)
    # ========================================================================
    
    thandi_wallet_id, business_name, owner, system_balance = wallets[0]
    
    print(f"\n{'='*80}")
    print(f"👤 {owner}'s {business_name}")
    print(f"{'='*80}")
    
    print(f"\n🤖 MzansiPulse:")
    print(f"   'Good evening, Mama Thandi! It's Friday - time to count your cash.'")
    print(f"   'My records say you should have: R{system_balance/100:,.2f}'")
    print(f"   'Please count your tin and tell me how much you have.'")
    
    # Thandi counts (R300 less because of unlogged personal withdrawal)
    actual_cash = system_balance - 30000
    
    print(f"\n👤 Mama Thandi:")
    print(f"   'I counted R{actual_cash/100:,.2f}'")
    
    print(f"\n🤖 MzansiPulse:")
    print(f"   'Hmm, there's a difference of R300.'")
    print(f"   'What happened to that R300?'")
    print(f"   '1. Forgot to log some expenses?'")
    print(f"   '2. Personal withdrawal?'")
    print(f"   '3. Lost/stolen?'")
    
    print(f"\n👤 Mama Thandi:")
    print(f"   'Oh! I took R300 for personal groceries on Thursday. Forgot to log it.'")
    
    # Perform reconciliation
    result = reconciler.perform_reconciliation(
        thandi_wallet_id,
        actual_cash,
        "Personal withdrawal R300 for groceries - forgot to log"
    )
    
    print(f"\n🤖 MzansiPulse:")
    print(f"   '✅ Thank you for being honest, Mama Thandi!'")
    print(f"   '📝 I've logged that personal withdrawal now.'")
    print(f"   '💰 Your balance is now correct: R{result['declared_balance']:,.2f}'")
    print(f"   ''")
    print(f"   '📊 Reconciliation Stats:'")
    print(f"   '   • Accuracy: {result['accuracy_rating']:.1f}%'")
    print(f"   '   • Reconciliations: {result['reconciliation_count']}'")
    print(f"   '   '")
    print(f"   '🌟 Your honesty score just improved!'")
    print(f"   '   Banks love accurate record-keeping!'")
    
    # ========================================================================
    # THABO'S RECONCILIATION (Perfect match!)
    # ========================================================================
    
    thabo_wallet_id, business_name, owner, system_balance = wallets[1]
    
    print(f"\n\n{'='*80}")
    print(f"👤 {owner}'s {business_name}")
    print(f"{'='*80}")
    
    print(f"\n🤖 MzansiPulse:")
    print(f"   'Dumela, Thabo! Friday reconciliation time.'")
    print(f"   'My records say you should have: R{system_balance/100:,.2f}'")
    print(f"   'Count your cash and tell me.'")
    
    # Thabo's count matches perfectly
    print(f"\n👤 Thabo:")
    print(f"   'I have R{system_balance/100:,.2f}'")
    
    result = reconciler.perform_reconciliation(
        thabo_wallet_id,
        system_balance
    )
    
    print(f"\n🤖 MzansiPulse:")
    print(f"   '🎉 PERFECT MATCH, Thabo!'")
    print(f"   '💯 Your records are 100% accurate!'")
    print(f"   ''")
    print(f"   '📊 Reconciliation Stats:'")
    print(f"   '   • Accuracy: {result['accuracy_rating']:.1f}% (EXCELLENT!)'")
    print(f"   '   • Reconciliations: {result['reconciliation_count']}'")
    print(f"   '   '")
    print(f"   '🏆 Your EmpowerScore will increase!'")
    print(f"   '   Perfect reconciliation = High trust from banks!'")
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    
    print(f"\n\n{'='*80}")
    print("📊 RECONCILIATION SUMMARY")
    print(f"{'='*80}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT b.business_name, u.first_name,
               w.reconciliation_count, w.accurate_reconciliations,
               w.accuracy_percentage
        FROM cash_wallets w
        JOIN businesses b ON w.business_id = b.business_id
        JOIN users u ON b.user_id = u.user_id
    ''')
    
    for row in cursor.fetchall():
        name, owner, count, accurate, accuracy_pct = row
        print(f"\n👤 {owner}'s {name}")
        print(f"   Reconciliations: {count}")
        print(f"   Accurate: {accurate}/{count}")
        print(f"   Accuracy Rate: {accuracy_pct:.1f}%")
        
        if accuracy_pct >= 95:
            print(f"   Rating: ⭐⭐⭐⭐⭐ EXCELLENT")
        elif accuracy_pct >= 85:
            print(f"   Rating: ⭐⭐⭐⭐ VERY GOOD")
        elif accuracy_pct >= 75:
            print(f"   Rating: ⭐⭐⭐ GOOD")
        else:
            print(f"   Rating: ⭐⭐ NEEDS IMPROVEMENT")
    
    conn.close()
    
    print(f"\n{'='*80}")
    print("✅ RECONCILIATION DEMO COMPLETE!")
    print(f"{'='*80}")
    print("\n💡 Why This Matters:")
    print("   • Proves users are honest about their cash")
    print("   • Builds trust with banks and funders")
    print("   • Catches mistakes before they become problems")
    print("   • Creates habit of regular financial review")
    print("   • Reconciliation accuracy = Part of EmpowerScore!")
    print(f"{'='*80}")

if __name__ == "__main__":
    demo_reconciliation()