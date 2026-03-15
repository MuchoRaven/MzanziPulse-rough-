"""
MzansiPulse Grant Matching System
Automatically matches businesses to eligible grants based on EmpowerScore
"""

import json
from typing import List, Dict
from db import get_db


class GrantMatcher:
    """Matches businesses to grant opportunities"""

    def __init__(self):
        pass

    def find_matches(self, business_id: int) -> List[Dict]:
        """
        Find all grants this business is eligible for

        Args:
            business_id: ID of business to match

        Returns:
            List of grant matches with scores
        """
        conn = get_db()
        cursor = conn.cursor()
        
        # Get business details
        cursor.execute('''
            SELECT b.business_name, b.province, b.township, b.business_type,
                   cl.empower_score, cl.score_tier
            FROM businesses b
            LEFT JOIN credit_logs cl ON b.business_id = cl.business_id
            WHERE b.business_id = %s
            ORDER BY cl.created_at DESC
            LIMIT 1
        ''', (business_id,))

        business_data = cursor.fetchone()

        if not business_data:
            conn.close()
            return []

        business_name = business_data['business_name']
        province      = business_data['province']
        township      = business_data['township']
        biz_type      = business_data['business_type']
        score         = business_data['empower_score']
        tier          = business_data['score_tier']
        
        # Get all active grants
        cursor.execute('''
            SELECT grant_id, grant_name, provider, grant_type,
                   eligibility_criteria, amount_range, application_url
            FROM grant_opportunities
            WHERE is_active = 1
        ''')
        
        grants = cursor.fetchall()
        matches = []
        
        for grant in grants:
            grant_id      = grant['grant_id']
            name          = grant['grant_name']
            provider      = grant['provider']
            g_type        = grant['grant_type']
            criteria_json = grant['eligibility_criteria']
            amount        = grant['amount_range']
            url           = grant['application_url']
            
            # Parse eligibility criteria
            try:
                criteria = json.loads(criteria_json)
            except:
                criteria = {}
            
            # Check eligibility
            is_eligible, match_score, reasons = self._check_eligibility(
                score, province, township, criteria
            )
            
            if is_eligible:
                matches.append({
                    'grant_id': grant_id,
                    'grant_name': name,
                    'provider': provider,
                    'grant_type': g_type,
                    'amount_range': amount,
                    'application_url': url,
                    'match_score': match_score,
                    'match_reasons': reasons
                })
        
        # Sort by match score (best matches first)
        matches.sort(key=lambda x: x['match_score'], reverse=True)
        
        conn.close()
        return matches
    
    def _check_eligibility(self, empower_score: int, province: str,
                          township: str, criteria: dict) -> tuple:
        """
        Check if business meets grant criteria
        
        Returns:
            (is_eligible, match_score, reasons)
        """
        reasons = []
        match_score = 0.5  # Base score
        
        # Check score requirement
        min_score = criteria.get('min_score', 0)
        if empower_score >= min_score:
            reasons.append(f"EmpowerScore ({empower_score}) meets minimum ({min_score})")
            match_score += 0.3
        else:
            return False, 0.0, [f"Score too low (need {min_score}, have {empower_score})"]
        
        # Check location requirement
        required_location = criteria.get('location', '')
        if required_location:
            if 'township' in required_location.lower() and township:
                reasons.append("Located in township (grant priority area)")
                match_score += 0.2
        
        # Check province requirement
        required_provinces = criteria.get('provinces', [])
        if required_provinces and province in required_provinces:
            reasons.append(f"Province match: {province}")
            match_score += 0.1
        
        # Age requirement (if applicable - we don't have this data yet)
        # Operating months requirement
        operating_months = criteria.get('operating_months', 0)
        if operating_months:
            reasons.append(f"Operating history requirement: {operating_months} months")
        
        return True, min(match_score, 1.0), reasons
    
    def save_matches(self, business_id: int, matches: List[Dict]) -> int:
        """Save grant matches to database"""
        conn = get_db()
        cursor = conn.cursor()
        
        saved_count = 0
        
        for match in matches:
            # Check if match already exists
            cursor.execute('''
                SELECT match_id FROM grant_matches
                WHERE business_id = %s AND grant_id = %s
            ''', (business_id, match['grant_id']))

            existing = cursor.fetchone()

            if not existing:
                # Insert new match
                cursor.execute('''
                    INSERT INTO grant_matches (
                        business_id, grant_id, match_score, match_reasons,
                        application_status
                    ) VALUES (%s, %s, %s, %s, %s)
                ''', (
                    business_id,
                    match['grant_id'],
                    match['match_score'],
                    json.dumps(match['match_reasons']),
                    'RECOMMENDED'
                ))
                saved_count += 1
        
        conn.commit()
        conn.close()
        
        return saved_count


# ============================================================================
# DEMONSTRATION
# ============================================================================

def demo():
    """Demonstrate grant matching"""
    
    print("=" * 80)
    print("🎁 MzansiPulse Grant Matching System - DEMO")
    print("=" * 80)
    
    matcher = GrantMatcher()
    business_id = 1
    
    print(f"\n🔍 Finding grant matches for Business ID: {business_id}")
    print("   (Mama Thandi's Spaza Shop - EmpowerScore: 542, BUILDER tier)")
    print("\n" + "-" * 80)
    
    # Find matches
    matches = matcher.find_matches(business_id)
    
    if not matches:
        print("❌ No matching grants found")
        return
    
    print(f"\n✅ Found {len(matches)} eligible grants!\n")
    
    for i, match in enumerate(matches, 1):
        print(f"MATCH #{i}: {match['grant_name']}")
        print("-" * 80)
        print(f"   Provider:          {match['provider']}")
        print(f"   Type:              {match['grant_type']}")
        print(f"   Amount:            {match['amount_range']}")
        print(f"   Match Score:       {match['match_score']:.0%}")
        print(f"   Application URL:   {match['application_url']}")
        
        print(f"\n   ✅ Why you qualify:")
        for reason in match['match_reasons']:
            print(f"      • {reason}")
        print()
    
    # Save matches to database
    saved = matcher.save_matches(business_id, matches)
    
    print("-" * 80)
    print(f"💾 Saved {saved} new grant matches to database")
    print("=" * 80)
    print("\n💡 TIP: View matches in DB Browser → grant_matches table")
    print("=" * 80)


if __name__ == "__main__":
    demo()