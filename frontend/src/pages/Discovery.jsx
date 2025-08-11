import { 
  Container, 
  Row, 
  Col, 
  Card, 
  Button, 
  Alert, 
  Form, 
  Table, 
  Offcanvas,
  Toast,
  ToastContainer,
  Badge,
  Spinner,
  Accordion,
  Modal
} from 'react-bootstrap';
import { useState, useEffect } from 'react';
import apiClient from '../services/api';
import { isHealthResponse, isDiscoveryResponse, isActivationResponse, isStatusResponse } from '../services/typeGuards';

function Discovery() {
  // API Health State
  const [healthStatus, setHealthStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Search Form State
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedPrincipal, setSelectedPrincipal] = useState('');
  const [selectedPlatforms, setSelectedPlatforms] = useState([]);
  const [selectedLimit, setSelectedLimit] = useState(5);
  const [isSearching, setIsSearching] = useState(false);

  // Results State
  const [matches, setMatches] = useState([]);
  const [proposals, setProposals] = useState([]);
  const [discoveryResponse, setDiscoveryResponse] = useState(null);
  const [searchError, setSearchError] = useState(null);

  // Status Drawer State
  const [showStatusDrawer, setShowStatusDrawer] = useState(false);
  const [selectedActivationId, setSelectedActivationId] = useState('');

  // Toast State
  const [toasts, setToasts] = useState([]);

  // Expanded rows state
  const [expandedMatches, setExpandedMatches] = useState(new Set());
  const [expandedProposals, setExpandedProposals] = useState(new Set());

  // Debug state
  const [showDebugPanel, setShowDebugPanel] = useState(false);
  const [debugData, setDebugData] = useState(null);

  // Platform options
  const platformOptions = [
    'index-exchange',
    'the-trade-desk', 
    'openx',
    'pubmatic',
    'amazon',
    'google-ads',
    'dv360'
  ];

  // Principal options
  const principalOptions = [
    { value: '', label: 'Public Access' },
    { value: 'principal_001', label: 'Principal 001' },
    { value: 'principal_002', label: 'Principal 002' }
  ];

  // Limit options
  const limitOptions = [
    { value: 1, label: '1 proposal' },
    { value: 2, label: '2 proposals' },
    { value: 3, label: '3 proposals' },
    { value: 4, label: '4 proposals' },
    { value: 5, label: '5 proposals (default)' },
    { value: 6, label: '6 proposals' },
    { value: 7, label: '7 proposals' },
    { value: 8, label: '8 proposals' },
    { value: 9, label: '9 proposals' },
    { value: 10, label: '10 proposals (max)' }
  ];

  const testHealth = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.getHealth();
      if (isHealthResponse(response)) {
        setHealthStatus(response);
        addToast('success', 'Backend connected successfully!');
      } else {
        const errorMessage = 'Invalid health response format';
        setError(errorMessage);
        addToast('danger', errorMessage);
      }
    } catch (err) {
      const errorMessage = getErrorMessage(err);
      setError(errorMessage);
      addToast('danger', `Connection failed: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) {
      addToast('warning', 'Please enter a search query');
      return;
    }

    setIsSearching(true);
    setSearchError(null);
    setDiscoveryResponse(null);
    
    try {
      const searchBody = {
        query: searchQuery,
        principal_id: selectedPrincipal || null,
        platforms: selectedPlatforms.length > 0 ? selectedPlatforms : null,
        limit: selectedLimit
      };

      const response = await apiClient.postDiscovery(searchBody);
      
      if (isDiscoveryResponse(response)) {
        setDiscoveryResponse(response);
        setMatches(response.matches || []);
        setProposals(response.proposals || []);
        
        // Handle debug data
        if (hasDebugData(response)) {
          setDebugData(response.debug);
          setShowDebugPanel(false); // Hidden by default, user can toggle with button
        } else {
          setDebugData(null);
          setShowDebugPanel(false);
        }
        
        const message = `Found ${response.total_matches} matches and ${response.total_proposals} proposals`;
        if (response.using_fallback) {
          addToast('warning', `${message} (using fallback mode)`);
        } else {
          addToast('success', message);
        }
      } else {
        throw new Error('Invalid discovery response format');
      }
    } catch (err) {
      const errorMessage = getErrorMessage(err);
      setSearchError(errorMessage);
      addToast('danger', `Search failed: ${errorMessage}`);
    } finally {
      setIsSearching(false);
    }
  };

  const handleActivate = (signalId) => {
    setSelectedActivationId(signalId);
    setShowStatusDrawer(true);
    addToast('info', `Activation initiated for signal: ${signalId}`);
  };

  const addToast = (variant, message) => {
    const id = Date.now();
    setToasts(prev => [...prev, { id, variant, message }]);
  };

  const removeToast = (id) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  };

  // Helper functions for expandable details
  const toggleMatchExpanded = (matchId) => {
    setExpandedMatches(prev => {
      const newSet = new Set(prev);
      if (newSet.has(matchId)) {
        newSet.delete(matchId);
      } else {
        newSet.add(matchId);
      }
      return newSet;
    });
  };

  const toggleProposalExpanded = (proposalId) => {
    setExpandedProposals(prev => {
      const newSet = new Set(prev);
      if (newSet.has(proposalId)) {
        newSet.delete(proposalId);
      } else {
        newSet.add(proposalId);
      }
      return newSet;
    });
  };

  const copyToClipboard = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      addToast('success', 'Copied to clipboard!');
    } catch (err) {
      addToast('danger', 'Failed to copy to clipboard');
    }
  };

  const formatDetails = (obj) => {
    if (obj === null || obj === undefined) return 'N/A';
    if (typeof obj === 'object') {
      return JSON.stringify(obj, null, 2);
    }
    return String(obj);
  };

  // Helper function to extract error message from API errors
  const getErrorMessage = (error) => {
    if (error.response?.data?.message) {
      return error.response.data.message;
    }
    if (error.response?.data?.detail) {
      return error.response.data.detail;
    }
    if (error.message) {
      return error.message;
    }
    return 'An unexpected error occurred';
  };

  // Helper function to check if debug data is available
  const hasDebugData = (response) => {
    return response?.debug && typeof response.debug === 'object';
  };

  useEffect(() => {
    // Test API connection on component mount
    testHealth();
  }, []);

  return (
    <>
      {/* API Base URL Badge */}
      <div className="position-fixed top-0 end-0 p-3" style={{ zIndex: 1050 }}>
        <Badge bg="secondary" className="fs-6">
          API: {import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'}
        </Badge>
      </div>

      <Container fluid>
        {/* Hero Search Form */}
        <Row className="mb-4">
          <Col>
            <Card className="border-primary shadow">
              <Card.Header className="bg-primary text-white">
                <h3 className="mb-0">🔍 Signal Discovery</h3>
              </Card.Header>
              <Card.Body>
                <Form onSubmit={handleSearch}>
                  <Row>
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label>Search Query</Form.Label>
                        <Form.Control
                          type="text"
                          placeholder="e.g., high value shoppers, luxury automotive, tech enthusiasts"
                          value={searchQuery}
                          onChange={(e) => setSearchQuery(e.target.value)}
                          required
                        />
                      </Form.Group>
                    </Col>
                    <Col md={2}>
                      <Form.Group className="mb-3">
                        <Form.Label>Principal (Optional)</Form.Label>
                        <Form.Select
                          value={selectedPrincipal}
                          onChange={(e) => setSelectedPrincipal(e.target.value)}
                        >
                          {principalOptions.map(option => (
                            <option key={option.value} value={option.value}>
                              {option.label}
                            </option>
                          ))}
                        </Form.Select>
                      </Form.Group>
                    </Col>
                    <Col md={2}>
                      <Form.Group className="mb-3">
                        <Form.Label>Platforms (Optional)</Form.Label>
                        <Form.Select
                          multiple
                          value={selectedPlatforms}
                          onChange={(e) => setSelectedPlatforms(Array.from(e.target.selectedOptions, option => option.value))}
                        >
                          {platformOptions.map(platform => (
                            <option key={platform} value={platform}>
                              {platform}
                            </option>
                          ))}
                        </Form.Select>
                        <Form.Text className="text-muted">
                          Hold Ctrl/Cmd to select multiple
                        </Form.Text>
                      </Form.Group>
                    </Col>
                    <Col md={2}>
                      <Form.Group className="mb-3">
                        <Form.Label>Response Limit</Form.Label>
                        <Form.Select
                          value={selectedLimit}
                          onChange={(e) => setSelectedLimit(parseInt(e.target.value))}
                        >
                          {limitOptions.map(option => (
                            <option key={option.value} value={option.value}>
                              {option.label}
                            </option>
                          ))}
                        </Form.Select>
                        <Form.Text className="text-muted">
                          Number of proposals to return
                        </Form.Text>
                      </Form.Group>
                    </Col>
                  </Row>
                  <div className="text-center">
                    <Button 
                      type="submit" 
                      variant="primary" 
                      size="lg"
                      disabled={isSearching || !searchQuery.trim()}
                      className="me-3"
                    >
                      {isSearching ? (
                        <>
                          <Spinner
                            as="span"
                            animation="border"
                            size="sm"
                            role="status"
                            aria-hidden="true"
                            className="me-2"
                          />
                          Searching...
                        </>
                      ) : (
                        '🔍 Discover Signals'
                      )}
                    </Button>
                    
                    {/* Debug Toggle Button - only show if debug data exists */}
                    {debugData && (
                      <Button
                        variant="outline-secondary"
                        size="sm"
                        onClick={() => setShowDebugPanel(!showDebugPanel)}
                        className="d-flex align-items-center gap-1"
                        style={{ display: 'inline-flex' }}
                      >
                        <i className={`fas fa-${showDebugPanel ? 'eye-slash' : 'bug'}`}></i>
                        {showDebugPanel ? 'Hide Debug' : 'Debug'}
                        {debugData.validation_report?.validation_errors?.length > 0 && (
                          <Badge bg="warning" text="dark" className="ms-1">
                            {debugData.validation_report.validation_errors.length}
                          </Badge>
                        )}
                      </Button>
                    )}
                  </div>
                </Form>
              </Card.Body>
            </Card>
          </Col>
        </Row>

        {/* Search Error Alert */}
        {searchError && (
          <Row className="mb-4">
            <Col>
              <Alert variant="danger" dismissible onClose={() => setSearchError(null)}>
                <Alert.Heading>Search Failed</Alert.Heading>
                <p>{searchError}</p>
              </Alert>
            </Col>
          </Row>
        )}



        {/* Debug Panel */}
        {showDebugPanel && debugData && (
          <Row className="mb-4">
            <Col>
              <Card className="border-info">
                <Card.Header className="bg-info text-white">
                  <div className="d-flex justify-content-between align-items-center">
                    <div>
                      <i className="fas fa-bug me-2"></i>
                      <strong>Debug Information</strong>
                      <Badge bg="light" text="dark" className="ms-2">
                        {debugData.validation_report?.validation_errors?.length || 0} validation issues
                      </Badge>
                    </div>
                    <Button
                      variant="outline-light"
                      size="sm"
                      onClick={() => setShowDebugPanel(false)}
                    >
                      <i className="fas fa-times"></i>
                    </Button>
                  </div>
                </Card.Header>
                
                <Card.Body className="bg-light">
                    <div className="row">
                      <div className="col-md-6">
                        <h6>Validation Summary</h6>
                        <Table size="sm" borderless>
                          <tbody>
                            <tr>
                              <td><strong>Valid Proposals:</strong></td>
                              <td>
                                <Badge bg="success">
                                  {debugData.valid_proposals || 0}
                                </Badge>
                              </td>
                            </tr>
                            <tr>
                              <td><strong>Invalid Proposals:</strong></td>
                              <td>
                                <Badge bg="danger">
                                  {debugData.invalid_proposals || 0}
                                </Badge>
                              </td>
                            </tr>
                            <tr>
                              <td><strong>Total Proposals:</strong></td>
                              <td>
                                <Badge bg="info">
                                  {debugData.proposals_generated || 0}
                                </Badge>
                              </td>
                            </tr>
                            <tr>
                              <td><strong>Ranking Method:</strong></td>
                              <td>
                                <code>{debugData.ranking_method || 'N/A'}</code>
                              </td>
                            </tr>
                            <tr>
                              <td><strong>Generation Method:</strong></td>
                              <td>
                                <code>{debugData.generation_method || 'N/A'}</code>
                              </td>
                            </tr>
                          </tbody>
                        </Table>
                      </div>
                      <div className="col-md-6">
                        <h6>Query & Processing</h6>
                        <Table size="sm" borderless>
                          <tbody>
                            <tr>
                              <td><strong>Query Processed:</strong></td>
                              <td>
                                <code>{debugData.query_processed || 'N/A'}</code>
                              </td>
                            </tr>
                            <tr>
                              <td><strong>Limit Requested:</strong></td>
                              <td>
                                <Badge bg="secondary">
                                  {debugData.limit_requested || 'N/A'}
                                </Badge>
                              </td>
                            </tr>
                            <tr>
                              <td><strong>Candidate Signals:</strong></td>
                              <td>
                                <Badge bg="secondary">
                                  {debugData.candidate_signals_count || 'N/A'}
                                </Badge>
                              </td>
                            </tr>
                            <tr>
                              <td><strong>Ranked Signals:</strong></td>
                              <td>
                                <Badge bg="secondary">
                                  {debugData.ranked_signals_count || 'N/A'}
                                </Badge>
                              </td>
                            </tr>
                            <tr>
                              <td><strong>Using Fallback:</strong></td>
                              <td>
                                <Badge bg={debugData.using_fallback ? 'warning' : 'success'}>
                                  {debugData.using_fallback ? 'Yes' : 'No'}
                                </Badge>
                              </td>
                            </tr>
                          </tbody>
                        </Table>
                      </div>
                    </div>

                    {debugData.validation_report?.validation_errors && debugData.validation_report.validation_errors.length > 0 && (
                      <div className="mt-3">
                        <h6>Validation Errors</h6>
                        <Alert variant="warning">
                          <ul className="mb-0">
                            {debugData.validation_report.validation_errors.map((error, idx) => (
                              <li key={idx}>{error}</li>
                            ))}
                          </ul>
                        </Alert>
                      </div>
                    )}

                    {debugData.validation_report?.debug_info && (
                      <div className="mt-3">
                        <h6>Validation Debug Info</h6>
                        <Table size="sm" borderless>
                          <tbody>
                            <tr>
                              <td><strong>Debug Mode:</strong></td>
                              <td>
                                <Badge bg={debugData.validation_report.debug_info.debug_mode ? 'success' : 'secondary'}>
                                  {debugData.validation_report.debug_info.debug_mode ? 'Enabled' : 'Disabled'}
                                </Badge>
                              </td>
                            </tr>
                            <tr>
                              <td><strong>Rules Applied:</strong></td>
                              <td>
                                {debugData.validation_report.debug_info.validation_rules_applied?.map(rule => (
                                  <Badge key={rule} bg="info" size="sm" className="me-1">
                                    {rule}
                                  </Badge>
                                ))}
                              </td>
                            </tr>
                          </tbody>
                        </Table>
                      </div>
                    )}

                    <div className="mt-3">
                      <h6>Raw Debug Data</h6>
                      <pre className="bg-dark text-light p-3 rounded" style={{ fontSize: '0.8rem', maxHeight: '200px', overflow: 'auto' }}>
                        <code>{formatDetails(debugData)}</code>
                      </pre>
                    </div>
                  </Card.Body>
                )}
              </Card>
            </Col>
          </Row>
        )}

        {/* Results Area */}
        <Row>
          {/* Matches Table */}
          <Col md={6}>
            <Card className="mb-4 shadow">
              <Card.Header className="bg-primary text-white">
                <div className="d-flex justify-content-between align-items-center">
                  <h4 className="mb-0">
                    📊 Signal Matches 
                    <Badge bg="light" text="dark" className="ms-2">
                      {matches.length}
                    </Badge>
                  </h4>
                  {discoveryResponse?.using_fallback && (
                    <Badge bg="warning" text="dark">
                      ⚠️ Fallback Mode
                    </Badge>
                  )}
                </div>
              </Card.Header>
              <Card.Body>
                {isSearching ? (
                  <div className="text-center py-4">
                    <Spinner animation="border" role="status">
                      <span className="visually-hidden">Loading...</span>
                    </Spinner>
                    <p className="mt-2 text-muted">Searching for signals...</p>
                  </div>
                ) : matches.length > 0 ? (
                  <div>
                    {matches.map((match, index) => (
                      <Card key={index} className="mb-3 shadow-sm">
                        <Card.Header 
                          className="d-flex justify-content-between align-items-center cursor-pointer bg-light"
                          onClick={() => toggleMatchExpanded(match.id)}
                          style={{ cursor: 'pointer' }}
                        >
                          <div className="d-flex align-items-center">
                            <i className={`fas fa-chevron-${expandedMatches.has(match.id) ? 'down' : 'right'} me-2`}></i>
                            <div>
                              <strong>{match.name}</strong>
                              <br />
                              <small className="text-muted">{match.id}</small>
                            </div>
                          </div>
                          <div className="d-flex align-items-center gap-3">
                            <span className="text-muted">{match.data_provider}</span>
                            <span className="text-muted">{typeof match.coverage_percentage === 'number' ? match.coverage_percentage.toFixed(2) : match.coverage_percentage}%</span>
                            <span className="text-muted">
                              {match.base_cpm ? `$${match.base_cpm}` : 'N/A'}
                            </span>
                            <div>
                              {match.allowed_platforms && match.allowed_platforms.length > 0 ? (
                                <div className="d-flex flex-wrap gap-2">
                                  {match.allowed_platforms.slice(0, 2).map(platform => (
                                    <Badge key={platform} bg="secondary" size="sm" className="me-1 mb-1">
                                      {platform}
                                    </Badge>
                                  ))}
                                  {match.allowed_platforms.length > 2 && (
                                    <Badge bg="light" text="dark" size="sm" className="me-1 mb-1">
                                      +{match.allowed_platforms.length - 2}
                                    </Badge>
                                  )}
                                </div>
                              ) : (
                                <span className="text-muted">N/A</span>
                              )}
                            </div>
                            <Button 
                              size="sm" 
                              variant="outline-primary"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleActivate(match.id);
                              }}
                            >
                              Activate
                            </Button>
                          </div>
                        </Card.Header>
                        
                        {expandedMatches.has(match.id) && (
                          <Card.Body className="bg-light p-4">
                            <div className="row g-4">
                              <div className="col-md-6">
                                <h6 className="mb-3 text-primary">Basic Information</h6>
                                <Table size="sm" borderless className="table-details">
                                  <tbody>
                                    <tr className="mb-3">
                                      <td className="fw-bold pe-3" style={{ width: '30%', verticalAlign: 'top' }}>ID:</td>
                                      <td>
                                        <div className="d-flex align-items-center">
                                          <code className="me-2">{match.id}</code>
                                          <Button 
                                            size="sm" 
                                            variant="outline-secondary" 
                                            onClick={() => copyToClipboard(match.id)}
                                          >
                                            📋 Copy
                                          </Button>
                                        </div>
                                      </td>
                                    </tr>
                                    <tr className="mb-3">
                                      <td className="fw-bold pe-3" style={{ width: '30%', verticalAlign: 'top' }}>Name:</td>
                                      <td className="text-break">{match.name}</td>
                                    </tr>
                                    <tr className="mb-3">
                                      <td className="fw-bold pe-3" style={{ width: '30%', verticalAlign: 'top' }}>Provider:</td>
                                      <td>{match.data_provider}</td>
                                    </tr>
                                    <tr className="mb-3">
                                      <td className="fw-bold pe-3" style={{ width: '30%', verticalAlign: 'top' }}>Description:</td>
                                      <td className="text-break">{match.description}</td>
                                    </tr>
                                    <tr className="mb-3">
                                      <td className="fw-bold pe-3" style={{ width: '30%', verticalAlign: 'top' }}>Signal Type:</td>
                                      <td>{match.signal_type}</td>
                                    </tr>
                                    <tr className="mb-3">
                                      <td className="fw-bold pe-3" style={{ width: '30%', verticalAlign: 'top' }}>Catalog Access:</td>
                                      <td>{match.catalog_access}</td>
                                    </tr>
                                  </tbody>
                                </Table>
                              </div>
                              <div className="col-md-6">
                                <h6 className="mb-3 text-primary">Metrics & Platforms</h6>
                                <Table size="sm" borderless className="table-details">
                                  <tbody>
                                    <tr className="mb-3">
                                      <td className="fw-bold pe-3" style={{ width: '30%', verticalAlign: 'top' }}>Coverage:</td>
                                      <td>{typeof match.coverage_percentage === 'number' ? match.coverage_percentage.toFixed(2) : match.coverage_percentage}%</td>
                                    </tr>
                                    <tr className="mb-3">
                                      <td className="fw-bold pe-3" style={{ width: '30%', verticalAlign: 'top' }}>Base CPM:</td>
                                      <td>{match.base_cpm ? `$${match.base_cpm}` : 'N/A'}</td>
                                    </tr>
                                    <tr className="mb-3">
                                      <td className="fw-bold pe-3" style={{ width: '30%', verticalAlign: 'top' }}>Valid:</td>
                                      <td>
                                        <Badge bg={match.valid ? 'success' : 'danger'}>
                                          {match.valid ? 'Yes' : 'No'}
                                        </Badge>
                                      </td>
                                    </tr>
                                    <tr className="mb-3">
                                      <td className="fw-bold pe-3" style={{ width: '30%', verticalAlign: 'top' }}>Platforms:</td>
                                      <td>
                                        {match.allowed_platforms && match.allowed_platforms.length > 0 ? (
                                          <div className="d-flex flex-wrap gap-2">
                                            {match.allowed_platforms.map(platform => (
                                              <Badge key={platform} bg="secondary" size="sm" className="me-1 mb-1">
                                                {platform}
                                              </Badge>
                                            ))}
                                          </div>
                                        ) : (
                                          <span className="text-muted">None</span>
                                        )}
                                      </td>
                                    </tr>
                                  </tbody>
                                </Table>
                              </div>
                            </div>
                            
                            <div className="mt-4">
                              <h6 className="mb-3 text-primary">Raw Data</h6>
                              <pre className="bg-dark text-light p-3 rounded" style={{ fontSize: '0.8rem', maxHeight: '200px', overflow: 'auto' }}>
                                <code>{formatDetails(match)}</code>
                              </pre>
                            </div>
                          </Card.Body>
                        )}
                      </Card>
                    ))}
                  </div>
                ) : (
                  <div className="text-center text-muted py-4">
                    <p>No matches found. Try searching for signals.</p>
                  </div>
                )}
              </Card.Body>
            </Card>
          </Col>

          {/* Proposals Table */}
          <Col md={6}>
            <Card className="mb-4 shadow">
              <Card.Header className="bg-info text-white">
                <div className="d-flex justify-content-between align-items-center">
                  <h4 className="mb-0">
                    💡 AI Proposals 
                    <Badge bg="light" text="dark" className="ms-2">
                      {proposals.length}
                    </Badge>
                  </h4>
                  {discoveryResponse?.using_fallback && (
                    <Badge bg="warning" text="dark">
                      ⚠️ Fallback Mode
                    </Badge>
                  )}
                </div>
              </Card.Header>
              <Card.Body>
                {isSearching ? (
                  <div className="text-center py-4">
                    <Spinner animation="border" role="status">
                      <span className="visually-hidden">Loading...</span>
                    </Spinner>
                    <p className="mt-2 text-muted">Generating proposals...</p>
                  </div>
                ) : proposals.length > 0 ? (
                  <div>
                    {proposals.map((proposal, index) => (
                      <Card key={index} className="mb-3 shadow-sm">
                        <Card.Header 
                          className="d-flex justify-content-between align-items-center cursor-pointer bg-light"
                          onClick={() => toggleProposalExpanded(proposal.id)}
                          style={{ cursor: 'pointer' }}
                        >
                          <div className="d-flex align-items-center">
                            <i className={`fas fa-chevron-${expandedProposals.has(proposal.id) ? 'down' : 'right'} me-2`}></i>
                            <div>
                              <strong>{proposal.name}</strong>
                              <br />
                              <small className="text-muted">{proposal.id}</small>
                            </div>
                          </div>
                          <div className="d-flex align-items-center gap-3">
                            <Badge bg={proposal.valid ? 'success' : 'danger'}>
                              {proposal.valid ? '✓ Valid' : '✗ Invalid'}
                            </Badge>
                            <div>
                              {proposal.platforms && proposal.platforms.length > 0 ? (
                                <div className="d-flex flex-wrap gap-1">
                                  {proposal.platforms.slice(0, 2).map(platform => (
                                    <Badge key={platform} bg="secondary" size="sm">
                                      {platform}
                                    </Badge>
                                  ))}
                                  {proposal.platforms.length > 2 && (
                                    <Badge bg="light" text="dark" size="sm">
                                      +{proposal.platforms.length - 2}
                                    </Badge>
                                  )}
                                </div>
                              ) : (
                                <span className="text-muted">N/A</span>
                              )}
                            </div>
                            <div className="text-muted small">
                              {proposal.signal_ids?.length || 0} signals, {proposal.logic || 'N/A'} logic
                            </div>
                            <Button 
                              size="sm" 
                              variant="outline-success"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleActivate(proposal.id);
                              }}
                              disabled={!proposal.valid}
                            >
                              Activate
                            </Button>
                          </div>
                        </Card.Header>
                        
                        {expandedProposals.has(proposal.id) && (
                          <Card.Body className="bg-light p-4">
                            <div className="row g-4">
                              <div className="col-md-6">
                                <h6 className="mb-3 text-primary">Basic Information</h6>
                                <Table size="sm" borderless className="table-details">
                                  <tbody>
                                    <tr className="mb-3">
                                      <td className="fw-bold pe-3" style={{ width: '30%', verticalAlign: 'top' }}>ID:</td>
                                      <td>
                                        <div className="d-flex align-items-center">
                                          <code className="me-2">{proposal.id}</code>
                                          <Button 
                                            size="sm" 
                                            variant="outline-secondary" 
                                            onClick={() => copyToClipboard(proposal.id)}
                                          >
                                            📋 Copy
                                          </Button>
                                        </div>
                                      </td>
                                    </tr>
                                    <tr className="mb-3">
                                      <td className="fw-bold pe-3" style={{ width: '30%', verticalAlign: 'top' }}>Name:</td>
                                      <td className="text-break">{proposal.name}</td>
                                    </tr>
                                    <tr className="mb-3">
                                      <td className="fw-bold pe-3" style={{ width: '30%', verticalAlign: 'top' }}>Description:</td>
                                      <td className="text-break">{proposal.description || 'N/A'}</td>
                                    </tr>
                                    <tr className="mb-3">
                                      <td className="fw-bold pe-3" style={{ width: '30%', verticalAlign: 'top' }}>Logic:</td>
                                      <td>
                                        <Badge bg={proposal.logic === 'OR' ? 'success' : 'warning'}>
                                          {proposal.logic}
                                        </Badge>
                                      </td>
                                    </tr>
                                    <tr className="mb-3">
                                      <td className="fw-bold pe-3" style={{ width: '30%', verticalAlign: 'top' }}>Valid:</td>
                                      <td>
                                        <Badge bg={proposal.valid ? 'success' : 'danger'}>
                                          {proposal.valid ? 'Yes' : 'No'}
                                        </Badge>
                                      </td>
                                    </tr>
                                    <tr className="mb-3">
                                      <td className="fw-bold pe-3" style={{ width: '30%', verticalAlign: 'top' }}>Score:</td>
                                      <td>{proposal.score || 'N/A'}</td>
                                    </tr>
                                  </tbody>
                                </Table>
                              </div>
                              <div className="col-md-6">
                                <h6 className="mb-3 text-primary">Signals & Platforms</h6>
                                <Table size="sm" borderless className="table-details">
                                  <tbody>
                                    <tr className="mb-3">
                                      <td className="fw-bold pe-3" style={{ width: '30%', verticalAlign: 'top' }}>Signal Count:</td>
                                      <td>{proposal.signal_ids?.length || 0}</td>
                                    </tr>
                                    <tr className="mb-3">
                                      <td className="fw-bold pe-3" style={{ width: '30%', verticalAlign: 'top' }}>Signal IDs:</td>
                                      <td>
                                        {proposal.signal_ids && proposal.signal_ids.length > 0 ? (
                                          <div className="d-flex flex-wrap gap-2">
                                            {proposal.signal_ids.map(signalId => (
                                              <Badge key={signalId} bg="info" size="sm" className="me-1 mb-1">
                                                {signalId}
                                              </Badge>
                                            ))}
                                          </div>
                                        ) : (
                                          <span className="text-muted">None</span>
                                        )}
                                      </td>
                                    </tr>
                                    <tr>
                                      <td><strong>Platforms:</strong></td>
                                      <td>
                                        {proposal.platforms && proposal.platforms.length > 0 ? (
                                          <div className="d-flex flex-wrap gap-2">
                                            {proposal.platforms.map(platform => (
                                              <Badge key={platform} bg="secondary" size="sm" className="me-1 mb-1">
                                                {platform}
                                              </Badge>
                                            ))}
                                          </div>
                                        ) : (
                                          <span className="text-muted">None</span>
                                        )}
                                      </td>
                                    </tr>
                                    <tr>
                                      <td><strong>Reasoning:</strong></td>
                                      <td>
                                        <small className="text-muted">
                                          {proposal.reasoning || 'N/A'}
                                        </small>
                                      </td>
                                    </tr>
                                  </tbody>
                                </Table>
                              </div>
                            </div>
                            
                            {proposal.validation_errors && proposal.validation_errors.length > 0 && (
                              <div className="mt-3">
                                <h6>Validation Errors</h6>
                                <Alert variant="danger">
                                  <ul className="mb-0">
                                    {proposal.validation_errors.map((error, idx) => (
                                      <li key={idx}>{error}</li>
                                    ))}
                                  </ul>
                                </Alert>
                              </div>
                            )}
                            
                            {proposal.metadata && Object.keys(proposal.metadata).length > 0 && (
                              <div className="mt-3">
                                <h6>Metadata</h6>
                                <pre className="bg-dark text-light p-3 rounded" style={{ fontSize: '0.8rem', maxHeight: '150px', overflow: 'auto' }}>
                                  <code>{formatDetails(proposal.metadata)}</code>
                                </pre>
                              </div>
                            )}
                            
                            <div className="mt-3">
                              <h6>Raw Data</h6>
                              <pre className="bg-dark text-light p-3 rounded" style={{ fontSize: '0.8rem', maxHeight: '200px', overflow: 'auto' }}>
                                <code>{formatDetails(proposal)}</code>
                              </pre>
                            </div>
                          </Card.Body>
                        )}
                      </Card>
                    ))}
                  </div>
                ) : (
                  <div className="text-center text-muted py-4">
                    <p>No proposals found. Try searching for signals.</p>
                  </div>
                )}
              </Card.Body>
            </Card>
          </Col>
        </Row>

        {/* API Health Status */}
        <Row>
          <Col>
            <Card className="border-secondary">
              <Card.Header>
                <h5 className="mb-0">🔌 Backend Status</h5>
              </Card.Header>
              <Card.Body>
                <Button 
                  onClick={testHealth} 
                  disabled={loading}
                  variant="outline-secondary"
                  size="sm"
                  className="me-3"
                >
                  {loading ? 'Testing...' : 'Test Connection'}
                </Button>
                
                {healthStatus && (
                  <Badge bg="success" className="me-2">
                    ✅ Connected ({healthStatus.mode})
                  </Badge>
                )}
                
                {error && (
                  <Badge bg="danger">
                    ❌ {error}
                  </Badge>
                )}
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>

      {/* Status Drawer */}
      <Offcanvas
        show={showStatusDrawer}
        onHide={() => setShowStatusDrawer(false)}
        placement="end"
        size="lg"
      >
        <Offcanvas.Header closeButton>
          <Offcanvas.Title>📊 Activation Status</Offcanvas.Title>
        </Offcanvas.Header>
        <Offcanvas.Body>
          <div className="text-center text-muted py-5">
            <h4>Status Drawer Placeholder</h4>
            <p>Activation ID: {selectedActivationId}</p>
            <p>Status tracking functionality will be implemented here.</p>
          </div>
        </Offcanvas.Body>
      </Offcanvas>

      {/* Toast Container */}
      <ToastContainer position="top-end" className="p-3">
        {toasts.map(toast => (
          <Toast
            key={toast.id}
            onClose={() => removeToast(toast.id)}
            bg={toast.variant}
            delay={5000}
            autohide
          >
            <Toast.Header>
              <strong className="me-auto">Signals Agent</strong>
            </Toast.Header>
            <Toast.Body className={toast.variant === 'dark' ? 'text-white' : ''}>
              {toast.message}
            </Toast.Body>
          </Toast>
        ))}
      </ToastContainer>
    </>
  );
}

export default Discovery;
