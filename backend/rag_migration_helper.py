#!/usr/bin/env python
"""
RAG LLM Integration Migration Helper

This script helps you set up the database for RAG LLM integration.
It provides options to:
1. Create migration
2. Apply migration
3. Rollback migration
4. Verify schema
"""

import os
import sys
import subprocess
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import inspect, create_engine
from app.core.config import settings


def run_command(cmd, description=""):
    """Run a shell command and return success status"""
    print(f"\n{'='*60}")
    if description:
        print(f"📋 {description}")
    print(f"🔧 Running: {' '.join(cmd)}")
    print('='*60)
    
    try:
        result = subprocess.run(cmd, cwd=str(PROJECT_ROOT), check=True)
        print(f"✅ Success: {description}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {description}")
        print(f"Exit code: {e.returncode}")
        return False


def check_schema():
    """Check if LLM columns exist in database"""
    print("\n" + "="*60)
    print("🔍 Checking Database Schema")
    print("="*60)
    
    try:
        engine = create_engine(settings.DATABASE_URL)
        inspector = inspect(engine)
        
        # Get columns from hospital_predictions table
        columns = [col['name'] for col in inspector.get_columns('hospital_predictions')]
        
        print(f"\n📊 Current columns in hospital_predictions:")
        for col in sorted(columns):
            print(f"   - {col}")
        
        # Check for LLM columns
        llm_columns = ['llm_confidence', 'llm_assumptions', 'llm_risk_flags']
        missing = [col for col in llm_columns if col not in columns]
        
        if missing:
            print(f"\n⚠️  Missing LLM columns: {', '.join(missing)}")
            print("   You need to run migrations to add these columns")
            return False
        else:
            print(f"\n✅ All LLM columns exist in database")
            return True
            
    except Exception as e:
        print(f"\n❌ Error connecting to database: {e}")
        return False


def main():
    """Main migration helper"""
    
    print("""
╔════════════════════════════════════════════════════════════╗
║   RAG LLM Integration - Database Migration Helper          ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    if len(sys.argv) < 2:
        print("""
Usage: python rag_migration_helper.py <command>

Commands:
  check      - Check current database schema
  upgrade    - Apply RAG LLM migration
  downgrade  - Rollback RAG LLM migration
  create     - Create new migration
  
Examples:
  python rag_migration_helper.py check
  python rag_migration_helper.py upgrade
  python rag_migration_helper.py downgrade
        """)
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "check":
        success = check_schema()
        sys.exit(0 if success else 1)
    
    elif command == "upgrade":
        print("\n🚀 Upgrading database schema for RAG LLM...")
        check_schema()
        
        success = run_command(
            ["alembic", "upgrade", "rag_llm_001"],
            "Apply RAG LLM migration"
        )
        
        if success:
            check_schema()
        sys.exit(0 if success else 1)
    
    elif command == "downgrade":
        print("\n⬅️  Rolling back RAG LLM migration...")
        
        success = run_command(
            ["alembic", "downgrade", "-1"],
            "Rollback migration"
        )
        
        if success:
            check_schema()
        sys.exit(0 if success else 1)
    
    elif command == "create":
        if len(sys.argv) < 3:
            print("Usage: python rag_migration_helper.py create <message>")
            sys.exit(1)
        
        message = " ".join(sys.argv[2:])
        print(f"\n📝 Creating migration: {message}")
        
        success = run_command(
            ["alembic", "revision", "--autogenerate", "-m", message],
            f"Create migration: {message}"
        )
        sys.exit(0 if success else 1)
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Use 'check', 'upgrade', 'downgrade', or 'create'")
        sys.exit(1)


if __name__ == "__main__":
    main()
