"""AI ranking service using Gemini for signal discovery and proposal generation."""

import json
import logging
import os
import re
from typing import List, Dict, Any, Optional, Tuple
import google.generativeai as genai
from api_models import SignalMatch, Proposal


class AIRankingService:
    """AI ranking service using Gemini for signal discovery."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize AI ranking service."""
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.logger = logging.getLogger(__name__)
        self.is_available = self._initialize_gemini()
    
    def _initialize_gemini(self) -> bool:
        """Initialize Gemini API if key is available."""
        if not self.api_key:
            self.logger.warning("No GEMINI_API_KEY provided, AI ranking will not be available")
            return False
        
        try:
            genai.configure(api_key=self.api_key)
            # Test the API with a simple request
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content("Hello")
            self.logger.info("Gemini API initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini API: {e}")
            return False
    
    def rank_signals(self, query: str, candidate_signals: List[SignalMatch], 
                    max_results: int = 10) -> Tuple[List[SignalMatch], str]:
        """
        Rank signals using AI based on query relevance.
        
        Returns:
            Tuple of (ranked_signals, ranking_method)
        """
        if not self.is_available:
            self.logger.warning("AI ranking not available, using fallback ranking")
            return self._fallback_ranking(candidate_signals, max_results), "fallback"
        
        try:
            self.logger.info(f"Starting AI ranking for query: {query}")
            
            # Create prompt for signal ranking
            prompt = self._create_ranking_prompt(query, candidate_signals, max_results)
            
            # Call Gemini API
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            
            # Log the AI response for debugging
            self.logger.info(f"AI ranking response: {response.text}")
            
            # Parse response
            ranked_signal_ids = self._parse_ranking_response(response.text)
            
            if ranked_signal_ids:
                # Reorder signals based on AI ranking
                ranked_signals = self._reorder_signals(candidate_signals, ranked_signal_ids)
                self.logger.info(f"AI ranking completed successfully, ranked {len(ranked_signals)} signals")
                return ranked_signals[:max_results], "ai_ranking"
            else:
                self.logger.warning("AI ranking failed to parse response, using fallback")
                return self._fallback_ranking(candidate_signals, max_results), "fallback"
                
        except Exception as e:
            self.logger.error(f"AI ranking failed: {e}")
            return self._fallback_ranking(candidate_signals, max_results), "fallback"
    
    def generate_proposals(self, query: str, ranked_signals: List[SignalMatch], 
                          max_proposals: int = 5) -> Tuple[List[Proposal], str]:
        """
        Generate proposals using AI based on query and ranked signals.
        
        Returns:
            Tuple of (proposals, generation_method)
        """
        if not self.is_available:
            self.logger.warning("AI proposal generation not available, using fallback")
            return self._fallback_proposals(ranked_signals, max_proposals), "fallback"
        
        try:
            self.logger.info(f"Starting AI proposal generation for query: {query}")
            
            # Create prompt for proposal generation
            prompt = self._create_proposal_prompt(query, ranked_signals, max_proposals)
            
            # Call Gemini API
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            
            # Parse response
            proposals = self._parse_proposal_response(response.text, ranked_signals)
            
            if proposals:
                self.logger.info(f"AI proposal generation completed successfully, generated {len(proposals)} proposals")
                return proposals, "ai_generation"
            else:
                self.logger.warning("AI proposal generation failed to parse response, using fallback")
                return self._fallback_proposals(ranked_signals, max_proposals), "fallback"
                
        except Exception as e:
            self.logger.error(f"AI proposal generation failed: {e}")
            return self._fallback_proposals(ranked_signals, max_proposals), "fallback"
    
    def _create_ranking_prompt(self, query: str, signals: List[SignalMatch], max_results: int) -> str:
        """Create prompt for signal ranking."""
        signal_info = []
        for signal in signals:
            signal_info.append({
                "id": signal.id,
                "name": signal.name,
                "description": signal.description or "",
                "provider": signal.provider,
                "coverage_percentage": signal.coverage_percentage,
                "price": signal.price,
                "signal_type": signal.signal_type
            })
        
        prompt = f"""
You are a Signal Discovery and Matching Agent for the Ad Context Protocol.
Your job is to take the provided list of available signals and recommend one or more "Proposed Segments" for the advertising campaign.

Campaign Query: "{query}"

Available signals:
{json.dumps(signal_info, indent=2)}

Follow these rules strictly:
1. Return ONLY valid JSON.
2. Do not include any commentary or explanations outside the JSON.
3. Each proposed segment must:
   - Contain only signal IDs from the provided list.
   - Include at least 1 signal.
   - Share at least one common decisioning platform.
   - Use OR logic only (no AND logic).
4. Do not create new or imaginary signal IDs.
5. Use the campaign context to select relevant signals.
6. Include the following fields for each proposal:
   - id: a unique string identifier
   - name: short descriptive name
   - description: short explanation of the segment
   - signals: array of signal IDs

Return a JSON array of proposed segments, like:
[
  {{
    "id": "proposal_001",
    "name": "Relevant Audience Segment",
    "description": "Targets users relevant to the campaign query",
    "signals": ["signal_001", "signal_002"]
  }}
]

Limit to top {max_results} most relevant signals.
"""
        return prompt
    
    def _create_proposal_prompt(self, query: str, signals: List[SignalMatch], max_proposals: int) -> str:
        """Create prompt for proposal generation."""
        signal_info = []
        for signal in signals:
            signal_info.append({
                "id": signal.id,
                "name": signal.name,
                "description": signal.description or "",
                "provider": signal.provider,
                "coverage_percentage": signal.coverage_percentage,
                "price": signal.price,
                "allowed_platforms": signal.allowed_platforms
            })
        
        prompt = f"""
You are an AI assistant that creates advertising signal proposals based on a search query.

Query: "{query}"

Available signals:
{json.dumps(signal_info, indent=2)}

Task: Create {max_proposals} proposals that combine signals to target the query effectively.

Rules:
- Use only OR logic (no AND logic)
- Each proposal should have 1-3 signals
- Signals in a proposal must share at least one platform
- Provide a meaningful name and reasoning for each proposal

Return ONLY a JSON array of proposals, like:
[
  {{
    "id": "proposal_001",
    "name": "High-Value Audience Package",
    "signal_ids": ["signal_001", "signal_002"],
    "reasoning": "Combines high-value shoppers with tech enthusiasts for premium targeting"
  }}
]

Each proposal must have: id, name, signal_ids (array), reasoning (string)
"""
        return prompt
    
    def _parse_ranking_response(self, response_text: str) -> List[str]:
        """Parse AI ranking response safely."""
        try:
            # Extract JSON from response (handle markdown formatting)
            response_text = response_text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            # Clean up common JSON formatting issues
            # Remove trailing commas
            response_text = response_text.replace(',]', ']').replace(',}', '}')
            # Remove trailing commas before closing brackets
            response_text = re.sub(r',\s*([}\]])', r'\1', response_text)
            
            data = json.loads(response_text)
            
            # Handle new format: array of proposed segments
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                # Extract signal IDs from all proposed segments
                signal_ids = []
                for segment in data:
                    if 'signals' in segment and isinstance(segment['signals'], list):
                        signal_ids.extend(segment['signals'])
                return signal_ids
            
            # Handle old format: direct array of signal IDs
            elif isinstance(data, list):
                return data
            else:
                self.logger.error(f"Invalid ranking response format: {response_text}")
                return []
                
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse ranking response as JSON: {e}")
            self.logger.error(f"Response text: {response_text}")
            return []
        except Exception as e:
            self.logger.error(f"Error parsing ranking response: {e}")
            return []
    
    def _parse_proposal_response(self, response_text: str, signals: List[SignalMatch]) -> List[Proposal]:
        """Parse AI proposal response safely."""
        try:
            # Extract JSON from response (handle markdown formatting)
            response_text = response_text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            proposal_data = json.loads(response_text)
            
            if not isinstance(proposal_data, list):
                self.logger.error(f"Invalid proposal response format: {response_text}")
                return []
            
            proposals = []
            signal_map = {signal.id: signal for signal in signals}
            
            for i, data in enumerate(proposal_data):
                try:
                    # Validate required fields
                    if not all(key in data for key in ['id', 'name', 'signal_ids', 'reasoning']):
                        self.logger.warning(f"Proposal {i} missing required fields, skipping")
                        continue
                    
                    # Validate signal IDs exist
                    signal_ids = data['signal_ids']
                    if not all(sid in signal_map for sid in signal_ids):
                        self.logger.warning(f"Proposal {i} contains invalid signal IDs, skipping")
                        continue
                    
                    # Get common platforms
                    common_platforms = self._get_common_platforms([signal_map[sid] for sid in signal_ids])
                    if not common_platforms:
                        self.logger.warning(f"Proposal {i} has no common platforms, skipping")
                        continue
                    
                    proposal = Proposal(
                        id=data['id'],
                        name=data['name'],
                        signal_ids=signal_ids,
                        logic="OR",
                        platforms=list(common_platforms),
                        reasoning=data['reasoning'],
                        score=0.8,  # Default score for AI-generated proposals
                        valid=True
                    )
                    proposals.append(proposal)
                    
                except Exception as e:
                    self.logger.warning(f"Error creating proposal {i}: {e}")
                    continue
            
            return proposals
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse proposal response as JSON: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error parsing proposal response: {e}")
            return []
    
    def _get_common_platforms(self, signals: List[SignalMatch]) -> set:
        """Get common platforms across signals."""
        if not signals:
            return set()
        
        platform_sets = [set(signal.allowed_platforms) for signal in signals]
        return set.intersection(*platform_sets)
    
    def _reorder_signals(self, signals: List[SignalMatch], ranked_ids: List[str]) -> List[SignalMatch]:
        """Reorder signals based on AI ranking."""
        signal_map = {signal.id: signal for signal in signals}
        ranked_signals = []
        seen_names = set()  # Track seen names to prevent duplicates
        
        # Add ONLY the signals that the AI ranked
        for signal_id in ranked_ids:
            if signal_id in signal_map:
                signal = signal_map[signal_id]
                if signal.name not in seen_names:
                    ranked_signals.append(signal)
                    seen_names.add(signal.name)
                else:
                    self.logger.debug(f"Skipping duplicate signal in ranking: {signal.name}")
        
        # Do NOT add remaining signals - only return what the AI ranked
        return ranked_signals
    
    def _fallback_ranking(self, signals: List[SignalMatch], max_results: int) -> List[SignalMatch]:
        """Fallback ranking based on coverage percentage."""
        self.logger.info("Using fallback ranking (coverage-based)")
        
        # Sort by coverage percentage and remove duplicates by name
        seen_names = set()
        unique_signals = []
        
        for signal in sorted(signals, key=lambda s: s.coverage_percentage, reverse=True):
            if signal.name not in seen_names:
                unique_signals.append(signal)
                seen_names.add(signal.name)
                if len(unique_signals) >= max_results:
                    break
        
        return unique_signals
    
    def _fallback_proposals(self, signals: List[SignalMatch], max_proposals: int) -> List[Proposal]:
        """Fallback proposal generation."""
        self.logger.info("Using fallback proposal generation")
        proposals = []
        seen_names = set()  # Track seen names to prevent duplicates
        
        # Create simple proposals with single signals
        for i, signal in enumerate(signals):
            if signal.name not in seen_names and len(proposals) < max_proposals:
                proposal = Proposal(
                    id=f"fallback_proposal_{i+1:03d}",
                    name=f"{signal.name} - Fallback",
                    signal_ids=[signal.id],
                    logic="OR",
                    platforms=signal.allowed_platforms,
                    reasoning=f"Fallback proposal for {signal.name}",
                    score=0.6,  # Lower score for fallback proposals
                    valid=True
                )
                proposals.append(proposal)
                seen_names.add(signal.name)
        
        return proposals
