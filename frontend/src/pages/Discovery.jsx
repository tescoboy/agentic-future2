import { useState, useEffect } from 'react'
import { 
  Container, 
  Row, 
  Col, 
  Card, 
  Button, 
  Form, 
  Badge, 
  Spinner, 
  Alert, 
  Table,
  Toast,
  ToastContainer
} from 'react-bootstrap'
import { apiClient } from '../services/api'

function Discovery() {
  // State
  const [searchQuery, setSearchQuery] = useState('shoppers')
  const [selectedPrincipal, setSelectedPrincipal] = useState('Public Access')
  const [selectedPlatforms, setSelectedPlatforms] = useState([])
  const [selectedLimit, setSelectedLimit] = useState(5)
  const [isSearching, setIsSearching] = useState(false)
  const [matches, setMatches] = useState([])
  const [proposals, setProposals] = useState([])
  const [discoveryResponse, setDiscoveryResponse] = useState(null)
  const [showDebugPanel, setShowDebugPanel] = useState(false)
  const [toasts, setToasts] = useState([])
  const [backendStatus, setBackendStatus] = useState(null)

  // Options
  const principalOptions = ['Public Access', 'Private Access', 'Premium Access']
  const platformOptions = [
    'index-exchange', 'the-trade-desk', 'openx', 'pubmatic', 
    'google-ads', 'dv360', 'amazon', 'xandr', 'criteo'
  ]
  const limitOptions = [1, 3, 5, 8, 10]

  useEffect(() => {
    testHealth()
  }, [])

  const testHealth = async () => {
    try {
      await apiClient.getHealth()
      setBackendStatus({ connected: true, message: 'Connected (demo)', variant: 'success' })
    } catch (error) {
      setBackendStatus({ connected: false, message: 'Connection failed', variant: 'danger' })
    }
  }

  const handleSearch = async (e) => {
    e.preventDefault()
    setIsSearching(true)
    setShowDebugPanel(false)

    try {
      const response = await apiClient.postDiscovery({
        query: searchQuery,
        principal_id: selectedPrincipal === 'Public Access' ? null : selectedPrincipal,
        platforms: selectedPlatforms.length > 0 ? selectedPlatforms : null,
        limit: selectedLimit
      })

      setMatches(response.matches || [])
      setProposals(response.proposals || [])
      setDiscoveryResponse(response)
      
      if (response.debug_data) {
        setShowDebugPanel(true)
      }

      addToast('success', `Found ${response.matches?.length || 0} signals and ${response.proposals?.length || 0} proposals`)
    } catch (error) {
      console.error('Search error:', error)
      addToast('danger', `Search failed: ${getErrorMessage(error)}`)
    } finally {
      setIsSearching(false)
    }
  }

  const handleActivate = (signalId) => {
    addToast('info', `Activation requested for signal: ${signalId}`)
  }

  const addToast = (variant, message) => {
    const id = Date.now()
    setToasts(prev => [...prev, { id, variant, message }])
  }

  const removeToast = (id) => {
    setToasts(prev => prev.filter(toast => toast.id !== id))
  }

  const copyToClipboard = async (text) => {
    try {
      await navigator.clipboard.writeText(text)
      addToast('success', 'Copied to clipboard!')
    } catch (error) {
      addToast('danger', 'Failed to copy to clipboard')
    }
  }

  const formatDetails = (obj) => {
    return JSON.stringify(obj, null, 2)
  }

  const getErrorMessage = (error) => {
    return error.response?.data?.detail || error.message || 'Unknown error'
  }

  const hasDebugData = (response) => {
    return response?.debug_data || response?.validation_report
  }

  const formatPercentage = (value) => {
    if (typeof value === 'number') {
      return value.toFixed(2)
    }
    return value
  }

  return (
    <div className="bg-light min-vh-100">
      {/* Header */}
      <nav className="navbar navbar-dark bg-dark mb-4">
        <div className="container">
          <span className="navbar-brand mb-0 h1">
            <i className="fas fa-chart-line me-2"></i>
            Signals Agent UI
          </span>
          <span className="navbar-text">
            API: {import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'}
          </span>
        </div>
      </nav>

      <Container className="py-4">
        {/* Toast Notifications */}
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
                <strong className="me-auto">Notification</strong>
              </Toast.Header>
              <Toast.Body className={toast.variant === 'dark' ? 'text-white' : ''}>
                {toast.message}
              </Toast.Body>
            </Toast>
          ))}
        </ToastContainer>

        {/* Search Form */}
        <Card className="mb-4">
          <Card.Header className="bg-primary text-white">
            <h5 className="mb-0">
              <i className="fas fa-search me-2"></i>
              Signal Discovery
            </h5>
          </Card.Header>
          <Card.Body>
            <Form onSubmit={handleSearch}>
              <Row className="g-3">
                <Col md={4}>
                  <Form.Group>
                    <Form.Label>Search Query</Form.Label>
                    <Form.Control
                      type="text"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      placeholder="Enter search terms..."
                      required
                    />
                  </Form.Group>
                </Col>
                <Col md={2}>
                  <Form.Group>
                    <Form.Label>Principal</Form.Label>
                    <Form.Select
                      value={selectedPrincipal}
                      onChange={(e) => setSelectedPrincipal(e.target.value)}
                    >
                      {principalOptions.map(option => (
                        <option key={option} value={option}>{option}</option>
                      ))}
                    </Form.Select>
                  </Form.Group>
                </Col>
                <Col md={3}>
                  <Form.Group>
                    <Form.Label>Platforms</Form.Label>
                    <Form.Select
                      multiple
                      value={selectedPlatforms}
                      onChange={(e) => setSelectedPlatforms(Array.from(e.target.selectedOptions, option => option.value))}
                      size="3"
                    >
                      {platformOptions.map(platform => (
                        <option key={platform} value={platform}>{platform}</option>
                      ))}
                    </Form.Select>
                    <Form.Text className="text-muted">
                      Hold Ctrl/Cmd to select multiple
                    </Form.Text>
                  </Form.Group>
                </Col>
                <Col md={2}>
                  <Form.Group>
                    <Form.Label>Response Limit</Form.Label>
                    <Form.Select
                      value={selectedLimit}
                      onChange={(e) => setSelectedLimit(parseInt(e.target.value))}
                    >
                      {limitOptions.map(limit => (
                        <option key={limit} value={limit}>{limit} proposals</option>
                      ))}
                    </Form.Select>
                  </Form.Group>
                </Col>
                <Col md={1} className="d-flex align-items-end">
                  <div className="d-flex gap-2 w-100">
                    {hasDebugData(discoveryResponse) && (
                      <Button
                        variant={showDebugPanel ? "warning" : "outline-secondary"}
                        size="sm"
                        onClick={() => setShowDebugPanel(!showDebugPanel)}
                        className="flex-fill"
                        title="Toggle Debug Information"
                      >
                        <i className="fas fa-bug"></i>
                      </Button>
                    )}
                    <Button
                      type="submit"
                      variant="primary"
                      disabled={isSearching}
                      className="flex-fill"
                    >
                      {isSearching ? (
                        <>
                          <Spinner animation="border" size="sm" className="me-2" />
                          Searching...
                        </>
                      ) : (
                        <>
                          <i className="fas fa-search me-2"></i>
                          Discover
                        </>
                      )}
                    </Button>
                  </div>
                </Col>
              </Row>
            </Form>
          </Card.Body>
        </Card>

        {/* Debug Panel */}
        {showDebugPanel && discoveryResponse?.debug_data && (
          <Card className="mb-4 border-warning">
            <Card.Header className="bg-warning text-dark">
              <h6 className="mb-0">
                <i className="fas fa-bug me-2"></i>
                Debug Information
              </h6>
            </Card.Header>
            <Card.Body>
              <Row>
                <Col md={6}>
                  <h6 className="text-muted mb-2">API Response</h6>
                  <pre className="bg-dark text-light p-3 rounded" style={{ fontSize: '0.75rem', maxHeight: '200px', overflow: 'auto' }}>
                    <code>{formatDetails(discoveryResponse)}</code>
                  </pre>
                </Col>
                <Col md={6}>
                  <h6 className="text-muted mb-2">Raw Debug Data</h6>
                  <pre className="bg-dark text-light p-3 rounded" style={{ fontSize: '0.75rem', maxHeight: '200px', overflow: 'auto' }}>
                    <code>{formatDetails(discoveryResponse.debug_data)}</code>
                  </pre>
                </Col>
              </Row>
            </Card.Body>
          </Card>
        )}

        {/* Results Section */}
        {matches.length > 0 || proposals.length > 0 ? (
          <Row className="g-4">
            {/* Signal Matches */}
            <Col lg={6}>
              <Card className="h-100">
                <Card.Header className="bg-success text-white">
                  <div className="d-flex justify-content-between align-items-center">
                    <h5 className="mb-0">
                      <i className="fas fa-chart-bar me-2"></i>
                      Signal Matches
                    </h5>
                    <Badge bg="light" text="dark">
                      {matches.length}
                    </Badge>
                  </div>
                </Card.Header>
                <Card.Body className="p-0">
                  {matches.length > 0 ? (
                    <div className="list-group list-group-flush">
                      {matches.map((match, index) => (
                        <div key={index} className="list-group-item">
                          <div className="d-flex justify-content-between align-items-start mb-2">
                            <div className="flex-grow-1">
                              <h6 className="mb-1">{match.name}</h6>
                              <small className="text-muted">{match.id}</small>
                            </div>
                            <div className="d-flex align-items-center gap-2">
                              <Badge bg="info">
                                {formatPercentage(match.coverage_percentage)}%
                              </Badge>
                              <Button
                                size="sm"
                                variant="outline-success"
                                onClick={() => handleActivate(match.id)}
                              >
                                <i className="fas fa-play me-1"></i>
                                Activate
                              </Button>
                            </div>
                          </div>
                          
                          <div className="mb-2">
                            <strong>Provider:</strong> {match.data_provider}
                          </div>
                          
                          <div className="mb-2">
                            <strong>Description:</strong> {match.description}
                          </div>
                          
                          <div className="mb-2">
                            <strong>Base CPM:</strong> {match.base_cpm ? `$${match.base_cpm}` : 'N/A'}
                          </div>
                          
                          <div className="mb-2">
                            <strong>Valid:</strong> 
                            <Badge bg={match.valid ? 'success' : 'danger'} className="ms-2">
                              {match.valid ? 'Yes' : 'No'}
                            </Badge>
                          </div>
                          
                          <div>
                            <strong>Platforms:</strong>
                            <div className="mt-1">
                              {match.allowed_platforms?.map(platform => (
                                <Badge key={platform} bg="secondary" className="me-1 mb-1">
                                  {platform}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-5 text-muted">
                      <i className="fas fa-search fa-3x mb-3"></i>
                      <p>No signal matches found</p>
                    </div>
                  )}
                </Card.Body>
              </Card>
            </Col>

            {/* AI Proposals */}
            <Col lg={6}>
              <Card className="h-100">
                <Card.Header className="bg-info text-white">
                  <div className="d-flex justify-content-between align-items-center">
                    <h5 className="mb-0">
                      <i className="fas fa-lightbulb me-2"></i>
                      AI Proposals
                    </h5>
                    <Badge bg="light" text="dark">
                      {proposals.length}
                    </Badge>
                  </div>
                </Card.Header>
                <Card.Body className="p-0">
                  {proposals.length > 0 ? (
                    <div className="list-group list-group-flush">
                      {proposals.map((proposal, index) => (
                        <div key={index} className="list-group-item">
                          <div className="d-flex justify-content-between align-items-start mb-2">
                            <div className="flex-grow-1">
                              <h6 className="mb-1">{proposal.name}</h6>
                              <small className="text-muted">{proposal.id}</small>
                            </div>
                            <div className="d-flex align-items-center gap-2">
                              <Badge bg={proposal.valid ? 'success' : 'danger'}>
                                {proposal.valid ? 'Valid' : 'Invalid'}
                              </Badge>
                              <Button
                                size="sm"
                                variant="outline-info"
                                onClick={() => handleActivate(proposal.id)}
                              >
                                <i className="fas fa-play me-1"></i>
                                Activate
                              </Button>
                            </div>
                          </div>
                          
                          <div className="mb-2">
                            <strong>Logic:</strong> 
                            <Badge bg={proposal.logic === 'OR' ? 'success' : 'warning'} className="ms-2">
                              {proposal.logic}
                            </Badge>
                          </div>
                          
                          <div className="mb-2">
                            <strong>Score:</strong> {proposal.score || 'N/A'}
                          </div>
                          
                          <div className="mb-2">
                            <strong>Signal Count:</strong> {proposal.signal_ids?.length || 0}
                          </div>
                          
                          <div className="mb-2">
                            <strong>Reasoning:</strong> {proposal.reasoning || 'N/A'}
                          </div>
                          
                          <div>
                            <strong>Platforms:</strong>
                            <div className="mt-1">
                              {proposal.platforms?.map(platform => (
                                <Badge key={platform} bg="secondary" className="me-1 mb-1">
                                  {platform}
                                </Badge>
                              ))}
                            </div>
                          </div>
                          
                          {proposal.validation_errors && proposal.validation_errors.length > 0 && (
                            <Alert variant="danger" className="mt-3">
                              <h6 className="mb-2">Validation Errors</h6>
                              <ul className="mb-0">
                                {proposal.validation_errors.map((error, idx) => (
                                  <li key={idx}>{error}</li>
                                ))}
                              </ul>
                            </Alert>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-5 text-muted">
                      <i className="fas fa-lightbulb fa-3x mb-3"></i>
                      <p>No AI proposals generated</p>
                    </div>
                  )}
                </Card.Body>
              </Card>
            </Col>
          </Row>
        ) : (
          <Card className="text-center py-5">
            <Card.Body>
              <i className="fas fa-search fa-4x text-muted mb-4"></i>
              <h4 className="text-muted mb-3">Ready to Discover Signals</h4>
              <p className="text-muted mb-0">
                Enter a search query above to find relevant signals and AI-generated proposals.
              </p>
            </Card.Body>
          </Card>
        )}

        {/* Backend Status */}
        <Card className="mt-4">
          <Card.Header className="bg-secondary text-white">
            <h6 className="mb-0">
              <i className="fas fa-database me-2"></i>
              Backend Status
            </h6>
          </Card.Header>
          <Card.Body>
            <div className="d-flex justify-content-between align-items-center">
              <div>
                {backendStatus ? (
                  <Badge bg={backendStatus.variant}>
                    <i className={`fas fa-${backendStatus.connected ? 'check-circle' : 'times-circle'} me-2`}></i>
                    {backendStatus.message}
                  </Badge>
                ) : (
                  <Badge bg="warning">
                    <i className="fas fa-question-circle me-2"></i>
                    Checking connection...
                  </Badge>
                )}
              </div>
              <Button
                variant="outline-secondary"
                size="sm"
                onClick={testHealth}
              >
                <i className="fas fa-sync-alt me-2"></i>
                Test Connection
              </Button>
            </div>
          </Card.Body>
        </Card>
      </Container>

      {/* Footer */}
      <footer className="bg-dark text-light text-center py-3 mt-5">
        <small>Powered by Ad Context Protocol</small>
      </footer>
    </div>
  )
}

export default Discovery
