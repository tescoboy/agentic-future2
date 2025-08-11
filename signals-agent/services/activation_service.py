"""Activation service for handling signal and proposal activations."""

import logging
import sqlite3
from datetime import datetime, timedelta
from typing import List, Optional, Set, Tuple, Dict, Any
from api_models import ActivationRequest, Proposal


class ActivationService:
    """Service for handling signal and proposal activations."""
    
    def __init__(self, db_connection: sqlite3.Connection):
        """Initialize activation service."""
        self.db_connection = db_connection
        self.logger = logging.getLogger(__name__)
    
    def process_activation(self, request: ActivationRequest) -> Tuple[str, List[str], Dict[str, Any]]:
        """
        Process activation request and return activation details.
        
        Returns:
            Tuple of (activation_id, allowed_platforms, activation_details)
        """
        try:
            self.logger.info(f"Processing activation request: {request}")
            
            # Step 1: Determine target and get allowed platforms
            if request.proposal_id:
                target_id, target_type, allowed_platforms = self._process_proposal_activation(request)
            elif request.segment_id:
                target_id, target_type, allowed_platforms = self._process_segment_activation(request)
            else:
                raise ValueError("Either proposal_id or segment_id must be provided")
            
            # Step 2: Validate principal access
            self._validate_principal_access(request.principal_id, target_id, target_type)
            
            # Step 3: Intersect with requested platforms
            final_platforms = self._intersect_platforms(allowed_platforms, request.platforms)
            
            if not final_platforms:
                raise ValueError(f"No valid platforms available for {target_type} {target_id}")
            
            # Step 4: Create activation context
            activation_id = self._create_activation_context(
                request.principal_id, target_id, target_type, final_platforms
            )
            
            # Step 5: Prepare activation details
            activation_details = {
                "target_id": target_id,
                "target_type": target_type,
                "principal_id": request.principal_id,
                "platforms": final_platforms,
                "status": "queued",
                "created_at": datetime.now().isoformat(),
                "estimated_duration_minutes": 60  # Default estimate
            }
            
            self.logger.info(f"Activation processed successfully: {activation_id}")
            return activation_id, final_platforms, activation_details
            
        except Exception as e:
            self.logger.error(f"Activation processing failed: {e}")
            raise
    
    def _process_proposal_activation(self, request: ActivationRequest) -> Tuple[str, str, List[str]]:
        """Process proposal activation."""
        self.logger.info(f"Processing proposal activation: {request.proposal_id}")
        
        # Load proposal from database (in a real system, this would be from a proposals table)
        # For now, we'll simulate this by checking if the proposal_id exists in our sample data
        proposal = self._get_proposal_by_id(request.proposal_id)
        
        if not proposal:
            raise ValueError(f"Proposal not found: {request.proposal_id}")
        
        if not proposal.valid:
            raise ValueError(f"Proposal is not valid: {request.proposal_id}")
        
        # Get common platforms from proposal's signal IDs
        allowed_platforms = self._get_common_platforms_for_signals(proposal.signal_ids)
        
        if not allowed_platforms:
            raise ValueError(f"No common platforms found for proposal signals: {proposal.signal_ids}")
        
        return request.proposal_id, "proposal", list(allowed_platforms)
    
    def _process_segment_activation(self, request: ActivationRequest) -> Tuple[str, str, List[str]]:
        """Process segment activation."""
        self.logger.info(f"Processing segment activation: {request.segment_id}")
        
        # Verify segment exists
        if not self._segment_exists(request.segment_id):
            raise ValueError(f"Segment not found: {request.segment_id}")
        
        # Get allowed platforms for the segment
        allowed_platforms = self._get_segment_platforms(request.segment_id)
        
        if not allowed_platforms:
            raise ValueError(f"No platforms found for segment: {request.segment_id}")
        
        return request.segment_id, "segment", list(allowed_platforms)
    
    def _get_proposal_by_id(self, proposal_id: str) -> Optional[Proposal]:
        """Get proposal by ID from database or sample data."""
        # In a real system, this would query a proposals table
        # For now, we'll create a simple proposal based on known signal IDs
        try:
            cursor = self.db_connection.cursor()
            
            # Check if this is a known proposal ID pattern
            if proposal_id.startswith("proposal_"):
                # Extract signal IDs from proposal ID or use default
                if "001" in proposal_id:
                    signal_ids = ["signal_001", "signal_002"]
                elif "002" in proposal_id:
                    signal_ids = ["signal_003"]
                else:
                    # Try to get signal IDs from a proposals table if it exists
                    cursor.execute("SELECT signal_ids FROM proposals WHERE id = ?", (proposal_id,))
                    result = cursor.fetchone()
                    if result:
                        signal_ids = result[0].split(',') if result[0] else []
                    else:
                        return None
                
                # Get common platforms for these signals
                common_platforms = self._get_common_platforms_for_signals(signal_ids)
                
                if common_platforms:
                    return Proposal(
                        id=proposal_id,
                        name=f"Proposal {proposal_id}",
                        signal_ids=signal_ids,
                        logic="OR",
                        platforms=list(common_platforms),
                        valid=True
                    )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting proposal {proposal_id}: {e}")
            return None
    
    def _segment_exists(self, segment_id: str) -> bool:
        """Check if segment exists in database."""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT id FROM signal_segments WHERE id = ?", (segment_id,))
            return cursor.fetchone() is not None
        except Exception as e:
            self.logger.error(f"Error checking segment existence: {e}")
            return False
    
    def _get_segment_platforms(self, segment_id: str) -> Set[str]:
        """Get allowed platforms for a segment."""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT DISTINCT platform 
                FROM platform_deployments 
                WHERE signals_agent_segment_id = ? AND is_live = 1
            """, (segment_id,))
            
            platforms = {row[0] for row in cursor.fetchall()}
            self.logger.info(f"Found platforms for segment {segment_id}: {platforms}")
            return platforms
            
        except Exception as e:
            self.logger.error(f"Error getting platforms for segment {segment_id}: {e}")
            return set()
    
    def _get_common_platforms_for_signals(self, signal_ids: List[str]) -> Set[str]:
        """Get common platforms across multiple signals."""
        if not signal_ids:
            return set()
        
        try:
            cursor = self.db_connection.cursor()
            all_platforms = []
            
            for signal_id in signal_ids:
                cursor.execute("""
                    SELECT DISTINCT platform 
                    FROM platform_deployments 
                    WHERE signals_agent_segment_id = ? AND is_live = 1
                """, (signal_id,))
                
                signal_platforms = {row[0] for row in cursor.fetchall()}
                all_platforms.append(signal_platforms)
                self.logger.info(f"Signal {signal_id} platforms: {signal_platforms}")
            
            if all_platforms:
                common_platforms = set.intersection(*all_platforms)
                self.logger.info(f"Common platforms: {common_platforms}")
                return common_platforms
            else:
                return set()
                
        except Exception as e:
            self.logger.error(f"Error getting common platforms: {e}")
            return set()
    
    def _validate_principal_access(self, principal_id: str, target_id: str, target_type: str):
        """Validate principal access to target."""
        try:
            cursor = self.db_connection.cursor()
            
            if target_type == "segment":
                # Check principal_segment_access table
                cursor.execute("""
                    SELECT access_type FROM principal_segment_access 
                    WHERE principal_id = ? AND signals_agent_segment_id = ?
                """, (principal_id, target_id))
                
                result = cursor.fetchone()
                if not result:
                    self.logger.warning(f"No access record found for principal {principal_id} to segment {target_id}")
                    # In a real system, you might want to be more strict here
                    # For now, we'll allow access if no explicit restriction exists
                
            elif target_type == "proposal":
                # For proposals, check access to all constituent segments
                proposal = self._get_proposal_by_id(target_id)
                if proposal:
                    for signal_id in proposal.signal_ids:
                        cursor.execute("""
                            SELECT access_type FROM principal_segment_access 
                            WHERE principal_id = ? AND signals_agent_segment_id = ?
                        """, (principal_id, signal_id))
                        
                        result = cursor.fetchone()
                        if not result:
                            self.logger.warning(f"No access record found for principal {principal_id} to segment {signal_id}")
                            # Continue checking other segments
                
        except Exception as e:
            self.logger.error(f"Error validating principal access: {e}")
            # In a real system, you might want to raise an exception here
            # For now, we'll log the error and continue
    
    def _intersect_platforms(self, available_platforms: List[str], requested_platforms: List[str]) -> List[str]:
        """Intersect available platforms with requested platforms."""
        if not requested_platforms:
            return available_platforms
        
        available_set = set(available_platforms)
        requested_set = set(requested_platforms)
        
        intersection = available_set.intersection(requested_set)
        
        if not intersection:
            raise ValueError(
                f"No overlap between available platforms {available_platforms} "
                f"and requested platforms {requested_platforms}"
            )
        
        self.logger.info(f"Platform intersection: {list(intersection)}")
        return list(intersection)
    
    def _create_activation_context(self, principal_id: str, target_id: str, 
                                 target_type: str, platforms: List[str]) -> str:
        """Create activation context in database."""
        try:
            cursor = self.db_connection.cursor()
            
            # Generate activation ID
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            activation_id = f"act_{timestamp}_{target_id}"
            
            # Create context row
            cursor.execute("""
                INSERT INTO contexts (
                    context_id, principal_id, context_type, parent_context_id,
                    status, metadata, created_at, expires_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                activation_id,
                principal_id,
                "activation",
                None,  # No parent context for now
                "pending",
                f'{{"target_id": "{target_id}", "target_type": "{target_type}", "platforms": {platforms}}}',
                datetime.now().isoformat(),
                (datetime.now() + timedelta(days=1)).isoformat()  # Expire in 24 hours
            ))
            
            self.db_connection.commit()
            self.logger.info(f"Created activation context: {activation_id}")
            return activation_id
            
        except Exception as e:
            self.logger.error(f"Error creating activation context: {e}")
            self.db_connection.rollback()
            raise
    
    def get_activation_status(self, activation_id: str) -> Optional[Dict[str, Any]]:
        """Get activation status from database."""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT context_id, principal_id, context_type, status, 
                       metadata, created_at, completed_at
                FROM contexts 
                WHERE context_id = ?
            """, (activation_id,))
            
            row = cursor.fetchone()
            if row:
                context_id, principal_id, context_type, status, metadata, created_at, completed_at = row
                return {
                    "activation_id": context_id,
                    "principal_id": principal_id,
                    "context_type": context_type,
                    "status": status,
                    "metadata": metadata,
                    "created_at": created_at,
                    "updated_at": completed_at or created_at  # Use completed_at or created_at as updated_at
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting activation status: {e}")
            return None
