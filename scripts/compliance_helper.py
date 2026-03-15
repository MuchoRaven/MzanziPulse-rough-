"""
Compliance Helper
Integration with CIPC, SARS, and other SA regulatory bodies
"""

import os
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()


class ComplianceHelper:
    """
    Handle compliance checks and registrations
    Integrates with South African regulatory APIs
    """
    
    def __init__(self):
        """Initialize compliance helper"""
        
        # API Keys (from environment)
        self.cipc_api_key = os.environ.get('CIPC_API_KEY')
        self.sars_api_key = os.environ.get('SARS_API_KEY')
        
        # API Endpoints
        self.cipc_base_url = "https://api.cipc.co.za/v1"  # Mock endpoint
        self.sars_base_url = "https://api.sars.gov.za/v1"  # Mock endpoint
        
        # Note: Real CIPC/SARS APIs require official partnerships
        # This implementation provides the structure for when APIs are available
        
        print("✅ Compliance Helper initialized")
    
    # ═══════════════════════════════════════════════════════════════════
    # CIPC REGISTRATION
    # ═══════════════════════════════════════════════════════════════════
    
    def check_cipc_status(self, registration_number: Optional[str] = None, 
                          business_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Check CIPC registration status
        
        Args:
            registration_number: CIPC registration number (e.g., 2023/123456/07)
            business_name: Business name to search
            
        Returns:
            dict: Registration status and details
        """
        
        if not self.cipc_api_key:
            # Return mock data if no API key
            return self._mock_cipc_status(registration_number, business_name)
        
        try:
            # Real API call structure (when available)
            headers = {
                'Authorization': f'Bearer {self.cipc_api_key}',
                'Content-Type': 'application/json'
            }
            
            params = {}
            if registration_number:
                params['registration_number'] = registration_number
            if business_name:
                params['business_name'] = business_name
            
            response = requests.get(
                f"{self.cipc_base_url}/company/search",
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'registered': data.get('registered', False),
                    'registrationNumber': data.get('registration_number'),
                    'entityType': data.get('entity_type'),
                    'status': data.get('status'),
                    'registrationDate': data.get('registration_date'),
                    'directors': data.get('directors', []),
                    'annualReturnDue': data.get('annual_return_due_date')
                }
            else:
                return {
                    'success': False,
                    'error': f'CIPC API error: {response.status_code}'
                }
                
        except Exception as e:
            print(f"❌ CIPC check error: {e}")
            return self._mock_cipc_status(registration_number, business_name)
    
    def _mock_cipc_status(self, registration_number: Optional[str], 
                          business_name: Optional[str]) -> Dict[str, Any]:
        """Mock CIPC status for testing"""
        return {
            'success': True,
            'registered': False,
            'registrationNumber': None,
            'entityType': None,
            'status': 'NOT_REGISTERED',
            'message': 'Business not registered with CIPC',
            'nextSteps': [
                'Choose entity type (PTY Ltd, CC, Sole Proprietor)',
                'Check name availability',
                'Prepare registration documents',
                'Submit online application',
                'Pay registration fee (R175 - R500)'
            ]
        }
    
    def initiate_cipc_registration(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Initiate CIPC registration process
        
        Args:
            business_data: {
                'businessName': str,
                'entityType': 'PTY_LTD' | 'CC' | 'SOLE_PROPRIETOR',
                'directors': [{'name': str, 'idNumber': str}],
                'physicalAddress': str,
                'postalAddress': str,
                'mainActivity': str
            }
            
        Returns:
            dict: Registration initiation status
        """
        
        # Validate required fields
        required = ['businessName', 'entityType', 'directors', 'physicalAddress']
        for field in required:
            if field not in business_data:
                return {
                    'success': False,
                    'error': f'Missing required field: {field}'
                }
        
        # Check name availability first
        name_check = self.check_name_availability(business_data['businessName'])
        
        if not name_check['available']:
            return {
                'success': False,
                'error': 'Business name not available',
                'suggestions': name_check.get('suggestions', [])
            }
        
        # In production, this would submit to CIPC API
        # For now, return mock registration process
        
        return {
            'success': True,
            'message': 'Registration initiated',
            'referenceNumber': f"CIPC-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'estimatedCompletionDays': 5,
            'steps': [
                {'step': 1, 'description': 'Name reservation', 'status': 'PENDING'},
                {'step': 2, 'description': 'Document submission', 'status': 'PENDING'},
                {'step': 3, 'description': 'Fee payment', 'status': 'PENDING'},
                {'step': 4, 'description': 'Registration review', 'status': 'PENDING'},
                {'step': 5, 'description': 'Certificate issuance', 'status': 'PENDING'}
            ],
            'fee': self._calculate_cipc_fee(business_data['entityType']),
            'paymentInstructions': 'Pay online via CIPC portal or EFT'
        }
    
    def check_name_availability(self, business_name: str) -> Dict[str, Any]:
        """Check if business name is available"""
        
        # In production, would check against CIPC database
        # For now, return mock availability
        
        # Simple validation
        if len(business_name) < 3:
            return {
                'available': False,
                'reason': 'Name too short (minimum 3 characters)',
                'suggestions': []
            }
        
        # Mock: Names with "test" are unavailable
        if 'test' in business_name.lower():
            return {
                'available': False,
                'reason': 'Name already in use',
                'suggestions': [
                    f"{business_name} Enterprises",
                    f"{business_name} Trading",
                    f"{business_name} Solutions"
                ]
            }
        
        return {
            'available': True,
            'message': f'"{business_name}" is available for registration',
            'reservationFee': 50.00,
            'reservationPeriod': '60 days'
        }
    
    def _calculate_cipc_fee(self, entity_type: str) -> float:
        """Calculate CIPC registration fee"""
        fees = {
            'PTY_LTD': 500.00,
            'CC': 175.00,
            'SOLE_PROPRIETOR': 0.00,  # Free registration
            'PARTNERSHIP': 175.00
        }
        return fees.get(entity_type, 500.00)
    
    # ═══════════════════════════════════════════════════════════════════
    # SARS TAX REGISTRATION
    # ═══════════════════════════════════════════════════════════════════
    
    def check_sars_status(self, tax_number: Optional[str] = None,
                         id_number: Optional[str] = None) -> Dict[str, Any]:
        """
        Check SARS tax registration status
        
        Args:
            tax_number: SARS tax reference number
            id_number: SA ID number
            
        Returns:
            dict: Tax status and compliance
        """
        
        if not self.sars_api_key:
            return self._mock_sars_status(tax_number, id_number)
        
        try:
            # Real API call structure
            headers = {
                'Authorization': f'Bearer {self.sars_api_key}',
                'Content-Type': 'application/json'
            }
            
            params = {}
            if tax_number:
                params['tax_number'] = tax_number
            if id_number:
                params['id_number'] = id_number
            
            response = requests.get(
                f"{self.sars_base_url}/taxpayer/status",
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'registered': data.get('registered', False),
                    'taxNumber': data.get('tax_number'),
                    'taxType': data.get('tax_type'),
                    'status': data.get('compliance_status'),
                    'outstandingReturns': data.get('outstanding_returns', []),
                    'taxClearance': {
                        'status': data.get('tax_clearance_status'),
                        'validUntil': data.get('clearance_expiry_date')
                    }
                }
            else:
                return {
                    'success': False,
                    'error': f'SARS API error: {response.status_code}'
                }
                
        except Exception as e:
            print(f"❌ SARS check error: {e}")
            return self._mock_sars_status(tax_number, id_number)
    
    def _mock_sars_status(self, tax_number: Optional[str], 
                          id_number: Optional[str]) -> Dict[str, Any]:
        """Mock SARS status for testing"""
        return {
            'success': True,
            'registered': False,
            'taxNumber': None,
            'status': 'NOT_REGISTERED',
            'message': 'Not registered with SARS',
            'nextSteps': [
                'Register as individual or business',
                'Choose tax types (Income Tax, VAT if turnover > R1M)',
                'Submit eFiling registration',
                'Activate eFiling profile',
                'File first tax return'
            ],
            'requirements': [
                'Valid SA ID or passport',
                'Proof of residential address',
                'Bank account details',
                'CIPC registration (for companies)'
            ]
        }
    
    def initiate_sars_registration(self, taxpayer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Initiate SARS tax registration
        
        Args:
            taxpayer_data: {
                'entityType': 'INDIVIDUAL' | 'COMPANY',
                'idNumber': str,
                'fullName': str,
                'address': str,
                'contactNumber': str,
                'email': str,
                'bankDetails': dict
            }
            
        Returns:
            dict: Registration status
        """
        
        # Validate
        required = ['entityType', 'idNumber', 'fullName', 'email']
        for field in required:
            if field not in taxpayer_data:
                return {
                    'success': False,
                    'error': f'Missing required field: {field}'
                }
        
        # Mock registration
        return {
            'success': True,
            'message': 'Tax registration initiated',
            'referenceNumber': f"SARS-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'efilingRegistration': {
                'username': taxpayer_data['email'],
                'temporaryPassword': 'Will be sent via SMS',
                'activationRequired': True
            },
            'nextSteps': [
                'Check email for eFiling credentials',
                'Activate eFiling profile',
                'Link bank account',
                'File first tax return',
                'Apply for tax clearance certificate'
            ],
            'estimatedCompletionDays': 3
        }
    
    def check_tax_clearance(self, tax_number: str) -> Dict[str, Any]:
        """Check tax clearance certificate status"""
        
        # Mock tax clearance check
        return {
            'success': True,
            'hasClearance': False,
            'status': 'NOT_APPLIED',
            'message': 'No active tax clearance certificate',
            'howToApply': [
                'Ensure all tax returns are up to date',
                'Login to SARS eFiling',
                'Navigate to Tax Clearance section',
                'Complete application form',
                'Wait 2-5 business days for approval'
            ],
            'validity': '12 months from issue date',
            'cost': 'Free'
        }
    
    # ═══════════════════════════════════════════════════════════════════
    # B-BBEE COMPLIANCE
    # ═══════════════════════════════════════════════════════════════════
    
    def get_bbbee_requirements(self, annual_turnover: float) -> Dict[str, Any]:
        """
        Get B-BBEE requirements based on turnover
        
        Args:
            annual_turnover: Annual turnover in Rands
            
        Returns:
            dict: B-BBEE requirements and options
        """
        
        # Determine category
        if annual_turnover <= 10_000_000:
            # Exempted Micro Enterprise (EME)
            return {
                'category': 'EME',
                'level': 'Level 4 (Automatic)',
                'requirements': {
                    'certificate': 'Affidavit (not full certificate)',
                    'cost': 'R500 - R2,000',
                    'validity': '12 months',
                    'verification': 'Self-declaration with accountant sign-off'
                },
                'benefits': [
                    'Automatic Level 4 B-BBEE status',
                    '100% procurement recognition',
                    'Cheaper than full verification',
                    'Simpler process'
                ],
                'process': [
                    'Prepare EME affidavit',
                    'Get accountant to sign',
                    'Submit to clients when required'
                ]
            }
        elif annual_turnover <= 50_000_000:
            # Qualifying Small Enterprise (QSE)
            return {
                'category': 'QSE',
                'level': 'Depends on scorecard',
                'requirements': {
                    'certificate': 'QSE Certificate (simplified scorecard)',
                    'cost': 'R5,000 - R15,000',
                    'validity': '12 months',
                    'verification': 'SANAS accredited agency'
                },
                'benefits': [
                    'Measured on 4 elements (not 5)',
                    'Lower targets than large companies',
                    'Can achieve Level 1-4',
                    'Better tenders opportunities'
                ],
                'process': [
                    'Choose verification agency',
                    'Prepare documentation',
                    'Complete scorecard assessment',
                    'Receive certificate'
                ]
            }
        else:
            # Generic Enterprise
            return {
                'category': 'GENERIC',
                'level': 'Depends on scorecard',
                'requirements': {
                    'certificate': 'Full B-BBEE Certificate',
                    'cost': 'R15,000 - R50,000+',
                    'validity': '12 months',
                    'verification': 'SANAS accredited agency'
                },
                'benefits': [
                    'Full B-BBEE compliance',
                    'Can achieve Level 1-8',
                    'Required for large tenders',
                    'Competitive advantage'
                ],
                'process': [
                    'Choose verification agency',
                    'Prepare comprehensive documentation',
                    'Complete full scorecard',
                    'Receive certificate'
                ]
            }
    
    # ═══════════════════════════════════════════════════════════════════
    # POPIA COMPLIANCE
    # ═══════════════════════════════════════════════════════════════════
    
    def get_popia_requirements(self) -> Dict[str, Any]:
        """Get POPIA compliance requirements"""
        
        return {
            'category': 'SMALL_BUSINESS',
            'requirements': [
                'Privacy Policy document',
                'Customer consent forms',
                'Data processing agreements',
                'Information officer appointed',
                'Data breach procedures'
            ],
            'templates': {
                'privacyPolicy': '/templates/popia_privacy_policy.docx',
                'consentForm': '/templates/popia_consent_form.pdf',
                'breachProcedure': '/templates/data_breach_procedure.pdf'
            },
            'cost': 'R0 - R5,000 (DIY vs legal)',
            'steps': [
                'Download templates',
                'Customize for your business',
                'Implement consent collection',
                'Train staff on POPIA',
                'Review annually'
            ],
            'penalties': 'Up to R10M or 10 years imprisonment for non-compliance'
        }
    
    # ═══════════════════════════════════════════════════════════════════
    # COMPREHENSIVE STATUS CHECK
    # ═══════════════════════════════════════════════════════════════════
    
    def get_comprehensive_status(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get comprehensive compliance status across all requirements
        
        Args:
            business_data: Business and owner information
            
        Returns:
            dict: Complete compliance picture
        """
        
        cipc_status = self.check_cipc_status(
            registration_number=business_data.get('cipcNumber'),
            business_name=business_data.get('businessName')
        )
        
        sars_status = self.check_sars_status(
            tax_number=business_data.get('taxNumber'),
            id_number=business_data.get('ownerIdNumber')
        )
        
        bbbee_reqs = self.get_bbbee_requirements(
            annual_turnover=business_data.get('annualTurnover', 0)
        )
        
        popia_reqs = self.get_popia_requirements()
        
        # Calculate overall compliance score
        score = 0
        max_score = 100
        
        if cipc_status.get('registered'):
            score += 30
        if sars_status.get('registered'):
            score += 30
        if business_data.get('hasBBBEE'):
            score += 20
        if business_data.get('hasPOPIA'):
            score += 20
        
        # Determine readiness level
        if score < 25:
            readiness = 'INFORMAL'
        elif score < 50:
            readiness = 'PARTIALLY_FORMAL'
        elif score < 75:
            readiness = 'FORMAL'
        else:
            readiness = 'INVESTOR_READY'
        
        return {
            'overallScore': score,
            'readinessLevel': readiness,
            'cipc': cipc_status,
            'sars': sars_status,
            'bbbee': bbbee_reqs,
            'popia': popia_reqs,
            'priorityActions': self._get_priority_actions(cipc_status, sars_status, score),
            'estimatedCostToComply': self._estimate_compliance_costs(cipc_status, sars_status, bbbee_reqs),
            'estimatedTimeToComply': '2-4 weeks'
        }
    
    def _get_priority_actions(self, cipc_status: dict, sars_status: dict, score: int) -> list:
        """Get prioritized list of actions"""
        actions = []
        
        if not cipc_status.get('registered'):
            actions.append({
                'priority': 'HIGH',
                'action': 'Register with CIPC',
                'reason': 'Required for formal business operations'
            })
        
        if not sars_status.get('registered'):
            actions.append({
                'priority': 'HIGH',
                'action': 'Register for tax',
                'reason': 'Legal requirement for all businesses'
            })
        
        if score < 50:
            actions.append({
                'priority': 'MEDIUM',
                'action': 'Get B-BBEE affidavit',
                'reason': 'Unlocks tender opportunities'
            })
        
        actions.append({
            'priority': 'MEDIUM',
            'action': 'Implement POPIA compliance',
            'reason': 'Legal requirement for customer data'
        })
        
        return actions
    
    def _estimate_compliance_costs(self, cipc_status: dict, sars_status: dict, bbbee_reqs: dict) -> Dict[str, float]:
        """Estimate total costs to achieve compliance"""
        costs = {
            'cipc': 0,
            'sars': 0,
            'bbbee': 0,
            'popia': 0,
            'total': 0
        }
        
        if not cipc_status.get('registered'):
            costs['cipc'] = 500.00
        
        # SARS is free
        costs['sars'] = 0
        
        # B-BBEE depends on category
        bbbee_cost_str = bbbee_reqs['requirements']['cost']
        if 'R500' in bbbee_cost_str:
            costs['bbbee'] = 1500.00  # Average
        
        # POPIA (DIY)
        costs['popia'] = 0
        
        costs['total'] = sum([costs['cipc'], costs['sars'], costs['bbbee'], costs['popia']])
        
        return costs


# ════════════════════════════════════════════════════════════════════════════
# TEST FUNCTION
# ════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    """Test compliance helper"""
    
    print("=" * 80)
    print("🏛️  Testing Compliance Helper")
    print("=" * 80)
    
    helper = ComplianceHelper()
    
    # Test business data
    test_business = {
        'businessName': 'Mama Thandi Spaza Shop',
        'ownerIdNumber': '8001015800080',
        'annualTurnover': 150000.00,
        'hasBBBEE': False,
        'hasPOPIA': False
    }
    
    # Check comprehensive status
    print("\n📊 Comprehensive Compliance Check:")
    status = helper.get_comprehensive_status(test_business)
    
    print(f"\n✅ Overall Score: {status['overallScore']}/100")
    print(f"📈 Readiness Level: {status['readinessLevel']}")
    print(f"💰 Estimated Cost to Comply: R{status['estimatedCostToComply']['total']:,.2f}")
    print(f"⏱️  Estimated Time: {status['estimatedTimeToComply']}")
    
    print("\n🎯 Priority Actions:")
    for action in status['priorityActions']:
        print(f"   {action['priority']:8s} - {action['action']}")
    
    print("\n" + "=" * 80)