#!/usr/bin/env python3
"""Test script for ProposalValidator service."""

import sqlite3
import os
from services.proposal_validator import ProposalValidator
from api_models import Proposal


def create_test_proposals():
    """Create test proposals for validation."""
    return [
        # Valid proposal - all signals exist and share platforms
        Proposal(
            id="proposal_valid_001",
            name="Valid High-Value Package",
            signal_ids=["signal_001", "signal_002"],
            logic="OR",
            platforms=["index-exchange", "the-trade-desk"],  # Will be updated to intersection
            score=0.85,
            reasoning="Valid proposal with existing signals"
        ),
        
        # Invalid proposal - non-existent signal ID
        Proposal(
            id="proposal_invalid_001",
            name="Invalid Signal Package",
            signal_ids=["signal_001", "non_existent_signal"],
            logic="OR",
            platforms=["index-exchange"],
            score=0.75,
            reasoning="Invalid proposal with non-existent signal"
        ),
        
        # Invalid proposal - signals don't share platforms
        Proposal(
            id="proposal_invalid_002",
            name="No Common Platforms",
            signal_ids=["signal_001", "signal_003"],  # These have different platform sets
            logic="OR",
            platforms=["index-exchange"],
            score=0.70,
            reasoning="Invalid proposal with no common platforms"
        ),
        
        # Invalid proposal - AND logic (forbidden) - we'll test this differently
        # since Pydantic model validation prevents creation
        # Proposal(
        #     id="proposal_invalid_003",
        #     name="AND Logic Proposal",
        #     signal_ids=["signal_001"],
        #     logic="AND",  # This should be rejected
        #     platforms=["index-exchange"],
        #     score=0.80,
        #     reasoning="Invalid proposal with AND logic"
        # ),
        
        # Valid proposal - single signal
        Proposal(
            id="proposal_valid_002",
            name="Single Signal Package",
            signal_ids=["signal_001"],
            logic="OR",
            platforms=["dv360", "tradedesk", "amazon"],
            score=0.90,
            reasoning="Valid single signal proposal"
        )
    ]


def test_proposal_validator():
    """Test the ProposalValidator with various scenarios."""
    print("=== Testing ProposalValidator ===")
    
    # Ensure database is initialized
    if not os.path.exists('signals_agent.db'):
        print("Database not found. Please run 'python init_db.py' first.")
        return
    
    # Connect to database
    db_connection = sqlite3.connect('signals_agent.db')
    
    try:
        # Create validator with debug mode
        validator = ProposalValidator(db_connection, debug_mode=True)
        
        # Create test proposals
        test_proposals = create_test_proposals()
        print(f"Created {len(test_proposals)} test proposals")
        
        # Add a test for AND logic validation by creating a proposal and modifying it
        and_logic_proposal = Proposal(
            id="proposal_invalid_003",
            name="AND Logic Proposal",
            signal_ids=["signal_001"],
            logic="OR",  # Start with OR to pass Pydantic validation
            platforms=["index-exchange"],
            score=0.80,
            reasoning="Invalid proposal with AND logic"
        )
        # Modify the logic after creation to test our validator
        and_logic_proposal.logic = "AND"
        test_proposals.append(and_logic_proposal)
        print(f"Added AND logic test proposal - total: {len(test_proposals)}")
        
        # Validate proposals
        print("\n--- Validating Proposals ---")
        valid_proposals, invalid_proposals, report = validator.validate(test_proposals)
        
        # Display results
        print(f"\n=== Validation Results ===")
        print(f"Request ID: {report.request_id}")
        print(f"Total proposals: {report.total_proposals}")
        print(f"Valid proposals: {report.valid_count}")
        print(f"Invalid proposals: {report.invalid_count}")
        print(f"Validation rate: {report.valid_count / report.total_proposals * 100:.1f}%")
        
        # Show valid proposals
        print(f"\n=== Valid Proposals ({len(valid_proposals)}) ===")
        for proposal in valid_proposals:
            print(f"✅ {proposal.id}: {proposal.name}")
            print(f"   Signal IDs: {proposal.signal_ids}")
            print(f"   Platforms: {proposal.platforms}")
            print(f"   Score: {proposal.score}")
            print()
        
        # Show invalid proposals with reasons
        print(f"=== Invalid Proposals ({len(invalid_proposals)}) ===")
        for proposal in invalid_proposals:
            print(f"❌ {proposal.id}: {proposal.name}")
            print(f"   Signal IDs: {proposal.signal_ids}")
            print(f"   Logic: {proposal.logic}")
            print(f"   Validation Errors: {proposal.validation_errors}")
            print()
        
        # Show validation errors
        if report.validation_errors:
            print("=== Validation Errors ===")
            for error in report.validation_errors:
                print(f"  • {error}")
        
        # Show validation summary
        summary = validator.get_validation_summary(valid_proposals, invalid_proposals)
        print(f"\n=== Validation Summary ===")
        print(f"Validation rate: {summary['validation_rate']:.1%}")
        print(f"Valid proposal IDs: {summary['valid_proposal_ids']}")
        print(f"Invalid proposal IDs: {summary['invalid_proposal_ids']}")
        
        # Show platform intersections for valid proposals
        print(f"\n=== Platform Intersections ===")
        for proposal_id, platforms in summary['common_platforms_by_proposal'].items():
            print(f"{proposal_id}: {platforms}")
        
        # Show debug info if available
        if report.debug_info:
            print(f"\n=== Debug Info ===")
            for key, value in report.debug_info.items():
                print(f"{key}: {value}")
        
        print(f"\n✅ Validation test completed successfully!")
        print(f"📝 Check logs/proposal_validation.log for detailed validation logs")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db_connection.close()


