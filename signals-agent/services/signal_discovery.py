"""Signal discovery service for database queries and candidate signal retrieval."""

import logging
import sqlite3
from typing import List, Optional, Set
from api_models import SignalMatch


class SignalDiscoveryService:
    """Service for discovering candidate signals from database."""
    
    def __init__(self, db_connection: sqlite3.Connection):
        """Initialize signal discovery service."""
        self.db_connection = db_connection
        self.logger = logging.getLogger(__name__)
    
    def get_candidate_signals(self, query: str, platforms: Optional[List[str]] = None, 
                            limit: int = 50) -> List[SignalMatch]:
        """
        Get candidate signals from database based on platform filters.
        Text relevance ranking is handled by AI, not database filtering.
        
        Args:
            query: Search query (used for logging, not database filtering)
            platforms: Optional list of platforms to filter by
            limit: Maximum number of signals to return
            
        Returns:
            List of SignalMatch objects
        """
        try:
            self.logger.info(f"Getting candidate signals (query: '{query}' for AI ranking, platforms: {platforms})")
            
            # Build the SQL query
            sql, params = self._build_search_query(query, platforms, limit)
            
            # Execute query
            cursor = self.db_connection.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            # Convert to SignalMatch objects
            signals = []
            seen_names = set()  # Track seen names to prevent duplicates
            
            for row in rows:
                signal = self._row_to_signal_match(row)
                if signal and signal.name not in seen_names:
                    signals.append(signal)
                    seen_names.add(signal.name)
                elif signal and signal.name in seen_names:
                    self.logger.debug(f"Skipping duplicate signal: {signal.name}")
            
            self.logger.info(f"Found {len(signals)} unique candidate signals")
            return signals
            
        except Exception as e:
            self.logger.error(f"Error getting candidate signals: {e}")
            return []
    
    def _build_search_query(self, query: str, platforms: Optional[List[str]], limit: int) -> tuple:
        """Build SQL query for signal search."""
        # Base query - get all signals, let AI do the relevance ranking
        sql = """
            SELECT DISTINCT 
                s.id,
                s.name,
                s.description,
                s.data_provider as provider,
                s.coverage_percentage,
                s.base_cpm as price,
                s.signal_type,
                s.catalog_access
            FROM signal_segments s
        """
        params = []
        
        # Add platform filter if specified
        if platforms:
            sql += """
                WHERE EXISTS (
                    SELECT 1 FROM platform_deployments pd 
                    WHERE pd.signals_agent_segment_id = s.id 
                    AND pd.platform IN ({})
                    AND pd.is_live = 1
                )
            """.format(','.join(['?' for _ in platforms]))
            params.extend(platforms)
        
        # Add ordering and limit
        sql += """
            ORDER BY s.coverage_percentage DESC, s.base_cpm ASC
            LIMIT ?
        """
        params.append(limit)
        
        return sql, params
    
    def _row_to_signal_match(self, row: tuple) -> Optional[SignalMatch]:
        """Convert database row to SignalMatch object."""
        try:
            signal_id, name, description, provider, coverage, price, signal_type, catalog_access = row
            
            # Get allowed platforms for this signal
            allowed_platforms = self._get_signal_platforms(signal_id)
            
            if not allowed_platforms:
                self.logger.warning(f"Signal {signal_id} has no allowed platforms, skipping")
                return None
            
            return SignalMatch(
                id=signal_id,
                name=name,
                provider=provider,
                coverage_percentage=coverage,
                price=price,
                allowed_platforms=list(allowed_platforms),
                description=description,
                signal_type=signal_type,
                catalog_access=catalog_access,
                valid=True
            )
            
        except Exception as e:
            self.logger.error(f"Error converting row to SignalMatch: {e}")
            return None
    
    def _get_signal_platforms(self, signal_id: str) -> Set[str]:
        """Get allowed platforms for a signal."""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT DISTINCT platform 
                FROM platform_deployments 
                WHERE signals_agent_segment_id = ? AND is_live = 1
            """, (signal_id,))
            
            platforms = {row[0] for row in cursor.fetchall()}
            return platforms
            
        except Exception as e:
            self.logger.error(f"Error getting platforms for signal {signal_id}: {e}")
            return set()
    
    def get_all_signals(self, limit: int = 100) -> List[SignalMatch]:
        """Get all available signals (for fallback when no query matches)."""
        try:
            self.logger.info(f"Getting all signals (limit: {limit})")
            
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT 
                    s.id,
                    s.name,
                    s.description,
                    s.data_provider as provider,
                    s.coverage_percentage,
                    s.base_cpm as price,
                    s.signal_type,
                    s.catalog_access
                FROM signal_segments s
                ORDER BY s.coverage_percentage DESC
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            signals = []
            seen_names = set()  # Track seen names to prevent duplicates
            
            for row in rows:
                signal = self._row_to_signal_match(row)
                if signal and signal.name not in seen_names:
                    signals.append(signal)
                    seen_names.add(signal.name)
                elif signal and signal.name in seen_names:
                    self.logger.debug(f"Skipping duplicate signal: {signal.name}")
            
            self.logger.info(f"Retrieved {len(signals)} unique signals")
            return signals
            
        except Exception as e:
            self.logger.error(f"Error getting all signals: {e}")
            return []
