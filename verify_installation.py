#!/usr/bin/env python3
"""
Smart Park System - Installation Verification Script
Verifies that all components are properly installed and configured
"""

import sys
from pathlib import Path

def check_python_version():
    """Check if Python version is adequate"""
    print("🔍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"  ✅ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"  ❌ Python {version.major}.{version.minor}.{version.micro} (Requires 3.8+)")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    print("\n🔍 Checking dependencies...")
    
    required_packages = [
        ('streamlit', 'Streamlit'),
        ('pandas', 'Pandas'),
        ('plotly', 'Plotly'),
    ]
    
    missing = []
    installed = []
    
    for package, name in required_packages:
        try:
            __import__(package)
            installed.append(name)
            print(f"  ✅ {name} installed")
        except ImportError:
            missing.append(name)
            print(f"  ❌ {name} not found")
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print("   Install with: pip install -r reqiuirements.txt")
        return False
    else:
        print(f"\n✅ All dependencies installed")
        return True

def check_project_files():
    """Check if all project files exist"""
    print("\n🔍 Checking project files...")
    
    required_files = [
        ('smart_park.py', 'Main application'),
        ('test_smart_park.py', 'Test suite'),
        ('generate_demo_data.py', 'Demo data generator'),
        ('start_smart_park.sh', 'Quick start script'),
        ('SMART_PARK_README.md', 'Technical documentation'),
        ('USER_GUIDE.md', 'User guide'),
        ('FEATURE_SHOWCASE.md', 'Feature showcase'),
        ('reqiuirements.txt', 'Dependencies'),
    ]
    
    project_dir = Path(__file__).parent
    missing = []
    found = []
    
    for filename, description in required_files:
        filepath = project_dir / filename
        if filepath.exists():
            found.append(filename)
            print(f"  ✅ {filename} - {description}")
        else:
            missing.append(filename)
            print(f"  ❌ {filename} - {description} (MISSING)")
    
    if missing:
        print(f"\n❌ Missing files: {', '.join(missing)}")
        return False
    else:
        print(f"\n✅ All project files present")
        return True

def check_syntax():
    """Check Python syntax of main files"""
    print("\n🔍 Checking Python syntax...")
    
    project_dir = Path(__file__).parent
    python_files = [
        'smart_park.py',
        'test_smart_park.py',
        'generate_demo_data.py'
    ]
    
    errors = []
    
    for filename in python_files:
        filepath = project_dir / filename
        try:
            with open(filepath, 'r') as f:
                compile(f.read(), filename, 'exec')
            print(f"  ✅ {filename} syntax OK")
        except SyntaxError as e:
            errors.append(f"{filename}: {e}")
            print(f"  ❌ {filename} has syntax errors")
    
    if errors:
        print("\n❌ Syntax errors found:")
        for error in errors:
            print(f"   {error}")
        return False
    else:
        print(f"\n✅ All Python files have valid syntax")
        return True

def verify_imports():
    """Test importing the main module"""
    print("\n🔍 Testing module imports...")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        import smart_park
        print("  ✅ smart_park module imported successfully")
        
        # Check if key functions exist
        required_functions = [
            'init_database',
            'load_database',
            'save_database',
            'get_parking_statistics',
            'main'
        ]
        
        for func_name in required_functions:
            if hasattr(smart_park, func_name):
                print(f"  ✅ Function '{func_name}' found")
            else:
                print(f"  ❌ Function '{func_name}' not found")
                return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        return False

def run_verification():
    """Run all verification checks"""
    print("=" * 60)
    print("🅿️  Smart Park System - Installation Verification")
    print("=" * 60)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Project Files", check_project_files),
        ("Python Syntax", check_syntax),
        ("Module Imports", verify_imports),
    ]
    
    results = {}
    
    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"\n❌ {check_name} check failed with error: {e}")
            results[check_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Verification Summary")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for check_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {check_name}")
    
    print("=" * 60)
    print(f"Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n✅ Installation verification PASSED!")
        print("\n🚀 You can now start the application:")
        print("   streamlit run smart_park.py")
        print("\nor use the quick start script:")
        print("   ./start_smart_park.sh")
        return 0
    else:
        print("\n❌ Installation verification FAILED!")
        print("\nPlease fix the issues above and run this script again.")
        return 1

if __name__ == "__main__":
    exit_code = run_verification()
    sys.exit(exit_code)
