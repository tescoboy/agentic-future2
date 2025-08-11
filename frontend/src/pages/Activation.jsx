import { Container, Row, Col, Card } from 'react-bootstrap';

function Activation() {
  return (
    <Container>
      <Row className="justify-content-center">
        <Col md={10}>
          <Card>
            <Card.Header>
              <h2 className="mb-0">Signal Activation</h2>
            </Card.Header>
            <Card.Body>
              <p className="text-muted">
                This is the Activation page placeholder. 
                Signal activation functionality will be implemented here.
              </p>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
}

export default Activation;
