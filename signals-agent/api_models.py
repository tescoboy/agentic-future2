"""Strict Pydantic models for Signals Agent API."""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, validator, model_validator
from datetime import datetime


class DiscoveryRequest(BaseModel):
    """Request model for signal discovery."""
    query: str = Field(..., min_length=1, max_length=1000, description="Search query for signal discovery")
    principal_id: Optional[str] = Field(None, description="Principal ID for access control")
    limit: Optional[int] = Field(5, ge=1, le=100, description="Maximum number of results to return (default: 5, max: 100)")
    platforms: Optional[List[str]] = Field(None, description="Filter by specific platforms")

    @validator('platforms')
    def validate_platforms(cls, v):
        """Validate platform names."""
        if v is not None:
            valid_platforms = {
                'index-exchange', 'the-trade-desk', 'openx', 'pubmatic',
                'dv360', 'tradedesk', 'amazon', 'google-ads'
            }
            for platform in v:
                if platform.lower() not in valid_platforms:
                    raise ValueError(f"Invalid platform: {platform}. Valid platforms: {', '.join(valid_platforms)}")
        return v


class SignalMatch(BaseModel):
    """Individual signal match result."""
    id: str = Field(..., description="Unique signal identifier")
    name: str = Field(..., min_length=1, max_length=200, description="Signal name")
    provider: str = Field(..., min_length=1, max_length=100, description="Data provider name")
    coverage_percentage: float = Field(..., ge=0.0, le=100.0, description="Coverage percentage")
    price: float = Field(..., ge=0.0, description="CPM price")
    allowed_platforms: List[str] = Field(..., min_items=1, description="Platforms where signal can be activated")
    description: Optional[str] = Field(None, max_length=500, description="Signal description")
    signal_type: str = Field(..., description="Type of signal (audience, contextual, etc.)")
    catalog_access: str = Field(..., description="Access level (public, personalized, private)")
    valid: bool = Field(True, description="Whether signal is valid for activation")

    @validator('allowed_platforms')
    def validate_allowed_platforms(cls, v):
        """Validate allowed platforms."""
        valid_platforms = {
            'index-exchange', 'the-trade-desk', 'openx', 'pubmatic',
            'dv360', 'tradedesk', 'amazon', 'google-ads'
        }
        for platform in v:
            if platform.lower() not in valid_platforms:
                raise ValueError(f"Invalid platform in allowed_platforms: {platform}")
        return v


class Proposal(BaseModel):
    """Signal proposal with validation."""
    id: str = Field(..., description="Unique proposal identifier")
    name: str = Field(..., min_length=1, max_length=200, description="Proposal name")
    signal_ids: List[str] = Field(..., min_items=1, max_items=10, description="List of signal IDs in proposal")
    logic: Literal["OR"] = Field("OR", description="Logic operator - only OR allowed")
    platforms: List[str] = Field(..., min_items=1, description="Platforms where proposal can be activated")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    valid: bool = Field(True, description="Whether proposal is valid")
    validation_errors: Optional[List[str]] = Field(None, description="List of validation errors if invalid")
    score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Proposal relevance score")
    reasoning: Optional[str] = Field(None, max_length=1000, description="Reasoning for proposal")

    @validator('signal_ids')
    def validate_signal_ids(cls, v):
        """Validate signal IDs are not empty and unique."""
        if not v:
            raise ValueError("signal_ids cannot be empty")
        if len(set(v)) != len(v):
            raise ValueError("signal_ids must be unique")
        return v

    @validator('platforms')
    def validate_platforms(cls, v):
        """Validate platforms."""
        valid_platforms = {
            'index-exchange', 'the-trade-desk', 'openx', 'pubmatic',
            'dv360', 'tradedesk', 'amazon', 'google-ads'
        }
        for platform in v:
            if platform.lower() not in valid_platforms:
                raise ValueError(f"Invalid platform: {platform}")
        return v

    @model_validator(mode='after')
    def validate_proposal_logic(self):
        """Ensure only OR logic is used."""
        if self.logic != "OR":
            raise ValueError("Only OR logic is allowed. AND logic is not permitted.")
        return self


class DiscoveryResponse(BaseModel):
    """Response model for signal discovery."""
    matches: List[SignalMatch] = Field(..., description="Individual signal matches")
    proposals: List[Proposal] = Field(..., description="Signal proposals")
    using_fallback: bool = Field(False, description="Whether fallback data is being used")
    ranking_method: str = Field(..., description="Method used for ranking results")
    debug: Optional[Dict[str, Any]] = Field(None, description="Debug information (only in DEBUG_MODE)")
    total_matches: int = Field(..., ge=0, description="Total number of matches found")
    total_proposals: int = Field(..., ge=0, description="Total number of proposals generated")

    @validator('ranking_method')
    def validate_ranking_method(cls, v):
        """Validate ranking method."""
        valid_methods = ['ai_ranking', 'relevance_score', 'coverage_based', 'price_based', 'fallback']
        # Allow combined methods like "ai_ranking_ai_generation"
        if v in valid_methods or any(method in v for method in valid_methods):
            return v
        else:
            raise ValueError(f"Invalid ranking_method: {v}. Valid methods: {', '.join(valid_methods)} or combinations")


