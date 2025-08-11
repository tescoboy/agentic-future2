#!/usr/bin/env python3
"""Test script for Pydantic models validation."""

import json
from api_models import (
    DiscoveryRequest, SignalMatch, Proposal, DiscoveryResponse,
    ActivationRequest, ActivationResponse, StatusResponse
)


def test_discovery_request():
    """Test DiscoveryRequest validation."""
    print("=== Testing DiscoveryRequest ===")
    
    # Valid request
    try:
        valid_request = DiscoveryRequest(
            query="high value shoppers",
            principal_id="acme_corp",
            limit=5,
            platforms=["index-exchange", "the-trade-desk"]
        )
        print("✅ Valid request created successfully")
    except Exception as e:
        print(f"❌ Valid request failed: {e}")
    
    # Invalid platform
    try:
        invalid_platform = DiscoveryRequest(
            query="test",
            platforms=["invalid-platform"]
        )
        print("❌ Invalid platform should have failed")
    except Exception as e:
        print(f"✅ Invalid platform caught: {e}")
    
    # Empty query
    try:
        empty_query = DiscoveryRequest(query="")
        print("❌ Empty query should have failed")
    except Exception as e:
        print(f"✅ Empty query caught: {e}")
    
    # Invalid limit
    try:
        invalid_limit = DiscoveryRequest(query="test", limit=0)
        print("❌ Invalid limit should have failed")
    except Exception as e:
        print(f"✅ Invalid limit caught: {e}")


def test_proposal():
    """Test Proposal validation."""
    print("\n=== Testing Proposal ===")
    
    # Valid proposal
    try:
        valid_proposal = Proposal(
            id="proposal_001",
            name="High Value Audience",
            signal_ids=["signal_001", "signal_002"],
            logic="OR",
            platforms=["index-exchange", "the-trade-desk"]
        )
        print("✅ Valid proposal created successfully")
    except Exception as e:
        print(f"❌ Valid proposal failed: {e}")
    
    # Invalid logic (AND not allowed)
    try:
        invalid_logic = Proposal(
            id="proposal_002",
            name="Test Proposal",
            signal_ids=["signal_001"],
            logic="AND",
            platforms=["index-exchange"]
        )
        print("❌ AND logic should have failed")
    except Exception as e:
        print(f"✅ AND logic caught: {e}")
    
    # Empty signal_ids
    try:
        empty_signals = Proposal(
            id="proposal_003",
            name="Test Proposal",
            signal_ids=[],
            logic="OR",
            platforms=["index-exchange"]
        )
        print("❌ Empty signal_ids should have failed")
    except Exception as e:
        print(f"✅ Empty signal_ids caught: {e}")
    
    # Duplicate signal_ids
    try:
        duplicate_signals = Proposal(
            id="proposal_004",
            name="Test Proposal",
            signal_ids=["signal_001", "signal_001"],
            logic="OR",
            platforms=["index-exchange"]
        )
        print("❌ Duplicate signal_ids should have failed")
    except Exception as e:
        print(f"✅ Duplicate signal_ids caught: {e}")


def test_activation_request():
    """Test ActivationRequest validation."""
    print("\n=== Testing ActivationRequest ===")
    
    # Valid request with segment_id
    try:
        valid_segment = ActivationRequest(
            segment_id="signal_001",
            principal_id="acme_corp",
            platforms=["index-exchange"]
        )
        print("✅ Valid segment activation created successfully")
    except Exception as e:
        print(f"❌ Valid segment activation failed: {e}")
    
    # Valid request with proposal_id
    try:
        valid_proposal = ActivationRequest(
            proposal_id="proposal_001",
            principal_id="acme_corp",
            platforms=["index-exchange"]
        )
        print("✅ Valid proposal activation created successfully")
    except Exception as e:
        print(f"❌ Valid proposal activation failed: {e}")
    
    # Missing both segment_id and proposal_id
    try:
        missing_target = ActivationRequest(
            principal_id="acme_corp",
            platforms=["index-exchange"]
        )
        print("❌ Missing target should have failed")
    except Exception as e:
        print(f"✅ Missing target caught: {e}")
    
    # Both segment_id and proposal_id provided
    try:
        both_targets = ActivationRequest(
            segment_id="signal_001",
            proposal_id="proposal_001",
            principal_id="acme_corp",
            platforms=["index-exchange"]
        )
        print("❌ Both targets should have failed")
    except Exception as e:
        print(f"✅ Both targets caught: {e}")
    
    # Empty platforms
    try:
        empty_platforms = ActivationRequest(
            segment_id="signal_001",
            principal_id="acme_corp",
            platforms=[]
        )
        print("❌ Empty platforms should have failed")
    except Exception as e:
        print(f"✅ Empty platforms caught: {e}")


def test_signal_match():
    """Test SignalMatch validation."""
    print("\n=== Testing SignalMatch ===")
    
    # Valid signal match
    try:
        valid_signal = SignalMatch(
            id="signal_001",
            name="High Value Shoppers",
            provider="LiveRamp",
            coverage_percentage=15.2,
            price=2.50,
            allowed_platforms=["index-exchange", "the-trade-desk"],
            signal_type="audience",
            catalog_access="public"
        )
        print("✅ Valid signal match created successfully")
    except Exception as e:
        print(f"❌ Valid signal match failed: {e}")
    
    # Invalid coverage percentage
    try:
        invalid_coverage = SignalMatch(
            id="signal_002",
            name="Test Signal",
            provider="Test Provider",
            coverage_percentage=150.0,  # > 100%
            price=2.50,
            allowed_platforms=["index-exchange"],
            signal_type="audience",
            catalog_access="public"
        )
        print("❌ Invalid coverage should have failed")
    except Exception as e:
        print(f"✅ Invalid coverage caught: {e}")
    
    # Negative price
    try:
        negative_price = SignalMatch(
            id="signal_003",
            name="Test Signal",
            provider="Test Provider",
            coverage_percentage=15.0,
            price=-1.0,  # Negative
            allowed_platforms=["index-exchange"],
            signal_type="audience",
            catalog_access="public"
        )
        print("❌ Negative price should have failed")
    except Exception as e:
        print(f"✅ Negative price caught: {e}")


def test_json_serialization():
    """Test JSON serialization of models."""
    print("\n=== Testing JSON Serialization ===")
    
    try:
        # Create a valid proposal
        proposal = Proposal(
            id="proposal_001",
            name="High Value Audience",
            signal_ids=["signal_001", "signal_002"],
            logic="OR",
            platforms=["index-exchange", "the-trade-desk"],
            score=0.85,
            reasoning="Combines high-value shoppers with tech enthusiasts"
        )
        
        # Convert to dict
        proposal_dict = proposal.model_dump()
        print("✅ Proposal converted to dict successfully")
        
        # Convert to JSON
        proposal_json = proposal.model_dump_json()
        print("✅ Proposal converted to JSON successfully")
        
        # Parse JSON back
        parsed_proposal = Proposal.model_validate_json(proposal_json)
        print("✅ JSON parsed back to Proposal successfully")
        
        print(f"Proposal JSON: {proposal_json[:100]}...")
        
    except Exception as e:
        print(f"❌ JSON serialization failed: {e}")


def main():
    """Run all tests."""
    print("Testing Pydantic Models Validation")
    print("=" * 50)
    
    test_discovery_request()
    test_proposal()
    test_activation_request()
    test_signal_match()
    test_json_serialization()
    
    print("\n" + "=" * 50)
    print("All tests completed!")


if __name__ == "__main__":
    main()
