"""Proposal validation service for Signals Agent."""

import logging
import os
import uuid
from datetime import datetime
from typing import List, Dict, Any, Tuple, Set
from dataclasses import dataclass

from api_models import Proposal, ValidationError


@dataclass
class ValidationReport:
    """Validation report for proposals."""
    request_id: str
    total_proposals: int
    valid_count: int
    invalid_count: int
    validation_errors: List[str]
    timestamp: str
    debug_info: Dict[str, Any]


class ProposalValidator:
    """Validates proposals against backend rules."""
    
    def __init__(self, db_connection, debug_mode: bool = False):
        """Initialize validator with database connection and debug mode."""
        self.db_connection = db_connection
        self.debug_mode = debug_mode
        
        # Configure logging
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
    
    def _setup_logging(self):
        """Set up logging to proposal_validation.log."""
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        # Create file handler for proposal validation
        file_handler = logging.FileHandler('logs/proposal_validation.log')
        file_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.INFO)
    
    def validate(self, proposals: List[Proposal]) -> Tuple[List[Proposal], List[Proposal], ValidationReport]:
        """
        Validate proposals against backend rules.
        
        Returns:
            Tuple of (valid_proposals, invalid_proposals, validation_report)
        """
        request_id = str(uuid.uuid4())
        self.logger.info(f"Starting proposal validation - Request ID: {request_id}")
        
        valid_proposals = []
        invalid_proposals = []
        validation_errors = []
        
        for proposal in proposals:
            self.logger.info(f"Validating proposal {proposal.id} - Request ID: {request_id}")
            
            # Validate the proposal
            is_valid, errors = self._validate_single_proposal(proposal, request_id)
            
            if is_valid:
                valid_proposals.append(proposal)
                self.logger.info(f"Proposal {proposal.id} is VALID - Request ID: {request_id}")
            else:
                # Mark proposal as invalid and add validation errors
                proposal.valid = False
                proposal.validation_errors = errors
                invalid_proposals.append(proposal)
                validation_errors.extend([f"Proposal {proposal.id}: {error}" for error in errors])
                self.logger.warning(f"Proposal {proposal.id} is INVALID - Errors: {errors} - Request ID: {request_id}")
        
        # Create validation report
        report = ValidationReport(
            request_id=request_id,
            total_proposals=len(proposals),
            valid_count=len(valid_proposals),
            invalid_count=len(invalid_proposals),
            validation_errors=validation_errors,
            timestamp=datetime.now().isoformat(),
            debug_info={
                "debug_mode": self.debug_mode,
                "validation_rules_applied": [
                    "no_hallucinations",
                    "platform_unity", 
                    "or_logic_only",
                    "required_metadata"
                ]
            } if self.debug_mode else {}
        )
        
        self.logger.info(
            f"Validation complete - Request ID: {request_id}, "
            f"Valid: {len(valid_proposals)}, Invalid: {len(invalid_proposals)}"
        )
        
        return valid_proposals, invalid_proposals, report
    
    def _validate_single_proposal(self, proposal: Proposal, request_id: str) -> Tuple[bool, List[str]]:
        """Validate a single proposal against all rules."""
        errors = []
        
        # Rule 1: No hallucinations - every signal_id exists in DB
        if not self._validate_signal_ids_exist(proposal.signal_ids, request_id):
            errors.append("One or more signal IDs do not exist in database")
        
        # Rule 2: Platform unity - all signals share at least one common decisioning platform
        common_platforms = self._validate_platform_unity(proposal.signal_ids, request_id)
        if not common_platforms:
            errors.append("Signals do not share any common decisioning platforms")
        else:
            # Update proposal platforms to intersection
            proposal.platforms = list(common_platforms)
            if self.debug_mode:
                self.logger.info(f"Updated proposal {proposal.id} platforms to intersection: {proposal.platforms} - Request ID: {request_id}")
        
        # Rule 3: OR logic only
        if proposal.logic != "OR":
            errors.append("Only OR logic is allowed")
        
        # Rule 4: Required metadata present
        if not self._validate_required_metadata(proposal):
            errors.append("Required metadata is missing")
        
        return len(errors) == 0, errors
    
    def _validate_signal_ids_exist(self, signal_ids: List[str], request_id: str) -> bool:
        """Check if all signal IDs exist in the database."""
        try:
            cursor = self.db_connection.cursor()
            
            # Check each signal ID
            for signal_id in signal_ids:
                cursor.execute(
                    "SELECT id FROM signal_segments WHERE id = ?",
                    (signal_id,)
                )
                result = cursor.fetchone()
                
                if not result:
                    self.logger.warning(f"Signal ID {signal_id} not found in database - Request ID: {request_id}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Database error checking signal IDs: {e} - Request ID: {request_id}")
            return False
    
    def _validate_platform_unity(self, signal_ids: List[str], request_id: str) -> Set[str]:
        """Find common platforms across all signals in the proposal."""
        try:
            cursor = self.db_connection.cursor()
            
            # Get platforms for each signal
            all_platforms = []
            for signal_id in signal_ids:
                cursor.execute("""
                    SELECT DISTINCT platform 
                    FROM platform_deployments 
                    WHERE signals_agent_segment_id = ? AND is_live = 1
                """, (signal_id,))
                
                signal_platforms = {row[0] for row in cursor.fetchall()}
                all_platforms.append(signal_platforms)
                
                if self.debug_mode:
                    self.logger.info(f"Signal {signal_id} platforms: {signal_platforms} - Request ID: {request_id}")
            
            # Find intersection of all platform sets
            if all_platforms:
                common_platforms = set.intersection(*all_platforms)
                if self.debug_mode:
                    self.logger.info(f"Common platforms: {common_platforms} - Request ID: {request_id}")
                return common_platforms
            else:
                return set()
                
        except Exception as e:
            self.logger.error(f"Database error checking platform unity: {e} - Request ID: {request_id}")
            return set()
    
    def _validate_required_metadata(self, proposal: Proposal) -> bool:
        """Validate that required metadata is present."""
        # Check for basic required fields
        required_fields = ['id', 'name', 'signal_ids', 'logic', 'platforms']
        
        for field in required_fields:
            if not hasattr(proposal, field) or getattr(proposal, field) is None:
                return False
        
        # Check that signal_ids is not empty
        if not proposal.signal_ids:
            return False
        
        # Check that platforms is not empty
        if not proposal.platforms:
            return False
        
        return True
    
    def get_validation_summary(self, valid_proposals: List[Proposal], invalid_proposals: List[Proposal]) -> Dict[str, Any]:
        """Get a summary of validation results."""
        return {
            "total_proposals": len(valid_proposals) + len(invalid_proposals),
            "valid_proposals": len(valid_proposals),
            "invalid_proposals": len(invalid_proposals),
            "validation_rate": len(valid_proposals) / (len(valid_proposals) + len(invalid_proposals)) if (len(valid_proposals) + len(invalid_proposals)) > 0 else 0,
            "valid_proposal_ids": [p.id for p in valid_proposals],
            "invalid_proposal_ids": [p.id for p in invalid_proposals],
            "common_platforms_by_proposal": {
                p.id: p.platforms for p in valid_proposals
            }
        }
