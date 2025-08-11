#!/usr/bin/env python3
"""
Test script to verify deduplication features work correctly.
"""

import sqlite3
import requests
import json
import os
from datetime import datetime

def test_database_deduplication():
    """Test that database has no duplicates."""
    print("🔍 Testing Database Deduplication...")
    
    db_path = os.getenv('DATABASE_PATH', 'signals_agent.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check for duplicates by name
    cursor.execute("""
        SELECT name, COUNT(*) as count 
        FROM signal_segments 
        GROUP BY name 
        HAVING count > 1
    """)
    
    duplicates = cursor.fetchall()
    
    if duplicates:
        print("❌ Found duplicates in database:")
        for name, count in duplicates:
            print(f"   - {name}: {count} occurrences")
        return False
    else:
        print("✅ No duplicates found in database")
    
    # Check total vs unique counts
    cursor.execute("SELECT COUNT(*) FROM signal_segments")
    total_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT name) FROM signal_segments")
    unique_count = cursor.fetchone()[0]
    
    print(f"📊 Total signals: {total_count}")
    print(f"📊 Unique signal names: {unique_count}")
    
    if total_count == unique_count:
        print("✅ Database deduplication: PASSED")
        conn.close()
        return True
    else:
        print("❌ Database deduplication: FAILED")
        conn.close()
        return False

def test_api_deduplication():
    """Test that API returns unique signals."""
    print("\n🔍 Testing API Deduplication...")
    
    api_base = "http://127.0.0.1:8000"
    
    # Test multiple queries
    test_queries = [
        "luxury cars",
        "health and fitness", 
        "technology enthusiasts",
        "travel planning"
    ]
    
    all_passed = True
    
    for query in test_queries:
        print(f"\n   Testing query: '{query}'")
        
        try:
            response = requests.post(
                f"{api_base}/discovery",
                headers={"Content-Type": "application/json"},
                json={"query": query, "limit": 10},
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"   ❌ API request failed: {response.status_code}")
                all_passed = False
                continue
            
            data = response.json()
            matches = data.get('matches', [])
            
            # Check for duplicate names
            names = [match['name'] for match in matches]
            unique_names = list(set(names))
            
            if len(names) == len(unique_names):
                print(f"   ✅ Query '{query}': {len(matches)} unique signals")
            else:
                print(f"   ❌ Query '{query}': Found duplicates!")
                print(f"      Total: {len(names)}, Unique: {len(unique_names)}")
                all_passed = False
                
                # Show duplicates
                from collections import Counter
                name_counts = Counter(names)
                for name, count in name_counts.items():
                    if count > 1:
                        print(f"      - {name}: {count} times")
            
        except Exception as e:
            print(f"   ❌ Error testing query '{query}': {e}")
            all_passed = False
    
    if all_passed:
        print("\n✅ API deduplication: PASSED")
    else:
        print("\n❌ API deduplication: FAILED")
    
    return all_passed

def test_constraint_enforcement():
    """Test that database constraints prevent duplicates."""
    print("\n🔍 Testing Constraint Enforcement...")
    
    db_path = os.getenv('DATABASE_PATH', 'signals_agent.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Try to insert a duplicate name
    test_name = "TEST_DUPLICATE_CONSTRAINT"
    
    try:
        # Insert first record
        cursor.execute("""
            INSERT INTO signal_segments 
            (id, name, description, data_provider, coverage_percentage, 
             signal_type, catalog_access, base_cpm, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            f"test_{datetime.now().timestamp()}_1",
            test_name,
            "Test description",
            "TestProvider",
            10.0,
            "audience",
            "public",
            5.0,
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        conn.commit()
        print(f"   ✅ Inserted first record with name: {test_name}")
        
        # Try to insert duplicate name
        cursor.execute("""
            INSERT INTO signal_segments 
            (id, name, description, data_provider, coverage_percentage, 
             signal_type, catalog_access, base_cpm, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            f"test_{datetime.now().timestamp()}_2",
            test_name,
            "Test description 2",
            "TestProvider2",
            15.0,
            "audience",
            "public",
            7.0,
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        conn.commit()
        print("   ❌ Constraint failed: Duplicate name was inserted")
        
        # Clean up
        cursor.execute("DELETE FROM signal_segments WHERE name = ?", (test_name,))
        conn.commit()
        conn.close()
        return False
        
    except sqlite3.IntegrityError as e:
        print(f"   ✅ Constraint working: {e}")
        
        # Clean up
        cursor.execute("DELETE FROM signal_segments WHERE name = ?", (test_name,))
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        conn.close()
        return False

def test_consistency_across_queries():
    """Test that the same query returns consistent results."""
    print("\n🔍 Testing Consistency Across Queries...")
    
    api_base = "http://127.0.0.1:8000"
    query = "luxury automotive"
    
    try:
        # Run the same query multiple times
        results = []
        for i in range(3):
            response = requests.post(
                f"{api_base}/discovery",
                headers={"Content-Type": "application/json"},
                json={"query": query, "limit": 5},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                matches = data.get('matches', [])
                names = [match['name'] for match in matches]
                results.append(set(names))
                print(f"   Query {i+1}: {len(matches)} signals")
            else:
                print(f"   ❌ Query {i+1} failed: {response.status_code}")
                return False
        
        # Check if all results are the same
        if len(set.intersection(*results)) == len(results[0]):
            print("   ✅ All queries returned the same unique signals")
            return True
        else:
            print("   ❌ Queries returned different results")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing consistency: {e}")
        return False

def main():
    """Run all deduplication tests."""
    print("🧪 Deduplication Feature Test Suite")
    print("=" * 50)
    
    tests = [
        ("Database Deduplication", test_database_deduplication),
        ("API Deduplication", test_api_deduplication),
        ("Constraint Enforcement", test_constraint_enforcement),
        ("Consistency Across Queries", test_consistency_across_queries)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print(f"\n🎉 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎊 All deduplication features working correctly!")
    else:
        print("⚠️  Some deduplication features need attention")

if __name__ == "__main__":
    main()
