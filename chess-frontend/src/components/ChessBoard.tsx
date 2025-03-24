import { useState, useCallback } from 'react';
import { Chess } from 'chess.js';
import { Chessboard } from 'react-chessboard';

export {};

interface ChessBoardProps {
  onMove?: (move: string) => void;
}

export default function ChessBoard({ onMove }: ChessBoardProps) {
  const [game, setGame] = useState(new Chess());
  const [backendResponse, setBackendResponse] = useState<any>(null);
  const [backendError, setBackendError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);


  const sendDataToBackend = async (data: any) => {
    try {
      const response = await fetch('http://localhost:3000/process-move', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
      const result = await response.json();
      console.log('Backend response:', result);
      setBackendResponse(result);
    } catch (error) {
      setBackendError(error as string);
    }
  }
  const makeMove = useCallback((move: any) => {
    try {
      const result = game.move(move);
      setGame(new Chess(game.fen()));
      if (onMove) {
        onMove(game.fen());
        sendDataToBackend(game.fen());
      }
      return result;
    } catch (e) {
      return null;
    }
  }, [game, onMove]);

  function onDrop(sourceSquare: string, targetSquare: string) {
    const move = makeMove({
      from: sourceSquare,
      to: targetSquare,
      promotion: 'q' // always promote to queen for simplicity
    });

    return move !== null;
  }

  return (
    <div style={{ maxWidth: '600px', margin: 'auto' }}>
      <Chessboard 
        position={game.fen()}
        onPieceDrop={onDrop}
        boardWidth={600}
      />
      <div style={{ marginTop: '20px', textAlign: 'center' }}>
        <button onClick={() => {
          setGame(new Chess());
        }}>Reset Game</button>
        <p>Current FEN: {game.fen()}</p>
      </div>
    </div>
  );
}