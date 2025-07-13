import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import styled from 'styled-components';

const Container = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
`;

function App() {
  return (
    <Router>
      <Container>
        <Routes>
          <Route path="/" element={<HomePage />} />
        </Routes>
      </Container>
    </Router>
  );
}

function HomePage() {
  return <h1>Welcome to {{app_name}}</h1>;
}

export default App;