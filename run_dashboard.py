#!/usr/bin/env python3
"""
ModoAI News Dashboard Runner
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """Run the dashboard"""
    print("🚀 Starting ModoAI News Dashboard...")
    print("📊 Dashboard will be available at: http://localhost:5001")
    print("🔄 Press Ctrl+C to stop the server")
    print()
    
    try:
        from dashboard.app import app
        app.run(debug=True, host='0.0.0.0', port=5001)
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped.")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        print("💡 Make sure you have installed all requirements: pip install -r requirements.txt")

if __name__ == "__main__":
    main() 