import sys
import os

# Add backend folder to path so imports work on Vercel
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app import app

# Export the app for Vercel
handler = app
