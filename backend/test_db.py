#!/usr/bin/env python3
import psycopg2

try:
    # Try without password first (for trust authentication)
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="sports_analytics",
            user="postgres"
        )
    except:
        # Fallback to password authentication
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="sports_analytics",
            user="postgres",
            password="password123"
        )
    print("✅ Direct connection successful!")
    
    cur = conn.cursor()
    cur.execute("SELECT version();")
    version = cur.fetchone()
    print(f"PostgreSQL version: {version[0]}")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Connection failed: {e}")