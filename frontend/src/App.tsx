import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import TagSelector from './pages/TagSelector';
import GamePage from './pages/GamePage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<TagSelector />} />
        <Route path="/game" element={<GamePage />} />
      </Routes>
    </Router>
  );
}

export default App;
