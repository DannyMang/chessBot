import React, { useState } from 'react';
import ChessBoard from './components/ChessBoard';
import GameSetup from './components/GameSetup';
import { getAIMove } from './services/aiService';
import './App.css';

type GameState = 'setup' | 'playing';

function App() {
  const [gameState, setGameState] = useState<GameState>('setup');
  const [playerColor, setPlayerColor] = useState<'white' | 'black'>('white');

  const handleGameStart = (color: 'white' | 'black') => {
    setPlayerColor(color);
    setGameState('playing');
  };

  const handleBackToSetup = () => {
    setGameState('setup');
  };

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
        {gameState === 'setup' ? (
          <GameSetup onGameStart={handleGameStart} />
        ) : (
          <ChessBoard 
            onMove={handleMove} 
            playerColor={playerColor}
            onBackToSetup={handleBackToSetup}
          />
        )}
      </main>
    </div>
  );
}

export default App;
