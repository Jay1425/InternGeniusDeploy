#!/usr/bin/env python3
"""
InternGenius Flask Application Runner

This script starts the InternGenius Flask application with proper configuration.
"""

import os
import sys
from app import create_app

def main():
    """Main function to run the Flask application."""
    
    # Set environment if not already set
    if not os.environ.get('FLASK_ENV'):
        os.environ['FLASK_ENV'] = 'development'
    
    # Create Flask app
    app = create_app()
    
    # Get configuration from environment
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    print("🎓 Starting InternGenius Application...")
    print(f"🌐 Running on: http://{host}:{port}")
    print(f"🔧 Environment: {os.environ.get('FLASK_ENV')}")
    print(f"🐛 Debug Mode: {debug}")
    print("\n📋 Available URLs:")
    print(f"   • Home: http://{host}:{port}/")
    print(f"   • Login: http://{host}:{port}/auth/login")
    print(f"   • Sign Up: http://{host}:{port}/auth/signup")
    print("\n🚀 Press Ctrl+C to stop the server\n")
    
    try:
        # Run the Flask application
        app.run(
            host=host,
            port=port,
            debug=debug,
            use_reloader=debug
        )
    except KeyboardInterrupt:
        print("\n👋 InternGenius application stopped.")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
