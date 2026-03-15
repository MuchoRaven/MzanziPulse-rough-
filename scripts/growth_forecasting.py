"""
AI-Powered Growth Forecasting
Uses DeepSeek V3.1 for intelligent business projections
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

try:
    from openrouter_helper import OpenRouterHelper
    AI_AVAILABLE = True
except ImportError:
    print("⚠️  OpenRouter helper not available")
    AI_AVAILABLE = False


class GrowthForecaster:
    """
    AI-powered business growth forecasting
    Analyzes historical data and predicts future performance
    """
    
    def __init__(self):
        """Initialize growth forecaster"""
        if AI_AVAILABLE:
            self.ai = OpenRouterHelper()
            # Use DeepSeek for analysis (best price/performance)
            self.forecast_model = os.environ.get('OPENROUTER_ADVANCED_MODEL', 'deepseek/deepseek-chat-v3.1')
        else:
            self.ai = None
        
        print("✅ Growth Forecaster initialized")
    
    # ═══════════════════════════════════════════════════════════════════
    # REVENUE FORECASTING
    # ═══════════════════════════════════════════════════════════════════
    
    def forecast_revenue(self, historical_data: Dict[str, Any], 
                        months_ahead: int = 12) -> Dict[str, Any]:
        """
        Forecast revenue for next N months
        
        Args:
            historical_data: {
                'monthlyRevenue': [list of monthly revenue],
                'monthlyTransactions': [list of transaction counts],
                'businessType': str,
                'location': str,
                'seasonality': bool
            }
            months_ahead: Number of months to forecast
            
        Returns:
            dict: Forecast with confidence intervals
        """
        
        if not self.ai:
            return self._statistical_forecast(historical_data, months_ahead)
        
        # Build AI prompt for forecasting
        prompt = self._build_forecast_prompt(historical_data, months_ahead)
        
        try:
            # Call AI for intelligent forecast
            response = self.ai.client.chat.completions.create(
                model=self.forecast_model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert business analyst specializing in township entrepreneurship in South Africa.
                        
You analyze historical business data and create realistic growth forecasts considering:
- Seasonal patterns (holidays, month-end)
- Economic conditions in South Africa
- Township business dynamics
- Cash flow patterns
- Growth potential

Respond ONLY with valid JSON in this exact format:
{
  "forecast": [
    {"month": 1, "revenue": 15000.0, "confidence": "HIGH"},
    {"month": 2, "revenue": 15750.0, "confidence": "HIGH"}
  ],
  "insights": ["Insight 1", "Insight 2"],
  "risks": ["Risk 1", "Risk 2"],
  "opportunities": ["Opportunity 1", "Opportunity 2"],
  "breakEvenMonth": 3,
  "recommendedActions": ["Action 1", "Action 2"]
}"""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Lower for more consistent forecasts
                max_tokens=2000
            )
            
            # Parse AI response
            ai_text = response.choices[0].message.content
            
            # Clean JSON (remove markdown if present)
            clean_text = ai_text.replace('```json', '').replace('```', '').strip()
            
            forecast_data = json.loads(clean_text)
            
            return {
                'success': True,
                'forecast': forecast_data['forecast'],
                'insights': forecast_data.get('insights', []),
                'risks': forecast_data.get('risks', []),
                'opportunities': forecast_data.get('opportunities', []),
                'breakEvenMonth': forecast_data.get('breakEvenMonth'),
                'recommendedActions': forecast_data.get('recommendedActions', []),
                'method': 'AI_POWERED',
                'model': self.forecast_model,
                'generatedAt': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ AI forecast error: {e}")
            # Fallback to statistical method
            return self._statistical_forecast(historical_data, months_ahead)
    
    def _build_forecast_prompt(self, historical_data: Dict[str, Any], months_ahead: int) -> str:
        """Build detailed prompt for AI forecasting"""
        
        monthly_revenue = historical_data.get('monthlyRevenue', [])
        monthly_transactions = historical_data.get('monthlyTransactions', [])
        business_type = historical_data.get('businessType', 'GENERAL')
        location = historical_data.get('location', 'South Africa')
        
        # Calculate basic stats
        avg_revenue = sum(monthly_revenue) / len(monthly_revenue) if monthly_revenue else 0
        avg_transactions = sum(monthly_transactions) / len(monthly_transactions) if monthly_transactions else 0
        
        # Detect trend
        if len(monthly_revenue) >= 3:
            recent_avg = sum(monthly_revenue[-3:]) / 3
            older_avg = sum(monthly_revenue[:3]) / 3 if len(monthly_revenue) >= 6 else avg_revenue
            growth_rate = ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0
        else:
            growth_rate = 0
        
        prompt = f"""Analyze this South African township business and forecast the next {months_ahead} months:

BUSINESS PROFILE:
- Type: {business_type}
- Location: {location}
- Current Average Revenue: R{avg_revenue:,.2f}/month
- Current Average Transactions: {avg_transactions:.0f}/month
- Observed Growth Rate: {growth_rate:.1f}% over recent period

HISTORICAL DATA (Last {len(monthly_revenue)} months):
Revenue: {[round(r, 2) for r in monthly_revenue]}
Transactions: {monthly_transactions}

CONTEXT:
This is a township business in South Africa. Consider:
- Month-end spikes (customers get paid)
- Festive season (Dec-Jan)
- Back-to-school (Jan)
- Economic pressures on customers
- Cash flow constraints

Create a realistic {months_ahead}-month forecast that accounts for:
1. Seasonal patterns
2. Growth potential if business continues current trajectory
3. Risks (economic downturn, competition)
4. Opportunities (expanding product range, new customers)

For each month, provide revenue estimate and confidence level (HIGH/MEDIUM/LOW).
Also identify the break-even month and give actionable recommendations.

Return ONLY valid JSON, no markdown or explanations."""
        
        return prompt
    
    def _statistical_forecast(self, historical_data: Dict[str, Any], 
                             months_ahead: int) -> Dict[str, Any]:
        """
        Simple statistical forecast (fallback when AI unavailable)
        Uses linear regression and seasonal adjustment
        """
        
        monthly_revenue = historical_data.get('monthlyRevenue', [])
        
        if not monthly_revenue:
            return {
                'success': False,
                'error': 'No historical data provided'
            }
        
        # Calculate average and growth rate
        avg_revenue = sum(monthly_revenue) / len(monthly_revenue)
        
        # Simple linear trend
        if len(monthly_revenue) >= 2:
            growth_rate = (monthly_revenue[-1] - monthly_revenue[0]) / len(monthly_revenue)
        else:
            growth_rate = 0
        
        # Generate forecast
        forecast = []
        current_revenue = monthly_revenue[-1] if monthly_revenue else avg_revenue
        
        for month in range(1, months_ahead + 1):
            projected = current_revenue + (growth_rate * month)
            
            # Apply seasonal adjustment (simple)
            seasonal_factor = 1.0
            month_of_year = (datetime.now().month + month - 1) % 12 + 1
            
            if month_of_year == 12:  # December (festive season)
                seasonal_factor = 1.3
            elif month_of_year == 1:  # January (back to school)
                seasonal_factor = 1.2
            elif month_of_year in [6, 7]:  # Mid-year (winter slowdown)
                seasonal_factor = 0.9
            
            adjusted = projected * seasonal_factor
            
            forecast.append({
                'month': month,
                'revenue': round(adjusted, 2),
                'confidence': 'MEDIUM'
            })
        
        return {
            'success': True,
            'forecast': forecast,
            'insights': [
                f'Based on {len(monthly_revenue)} months of data',
                f'Average monthly revenue: R{avg_revenue:,.2f}',
                f'Projected growth: R{growth_rate:,.2f}/month'
            ],
            'risks': [
                'Forecast assumes stable economic conditions',
                'Does not account for major market changes'
            ],
            'opportunities': [
                'Expand product range',
                'Improve marketing'
            ],
            'method': 'STATISTICAL',
            'generatedAt': datetime.now().isoformat()
        }
    
    # ═══════════════════════════════════════════════════════════════════
    # SCENARIO PLANNING
    # ═══════════════════════════════════════════════════════════════════
    
    def generate_scenarios(self, base_forecast: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate best-case, worst-case, and realistic scenarios
        
        Args:
            base_forecast: Base forecast data
            
        Returns:
            dict: Three scenario forecasts
        """
        
        forecast = base_forecast.get('forecast', [])
        
        if not forecast:
            return {'success': False, 'error': 'No forecast data'}
        
        scenarios = {
            'optimistic': [],
            'realistic': [],
            'pessimistic': []
        }
        
        for month_data in forecast:
            month = month_data['month']
            base_revenue = month_data['revenue']
            
            scenarios['optimistic'].append({
                'month': month,
                'revenue': round(base_revenue * 1.25, 2),  # 25% better
                'description': 'Strong growth, new customers, expanded range'
            })
            
            scenarios['realistic'].append({
                'month': month,
                'revenue': base_revenue,
                'description': 'Steady growth as projected'
            })
            
            scenarios['pessimistic'].append({
                'month': month,
                'revenue': round(base_revenue * 0.75, 2),  # 25% worse
                'description': 'Economic pressure, increased competition'
            })
        
        return {
            'success': True,
            'scenarios': scenarios,
            'recommendation': 'Plan for realistic scenario, prepare for pessimistic'
        }
    
    # ═══════════════════════════════════════════════════════════════════
    # MILESTONE PROJECTION
    # ═══════════════════════════════════════════════════════════════════
    
    def project_milestones(self, forecast: Dict[str, Any], 
                          goals: Dict[str, float]) -> Dict[str, Any]:
        """
        Project when business will hit key milestones
        
        Args:
            forecast: Forecast data
            goals: {
                'monthlyRevenue': 50000.0,
                'cumulativeRevenue': 500000.0,
                'profitMargin': 30.0
            }
            
        Returns:
            dict: Milestone projections
        """
        
        forecast_data = forecast.get('forecast', [])
        
        if not forecast_data:
            return {'success': False, 'error': 'No forecast data'}
        
        milestones = []
        cumulative_revenue = 0
        
        for month_data in forecast_data:
            month = month_data['month']
            revenue = month_data['revenue']
            cumulative_revenue += revenue
            
            # Check monthly revenue goal
            if 'monthlyRevenue' in goals and revenue >= goals['monthlyRevenue']:
                milestones.append({
                    'type': 'MONTHLY_REVENUE',
                    'month': month,
                    'value': revenue,
                    'goal': goals['monthlyRevenue'],
                    'message': f"Reach R{goals['monthlyRevenue']:,.0f}/month in Month {month}"
                })
            
            # Check cumulative revenue goal
            if 'cumulativeRevenue' in goals and cumulative_revenue >= goals['cumulativeRevenue']:
                if not any(m['type'] == 'CUMULATIVE_REVENUE' for m in milestones):
                    milestones.append({
                        'type': 'CUMULATIVE_REVENUE',
                        'month': month,
                        'value': cumulative_revenue,
                        'goal': goals['cumulativeRevenue'],
                        'message': f"Reach R{goals['cumulativeRevenue']:,.0f} total in Month {month}"
                    })
        
        return {
            'success': True,
            'milestones': milestones,
            'projectedCumulativeRevenue': cumulative_revenue,
            'timeToGoals': len([m for m in milestones if m['type'] == 'MONTHLY_REVENUE']) > 0
        }
    
    # ═══════════════════════════════════════════════════════════════════
    # INVESTMENT IMPACT ANALYSIS
    # ═══════════════════════════════════════════════════════════════════
    
    def analyze_investment_impact(self, base_forecast: Dict[str, Any],
                                 investment_amount: float,
                                 investment_use: str) -> Dict[str, Any]:
        """
        Analyze impact of investment on growth
        
        Args:
            base_forecast: Forecast without investment
            investment_amount: Amount to invest
            investment_use: 'INVENTORY' | 'MARKETING' | 'EQUIPMENT' | 'STAFF'
            
        Returns:
            dict: Projected impact
        """
        
        # Impact multipliers based on use
        multipliers = {
            'INVENTORY': 1.5,      # 50% boost from more stock
            'MARKETING': 1.3,      # 30% boost from marketing
            'EQUIPMENT': 1.4,      # 40% boost from better equipment
            'STAFF': 1.6           # 60% boost from hiring help
        }
        
        multiplier = multipliers.get(investment_use, 1.2)
        
        forecast_data = base_forecast.get('forecast', [])
        enhanced_forecast = []
        
        for month_data in forecast_data:
            month = month_data['month']
            base_revenue = month_data['revenue']
            
            # Impact grows over time
            impact_factor = min(multiplier, 1 + ((multiplier - 1) * (month / 6)))
            enhanced_revenue = base_revenue * impact_factor
            
            enhanced_forecast.append({
                'month': month,
                'baseRevenue': base_revenue,
                'enhancedRevenue': round(enhanced_revenue, 2),
                'additionalRevenue': round(enhanced_revenue - base_revenue, 2)
            })
        
        total_additional = sum(m['additionalRevenue'] for m in enhanced_forecast)
        roi = (total_additional / investment_amount * 100) if investment_amount > 0 else 0
        
        return {
            'success': True,
            'investmentAmount': investment_amount,
            'investmentUse': investment_use,
            'enhancedForecast': enhanced_forecast,
            'totalAdditionalRevenue': round(total_additional, 2),
            'roi': round(roi, 2),
            'paybackMonths': self._calculate_payback(enhanced_forecast, investment_amount),
            'recommendation': 'PROCEED' if roi > 100 else 'RECONSIDER'
        }
    
    def _calculate_payback(self, forecast: List[Dict], investment: float) -> int:
        """Calculate months until investment is paid back"""
        cumulative = 0
        for i, month_data in enumerate(forecast, 1):
            cumulative += month_data['additionalRevenue']
            if cumulative >= investment:
                return i
        return len(forecast)  # Doesn't pay back in forecast period


# ════════════════════════════════════════════════════════════════════════════
# TEST FUNCTION
# ════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    """Test growth forecasting"""
    
    print("=" * 80)
    print("📈 Testing AI Growth Forecasting")
    print("=" * 80)
    
    forecaster = GrowthForecaster()
    
    # Test data
    test_data = {
        'monthlyRevenue': [12000, 13500, 14200, 15000, 14800, 16500],
        'monthlyTransactions': [120, 135, 140, 150, 148, 165],
        'businessType': 'SPAZA_SHOP',
        'location': 'Soweto, Gauteng',
        'seasonality': True
    }
    
    # Generate forecast
    print("\n🔮 Generating 12-month forecast...")
    forecast = forecaster.forecast_revenue(test_data, months_ahead=12)
    
    if forecast['success']:
        print(f"\n✅ Method: {forecast.get('method', 'UNKNOWN')}")
        print(f"\n📊 Forecast Preview (first 6 months):")
        for month_data in forecast['forecast'][:6]:
            print(f"   Month {month_data['month']:2d}: R{month_data['revenue']:>10,.2f} ({month_data.get('confidence', 'N/A')})")
        
        if forecast.get('insights'):
            print(f"\n💡 Insights:")
            for insight in forecast['insights'][:3]:
                print(f"   • {insight}")
    
    # Test investment impact
    print("\n💰 Analyzing investment impact...")
    impact = forecaster.analyze_investment_impact(forecast, 10000, 'INVENTORY')
    
    if impact['success']:
        print(f"\n✅ Investment: R{impact['investmentAmount']:,.2f} in {impact['investmentUse']}")
        print(f"📈 Additional Revenue (12 months): R{impact['totalAdditionalRevenue']:,.2f}")
        print(f"💵 ROI: {impact['roi']:.1f}%")
        print(f"⏱️  Payback: {impact['paybackMonths']} months")
        print(f"🎯 Recommendation: {impact['recommendation']}")
    
    print("\n" + "=" * 80)