import { Container } from 'react-bootstrap';

function Footer() {
  return (
    <footer className="mt-auto py-3 bg-light border-top">
      <Container>
        <div className="text-center">
          <small className="text-muted">
            Powered by Ad Context Protocol
          </small>
        </div>
      </Container>
    </footer>
  );
}

export default Footer;
