"""Status simulator for demo activation lifecycle management."""

import logging
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from database import get_db_connection


class StatusSimulator:
    """Simulates activation status transitions for demo purposes."""
    
    def __init__(self, db_connection: sqlite3.Connection):
        """Initialize status simulator."""
        self.db_connection = db_connection
        self.logger = logging.getLogger(__name__)
        
        # Define status transition flow (matching database constraints)
        self.status_flow = {
            'pending': 'in_progress',
            'in_progress': 'completed',
            'completed': 'completed',  # Terminal state
            'failed': 'failed',        # Terminal state
            'expired': 'expired'       # Terminal state
        }
    
    def simulate_status_transition(self, activation_id: str) -> Optional[Dict[str, Any]]:
        """
        Simulate the next status transition for an activation.
        
        Returns:
            Updated activation details or None if not found
        """
        try:
            cursor = self.db_connection.cursor()
            
            # Get current activation status
            cursor.execute("""
                SELECT context_id, principal_id, context_type, status, 
                       metadata, created_at, completed_at
                FROM contexts 
                WHERE context_id = ?
            """, (activation_id,))
            
            row = cursor.fetchone()
            if not row:
                self.logger.warning(f"Activation not found: {activation_id}")
                return None
            
            context_id, principal_id, context_type, current_status, metadata, created_at, completed_at = row
            
            # Determine next status
            next_status = self.status_flow.get(current_status)
            if not next_status or next_status == current_status:
                self.logger.info(f"Activation {activation_id} already in terminal state: {current_status}")
                return self._get_activation_details(row)
            
            # Update status
            update_time = datetime.now().isoformat()
            
            if next_status in ['completed', 'failed']:
                # Set completed_at for terminal states
                cursor.execute("""
                    UPDATE contexts 
                    SET status = ?, completed_at = ?
                    WHERE context_id = ?
                """, (next_status, update_time, activation_id))
            else:
                # Update status only for non-terminal states
                cursor.execute("""
                    UPDATE contexts 
                    SET status = ?
                    WHERE context_id = ?
                """, (next_status, activation_id))
            
            self.db_connection.commit()
            
            # Get updated details
            cursor.execute("""
                SELECT context_id, principal_id, context_type, status, 
                       metadata, created_at, completed_at
                FROM contexts 
                WHERE context_id = ?
            """, (activation_id,))
            
            updated_row = cursor.fetchone()
            if updated_row:
                self.logger.info(f"Activation {activation_id} status updated: {current_status} -> {next_status}")
                return self._get_activation_details(updated_row)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error simulating status transition: {e}")
            self.db_connection.rollback()
            return None
    
    def simulate_bulk_transitions(self, max_transitions: int = 10) -> List[Dict[str, Any]]:
        """
        Simulate status transitions for multiple pending/queued activations.
        
        Returns:
            List of updated activation details
        """
        try:
            cursor = self.db_connection.cursor()
            
            # Get activations that can be transitioned
            cursor.execute("""
                SELECT context_id, principal_id, context_type, status, 
                       metadata, created_at, completed_at
                FROM contexts 
                WHERE context_type = 'activation' 
                AND status IN ('pending', 'in_progress')
                ORDER BY created_at ASC
                LIMIT ?
            """, (max_transitions,))
            
            rows = cursor.fetchall()
            updated_activations = []
            
            for row in rows:
                activation_id = row[0]
                updated_details = self.simulate_status_transition(activation_id)
                if updated_details:
                    updated_activations.append(updated_details)
            
            self.logger.info(f"Bulk transition completed: {len(updated_activations)} activations updated")
            return updated_activations
            
        except Exception as e:
            self.logger.error(f"Error in bulk transition simulation: {e}")
            return []
    
    def get_activation_status(self, activation_id: str) -> Optional[Dict[str, Any]]:
        """Get current activation status from database."""
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
                return self._get_activation_details(row)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting activation status: {e}")
            return None
    
    def get_pending_activations(self) -> List[Dict[str, Any]]:
        """Get all pending activations."""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT context_id, principal_id, context_type, status, 
                       metadata, created_at, completed_at
                FROM contexts 
                WHERE context_type = 'activation' 
                AND status IN ('pending', 'in_progress')
                ORDER BY created_at ASC
            """)
            
            rows = cursor.fetchall()
            return [self._get_activation_details(row) for row in rows]
            
        except Exception as e:
            self.logger.error(f"Error getting pending activations: {e}")
            return []
    
    def force_status(self, activation_id: str, status: str) -> Optional[Dict[str, Any]]:
        """
        Force an activation to a specific status (for testing).
        
        Args:
            activation_id: The activation ID
            status: The status to force (must be valid)
        
        Returns:
            Updated activation details or None if failed
        """
        valid_statuses = ['pending', 'in_progress', 'completed', 'failed', 'expired']
        if status not in valid_statuses:
            self.logger.error(f"Invalid status: {status}. Valid statuses: {valid_statuses}")
            return None
        
        try:
            cursor = self.db_connection.cursor()
            
            # Check if activation exists
            cursor.execute("SELECT context_id FROM contexts WHERE context_id = ?", (activation_id,))
            if not cursor.fetchone():
                self.logger.warning(f"Activation not found: {activation_id}")
                return None
            
            # Update status
            update_time = datetime.now().isoformat()
            
            if status in ['completed', 'failed']:
                cursor.execute("""
                    UPDATE contexts 
                    SET status = ?, completed_at = ?
                    WHERE context_id = ?
                """, (status, update_time, activation_id))
            else:
                cursor.execute("""
                    UPDATE contexts 
                    SET status = ?
                    WHERE context_id = ?
                """, (status, activation_id))
            
            self.db_connection.commit()
            
            # Get updated details
            return self.get_activation_status(activation_id)
            
        except Exception as e:
            self.logger.error(f"Error forcing status: {e}")
            self.db_connection.rollback()
            return None
    
    def _get_activation_details(self, row: tuple) -> Dict[str, Any]:
        """Convert database row to activation details dictionary."""
        context_id, principal_id, context_type, status, metadata, created_at, completed_at = row
        
        return {
            "activation_id": context_id,
            "principal_id": principal_id,
            "context_type": context_type,
            "status": status,
            "metadata": metadata,
            "created_at": created_at,
            "updated_at": completed_at or created_at,
            "completed_at": completed_at
        }
    
    def cleanup_expired_activations(self) -> int:
        """
        Clean up expired activations (older than 7 days).
        
        Returns:
            Number of activations cleaned up
        """
        try:
            cursor = self.db_connection.cursor()
            
            # Delete activations older than 7 days
            cutoff_date = (datetime.now() - timedelta(days=7)).isoformat()
            
            cursor.execute("""
                DELETE FROM contexts 
                WHERE context_type = 'activation' 
                AND created_at < ?
            """, (cutoff_date,))
            
            deleted_count = cursor.rowcount
            self.db_connection.commit()
            
            self.logger.info(f"Cleaned up {deleted_count} expired activations")
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"Error cleaning up expired activations: {e}")
            self.db_connection.rollback()
            return 0
