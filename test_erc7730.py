#!/usr/bin/env python3
"""Test script for erc7730 package"""

import sys

def test_erc7730_import():
    """Test if erc7730 package can be imported"""
    try:
        import erc7730
        print(f"✅ Successfully imported erc7730 package")
        return True
    except ImportError as e:
        print(f"❌ Failed to import erc7730 package: {e}")
        return False

def test_erc7730_model():
    """Test if erc7730.model module can be imported"""
    try:
        import erc7730.model
        from erc7730.model import input
        print(f"✅ Successfully imported erc7730.model module")
        return True
    except ImportError as e:
        print(f"❌ Failed to import erc7730.model module: {e}")
        return False

def test_erc7730_generate():
    """Test if erc7730.generate module can be imported"""
    try:
        import erc7730.generate
        print(f"✅ Successfully imported erc7730.generate module")
        
        # Check if the generate_descriptor function is available
        try:
            from erc7730.generate.generate import generate_descriptor
            print(f"✅ Successfully imported generate_descriptor function")
            return True
        except ImportError as e:
            print(f"❌ Failed to import generate_descriptor function: {e}")
            return False
    except ImportError as e:
        print(f"❌ Failed to import erc7730.generate module: {e}")
        return False

if __name__ == "__main__":
    print("Testing erc7730 package...")
    
    import_success = test_erc7730_import()
    model_success = test_erc7730_model() if import_success else False
    generate_success = test_erc7730_generate() if import_success else False
    
    if import_success and model_success and generate_success:
        print("All tests passed! ✅")
        print("The erc7730 package is correctly installed and can be used in the API.")
        sys.exit(0)
    else:
        print("Tests failed! ❌")
        sys.exit(1) 