class ActivationRequest(BaseModel):
    """Request model for signal activation."""
    segment_id: Optional[str] = Field(None, description="Individual segment ID to activate")
    proposal_id: Optional[str] = Field(None, description="Proposal ID to activate")
    principal_id: str = Field(..., description="Principal ID for access control")
    platforms: List[str] = Field(..., min_items=1, description="Platforms to activate on")

    @validator('platforms')
    def validate_platforms(cls, v):
        """Validate platforms."""
        valid_platforms = {
            'index-exchange', 'the-trade-desk', 'openx', 'pubmatic',
            'dv360', 'tradedesk', 'amazon', 'google-ads'
        }
        for platform in v:
            if platform.lower() not in valid_platforms:
                raise ValueError(f"Invalid platform: {platform}")
        return v

    @model_validator(mode='after')
    def validate_activation_target(self):
        """Ensure either segment_id or proposal_id is provided, but not both."""
        if not self.segment_id and not self.proposal_id:
            raise ValueError("Either segment_id or proposal_id must be provided")
        
        if self.segment_id and self.proposal_id:
            raise ValueError("Cannot provide both segment_id and proposal_id")
        
        return self


class ActivationResponse(BaseModel):
    """Response model for signal activation."""
    activation_id: str = Field(..., description="Unique activation identifier")
    status: str = Field(..., description="Activation status")
    allowed_platforms: List[str] = Field(..., description="Platforms where activation is allowed")
    message: str = Field(..., description="Status message")
    estimated_duration_minutes: Optional[int] = Field(None, ge=1, description="Estimated activation duration")
    created_at: datetime = Field(default_factory=datetime.now, description="Activation creation timestamp")

    @validator('status')
    def validate_status(cls, v):
        """Validate activation status."""
        valid_statuses = ['pending', 'queued', 'in_progress', 'completed', 'failed', 'cancelled']
        if v not in valid_statuses:
            raise ValueError(f"Invalid status: {v}. Valid statuses: {', '.join(valid_statuses)}")
        return v

    @validator('allowed_platforms')
    def validate_allowed_platforms(cls, v):
        """Validate allowed platforms."""
        valid_platforms = {
            'index-exchange', 'the-trade-desk', 'openx', 'pubmatic',
            'dv360', 'tradedesk', 'amazon', 'google-ads'
        }
        for platform in v:
            if platform.lower() not in valid_platforms:
                raise ValueError(f"Invalid platform in allowed_platforms: {platform}")
        return v


class StatusResponse(BaseModel):
    """Response model for activation status."""
    activation_id: str = Field(..., description="Activation identifier")
    status: str = Field(..., description="Current activation status")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional status details")
    created_at: datetime = Field(..., description="Activation creation timestamp")
    updated_at: datetime = Field(..., description="Last status update timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    error_message: Optional[str] = Field(None, description="Error message if failed")

    @validator('status')
    def validate_status(cls, v):
        """Validate status."""
        valid_statuses = ['pending', 'queued', 'in_progress', 'completed', 'failed', 'cancelled']
        if v not in valid_statuses:
            raise ValueError(f"Invalid status: {v}. Valid statuses: {', '.join(valid_statuses)}")
        return v


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str = Field(..., description="Health status")
    timestamp: datetime = Field(default_factory=datetime.now, description="Health check timestamp")
    version: str = Field("1.0.0", description="API version")
    database_connected: bool = Field(..., description="Database connection status")


class ErrorResponse(BaseModel):
    """Standard error response model."""
    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")


# Additional utility models for internal use

class ValidationError(BaseModel):
    """Validation error details."""
    field: str = Field(..., description="Field that failed validation")
    message: str = Field(..., description="Validation error message")
    value: Optional[Any] = Field(None, description="Invalid value")


class ProposalValidationResult(BaseModel):
    """Result of proposal validation."""
    proposal_id: str = Field(..., description="Proposal ID")
    valid: bool = Field(..., description="Whether proposal is valid")
    errors: List[ValidationError] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")


class PlatformInfo(BaseModel):
    """Platform information."""
    name: str = Field(..., description="Platform name")
    display_name: str = Field(..., description="Display name")
    supported: bool = Field(..., description="Whether platform is supported")
    activation_time_minutes: int = Field(..., ge=1, description="Typical activation time")