def test_database_queries():
    """Test database queries used by the validator."""
    print("\n=== Testing Database Queries ===")
    
    if not os.path.exists('signals_agent.db'):
        print("Database not found. Please run 'python init_db.py' first.")
        return
    
    db_connection = sqlite3.connect('signals_agent.db')
    cursor = db_connection.cursor()
    
    try:
        # Test signal segments query
        print("--- Signal Segments ---")
        cursor.execute("SELECT id, name FROM signal_segments LIMIT 5")
        signals = cursor.fetchall()
        for signal_id, name in signals:
            print(f"  {signal_id}: {name}")
        
        # Test platform deployments query
        print("\n--- Platform Deployments ---")
        cursor.execute("""
            SELECT signals_agent_segment_id, platform, is_live 
            FROM platform_deployments 
            WHERE is_live = 1 
            LIMIT 10
        """)
        deployments = cursor.fetchall()
        for segment_id, platform, is_live in deployments:
            print(f"  {segment_id} -> {platform} (live: {is_live})")
        
        # Test platform intersection for specific signals
        print("\n--- Platform Intersection Test ---")
        test_signal_ids = ["signal_001", "signal_002"]
        all_platforms = []
        
        for signal_id in test_signal_ids:
            cursor.execute("""
                SELECT DISTINCT platform 
                FROM platform_deployments 
                WHERE signals_agent_segment_id = ? AND is_live = 1
            """, (signal_id,))
            
            signal_platforms = {row[0] for row in cursor.fetchall()}
            all_platforms.append(signal_platforms)
            print(f"  {signal_id} platforms: {signal_platforms}")
        
        if all_platforms:
            common_platforms = set.intersection(*all_platforms)
            print(f"  Common platforms: {common_platforms}")
        
        print("✅ Database queries test completed successfully!")
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db_connection.close()


def main():
    """Run all tests."""
    print("Testing ProposalValidator Service")
    print("=" * 50)
    
    # Test database queries first
    test_database_queries()
    
    # Test proposal validator
    test_proposal_validator()
    
    print("\n" + "=" * 50)
    print("All tests completed!")


if __name__ == "__main__":
    main()
