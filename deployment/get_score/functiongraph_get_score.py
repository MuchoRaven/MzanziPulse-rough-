"""
FunctionGraph Function: Get EmpowerScore
Endpoint: GET /score/{business_id}
Returns EmpowerScore and grant matches
"""

import json
import sqlite3
import os

from obs_helper import OBSDatabaseManager
from empower_score import EmpowerScoreCalculator

def handler(event, context):
    """
    Get EmpowerScore for a business
    
    Request: GET /score/1
    
    Response:
    {
        "business_id": 1,
        "score": 542,
        "tier": "BUILDER",
        "breakdown": {...},
        "grants": [...],
        "recommendations": [...]
    }
    """
    
    print("=" * 80)
    print("🧠 Get EmpowerScore Function Started")
    print("=" * 80)
    
    db_path = None
    obs_manager = None
    
    try:
        # Parse business_id from URL
        path_params = event.get('pathParameters', {})
        business_id = path_params.get('business_id')
        
        if not business_id:
            return error_response(400, "Missing business_id")
        
        print(f"📊 Calculating score for business_id: {business_id}")
        
        # Download database
        obs_manager = OBSDatabaseManager(
            access_key_id=os.environ.get('OBS_ACCESS_KEY'),
            secret_access_key=os.environ.get('OBS_SECRET_KEY'),
            bucket_name=os.environ.get('OBS_BUCKET_NAME', 'mzansipulse-data')
        )
        db_path = obs_manager.download_database()
        
        # Calculate EmpowerScore
        calculator = EmpowerScoreCalculator(db_path)
        score_data = calculator.calculate_score(int(business_id))
        
        # Get grant matches
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT gm.match_score, go.grant_name, go.provider,
                   go.amount_range, go.application_url
            FROM grant_matches gm
            JOIN grant_opportunities go ON gm.grant_id = go.grant_id
            WHERE gm.business_id = ?
            ORDER BY gm.match_score DESC
        ''', (business_id,))
        
        grants = [{
            'name': row[1],
            'provider': row[2],
            'amount': row[3],
            'url': row[4],
            'match': f"{row[0]:.0%}"
        } for row in cursor.fetchall()]
        
        # Get business info
        cursor.execute('''
            SELECT b.business_name, u.first_name, b.township
            FROM businesses b
            JOIN users u ON b.user_id = u.user_id
            WHERE b.business_id = ?
        ''', (business_id,))
        
        biz_info = cursor.fetchone()
        conn.close()
        
        # Build response
        response_data = {
            'business_id': int(business_id),
            'business_name': biz_info[0] if biz_info else 'Unknown',
            'owner': biz_info[1] if biz_info else 'Unknown',
            'location': biz_info[2] if biz_info else 'Unknown',
            'empower_score': score_data['empower_score'],
            'score_tier': score_data['score_tier'],
            'score_breakdown': {
                'consistency': score_data['consistency_score'],
                'growth': score_data['growth_score'],
                'diversity': score_data['diversity_score'],
                'discipline': score_data['discipline_score']
            },
            'confidence': score_data['confidence_interval'],
            'red_flags': score_data['red_flags'],
            'green_flags': score_data['green_flags'],
            'eligible_grants': grants,
            'recommendations': build_recommendations(score_data)
        }
        
        obs_manager.cleanup(db_path)
        
        print(f"✅ Score: {score_data['empower_score']}/1000 ({score_data['score_tier']})")
        print("=" * 80)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(response_data)
        }
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        if db_path:
            try:
                obs_manager.cleanup(db_path)
            except:
                pass
        return error_response(500, str(e))


def build_recommendations(score_data: dict) -> list:
    """
    Build actionable recommendations based on score breakdown
    
    CS CONCEPT: This is rule-based expert system logic
    Different score combinations → Different recommendations
    """
    recommendations = []
    
    # Low consistency → Recommend daily logging
    if score_data['consistency_score'] < 60:
        recommendations.append({
            'priority': 'HIGH',
            'area': 'Consistency',
            'action': 'Log transactions DAILY - even small sales!',
            'impact': f"+{int((60 - score_data['consistency_score']) * 0.3)} points potential"
        })
    
    # Low growth → Recommend diversification
    if score_data['growth_score'] < 50:
        recommendations.append({
            'priority': 'HIGH',
            'area': 'Revenue Growth',
            'action': 'Add 2-3 new product lines to grow revenue',
            'impact': '+25-40 points potential'
        })
    
    # Low diversity → More suppliers
    if score_data['diversity_score'] < 60:
        recommendations.append({
            'priority': 'MEDIUM',
            'area': 'Supplier Diversity',
            'action': 'Add another supplier to reduce dependency risk',
            'impact': '+15-20 points potential'
        })
    
    # Low discipline → Separate personal/business
    if score_data['discipline_score'] < 70:
        recommendations.append({
            'priority': 'HIGH',
            'area': 'Financial Discipline',
            'action': 'Stop mixing personal and business money! Open separate wallet.',
            'impact': '+20-30 points potential'
        })
    
    # All good!
    if not recommendations:
        recommendations.append({
            'priority': 'LOW',
            'area': 'General',
            'action': 'Excellent! Apply for PRIME tier grants now',
            'impact': 'Maintain current habits'
        })
    
    return recommendations


def error_response(status_code: int, message: str) -> dict:
    return {
        'statusCode': status_code,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'error': message})
    }