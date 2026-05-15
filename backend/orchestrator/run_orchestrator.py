#!/usr/bin/env python3
"""
Wrapper script to run the orchestrator with proper Python path setup
"""
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Now import and run the main module
if __name__ == "__main__":
    import main_simple
    # Run the FastAPI app if it exists
    if hasattr(main_simple, 'app'):
        import uvicorn
        uvicorn.run(main_simple.app, host="0.0.0.0", port=8000)
    else:
        print("No FastAPI app found in main_simple.py")
        # Try to run main directly if it has a main function
        if hasattr(main_simple, 'main'):
            main_simple.main()