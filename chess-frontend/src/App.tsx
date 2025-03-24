import React from 'react';
import ChessBoard from './components/ChessBoard';
import { getAIMove } from './services/aiService';
import './App.css';

function App() {
  const handleMove = async (fen: string) => {
    try {
      const aiMove = await getAIMove(fen);
      console.log('AI Move:', aiMove);
      // You can implement the AI move here
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <div className="App">
      <main>
        <ChessBoard onMove={handleMove} />
      </main>
    </div>
  );
}

export default App;
