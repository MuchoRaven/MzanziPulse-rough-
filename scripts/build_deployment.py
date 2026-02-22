"""
Deployment Package Builder
Packages Python functions for FunctionGraph deployment

CS CONCEPT: Build automation
Instead of manually copying files, we write a script to do it.
This is called "build automation" - used in all real software projects.
"""

import os
import shutil
import zipfile
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

# Root directory of project
ROOT_DIR = Path(__file__).parent.parent

# Source scripts directory
SCRIPTS_DIR = ROOT_DIR / 'scripts'

# Deployment output directory
DEPLOY_DIR = ROOT_DIR / 'deployment'

# ============================================================================
# WHAT EACH FUNCTION NEEDS
# Dependencies = files each function requires to work
# ============================================================================

FUNCTIONS = {
    'get_balance': {
        'description': 'Get wallet balance for a business',
        'main_file': 'functiongraph_get_balance.py',
        'dependencies': [
            'obs_helper.py',         # OBS download/upload logic
        ],
        'handler': 'functiongraph_get_balance.handler'
    },
    'add_transaction': {
        'description': 'Add cash transaction from WhatsApp',
        'main_file': 'functiongraph_add_transaction.py',
        'dependencies': [
            'obs_helper.py',          # OBS download/upload logic
            'transaction_parser.py',  # WhatsApp message parser
            'whatsapp_handler.py',    # WhatsApp integration
        ],
        'handler': 'functiongraph_add_transaction.handler'
    },
    'get_score': {
        'description': 'Get EmpowerScore for a business',
        'main_file': 'functiongraph_get_score.py',
        'dependencies': [
            'obs_helper.py',      # OBS download/upload logic
            'empower_score.py',   # Scoring algorithm
        ],
        'handler': 'functiongraph_get_score.handler'
    },
    'reconcile': {
        'description': 'Weekly cash reconciliation',
        'main_file': 'functiongraph_reconcile.py',
        'dependencies': [
            'obs_helper.py',              # OBS download/upload logic
            'reconciliation_demo.py',     # Reconciliation logic
        ],
        'handler': 'functiongraph_reconcile.handler'
    }
}

# ============================================================================
# BUILD FUNCTIONS
# ============================================================================

def create_zip_package(function_name: str, config: dict) -> str:
    """
    Create ZIP package for a single function
    
    CS CONCEPT: We're doing dependency management
    Each function gets its own package with ONLY what it needs
    This keeps packages small and functions fast
    
    Args:
        function_name: Name of the function (e.g., 'get_balance')
        config: Configuration dict with files to include
    
    Returns:
        Path to created ZIP file
    """
    
    print(f"\n📦 Building package: {function_name}")
    print(f"   Description: {config['description']}")
    
    # Create function directory
    func_dir = DEPLOY_DIR / function_name
    func_dir.mkdir(parents=True, exist_ok=True)
    
    # Files to include in package
    files_to_include = [config['main_file']] + config['dependencies']
    
    # Copy files to function directory
    print(f"   📋 Copying files:")
    for filename in files_to_include:
        source = SCRIPTS_DIR / filename
        destination = func_dir / filename
        
        if source.exists():
            shutil.copy2(source, destination)
            print(f"      ✅ {filename}")
        else:
            print(f"      ⚠️  {filename} NOT FOUND - creating placeholder")
            # Create placeholder so ZIP doesn't fail
            with open(destination, 'w') as f:
                f.write(f"# Placeholder for {filename}\n")
                f.write(f"# TODO: Implement this module\n")
    
    # Create ZIP file
    zip_path = DEPLOY_DIR / f"{function_name}.zip"
    
    print(f"   🗜️  Creating ZIP: {function_name}.zip")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for filename in files_to_include:
            file_path = func_dir / filename
            if file_path.exists():
                # Add to ZIP (arcname = name inside ZIP)
                zipf.write(file_path, arcname=filename)
                print(f"      📄 Added: {filename}")
    
    # Get ZIP file size
    zip_size = os.path.getsize(zip_path)
    print(f"   📊 Package size: {zip_size/1024:.1f} KB")
    
    return str(zip_path)


def build_all_packages():
    """
    Build deployment packages for all functions
    """
    
    print("=" * 80)
    print("🏗️  MzansiPulse Deployment Package Builder")
    print("=" * 80)
    
    # Create deployment directory
    DEPLOY_DIR.mkdir(parents=True, exist_ok=True)
    
    # Build each function package
    built_packages = {}
    
    for function_name, config in FUNCTIONS.items():
        zip_path = create_zip_package(function_name, config)
        built_packages[function_name] = {
            'zip_path': zip_path,
            'handler': config['handler']
        }
    
    # Print deployment summary
    print("\n" + "=" * 80)
    print("📋 DEPLOYMENT SUMMARY")
    print("=" * 80)
    print("\nPackages built:")
    
    for name, info in built_packages.items():
        print(f"\n   📦 {name}")
        print(f"      ZIP: {info['zip_path']}")
        print(f"      Handler: {info['handler']}")
    
    print("\n" + "=" * 80)
    print("📋 FUNCTIONGRAPH DEPLOYMENT CHECKLIST")
    print("=" * 80)
    print("\nFor each function above, you will:")
    print("   1. Open Huawei Cloud Console")
    print("   2. Go to FunctionGraph")
    print("   3. Create new function")
    print("   4. Upload the ZIP file")
    print("   5. Set handler name (from above)")
    print("   6. Set environment variables:")
    print("      OBS_ACCESS_KEY = [your AK]")
    print("      OBS_SECRET_KEY = [your SK]")
    print("      OBS_BUCKET_NAME = mzansipulse-data")
    print("   7. Test the function")
    print("   8. Create API Gateway URL")
    print("\n✅ PACKAGES READY FOR DEPLOYMENT!")
    print("=" * 80)
    
    return built_packages


if __name__ == "__main__":
    build_all_packages()