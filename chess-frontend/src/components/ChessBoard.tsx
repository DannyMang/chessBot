import { useState, useCallback, useEffect } from "react";
import { Chess } from "chess.js";
import { Chessboard } from "react-chessboard";

export {};

interface ChessBoardProps {
  onMove?: (move: string) => void;
  playerColor: 'white' | 'black';
  onBackToSetup: () => void;
}

interface MoveData {
  //fen is the current board state
  fen: string;
  //move_from is the starting position of the move
  move_from: string;
  //move_to is the ending position of the move
  move_to: string;
  //promotion is the piece that is being promoted to
  promotion: string | null;
  //valid_moves is an array of valid moves
  valid_moves: string[];
  //is_check is true if the game is in check
  is_check: boolean;
  //is_checkmate is true if the game is in checkmate
  is_checkmate: boolean;
  //is_stalemate is true if the game is in stalemate
  is_stalemate: boolean;
}

export default function ChessBoard({ onMove, playerColor, onBackToSetup }: ChessBoardProps) {
  const [game, setGame] = useState(new Chess());
  const [backendResponse, setBackendResponse] = useState<any>(null);
  const [backendError, setBackendError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [gameStarted, setGameStarted] = useState<boolean>(false);

  // Initialize game based on player color
  useEffect(() => {
    if (!gameStarted) {
      setGameStarted(true);
      // If player is black, make AI move first
      if (playerColor === 'black') {
        // Request AI to make the first move
        const initialMoveData: MoveData = {
          fen: game.fen(),
          move_from: '',
          move_to: '',
          promotion: null,
          valid_moves: game.moves(),
          is_check: game.isCheck(),
          is_checkmate: game.isCheckmate(),
          is_stalemate: game.isStalemate(),
        };
        sendDataToBackend(initialMoveData);
      }
    }
  }, [gameStarted, playerColor, game]);

  const sendDataToBackend = async (moveData: MoveData) => {
    console.log("Sending data to backend:", moveData);
    setIsLoading(true);
    try {
      // Update URL to match your backend endpoint
      const response = await fetch("http://localhost:8080/api/move", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(moveData),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const result = await response.json();
      console.log("Backend response:", result);
      setBackendResponse(result);

      // If the backend sent a move, apply it
      if (result.next_move) {
        makeMove({
          from: result.next_move.from,
          to: result.next_move.to,
          promotion: result.next_move.promotion || "q",
        });
      }
    } catch (error) {
      console.error("Error sending data to backend:", error);
      setBackendError(error instanceof Error ? error.message : String(error));
    } finally {
      setIsLoading(false);
    }
  };

  const makeMove = useCallback(
    (move: any) => {
      try {
        const result = game.move(move);
        if (result === null) {
          return null; // Invalid move
        }
        // In chess.js, when you make a move using game.move(),
        // it mutates the original Chess object directly.
        // In React, state updates should be immutable -
        //  you should create a new object rather than mutating the existing one.
        //  This helps React detect changes and trigger re-renders properly.

        // this line may have room for performance improvements
        const newGame = new Chess(game.fen());

        setGame(newGame);
        if (onMove) {
          onMove(newGame.fen());
        }

        // Only send data to backend for player moves, not AI moves
        if (!move.isAiMove) {
          const valid_moves = newGame.moves();

          const moveData: MoveData = {
            fen: newGame.fen(),
            move_from: move.from,
            move_to: move.to,
            promotion: move.promotion || null,
            valid_moves: valid_moves,
            is_check: newGame.isCheck(),
            is_checkmate: newGame.isCheckmate(),
            is_stalemate: newGame.isStalemate(),
          };

          sendDataToBackend(moveData);
        }

        return result;
      } catch (e) {
        console.error("Error making move:", e);
        return null;
      }
    },
    [game, onMove],
  );

  function onDrop(sourceSquare: string, targetSquare: string) {
    // Check if it's the player's turn
    const isPlayerTurn = (playerColor === 'white' && game.turn() === 'w') || 
                        (playerColor === 'black' && game.turn() === 'b');
    
    if (!isPlayerTurn) {
      return false; // Not player's turn
    }

    const move = makeMove({
      from: sourceSquare,
      to: targetSquare,
      promotion: "q", // always promote to queen for simplicity
      isAiMove: false, // flag to indicate this is a player move
    });

    return move !== null;
  }
  // Handle backend responses
  useEffect(() => {
    if (backendResponse?.next_move) {
      console.log("AI move received:", backendResponse.next_move);
    }
  }, [backendResponse]);

  return (
    <div style={{ maxWidth: "600px", margin: "auto" }}>
      <div className="game-status">
        <h2>Chess Bot Game</h2>
        <p>You are playing as: <strong>{playerColor === 'white' ? 'White' : 'Black'}</strong></p>
        <p>Current turn: <strong>{game.turn() === 'w' ? 'White' : 'Black'}</strong></p>
      </div>
      
      <Chessboard 
        position={game.fen()} 
        onPieceDrop={onDrop} 
        boardWidth={600}
        boardOrientation={playerColor}
      />
      
      <div style={{ marginTop: "20px", textAlign: "center" }}>
        <button
          onClick={() => {
            setGame(new Chess());
            setBackendResponse(null);
            setBackendError(null);
            setGameStarted(false);
          }}
          style={{ marginRight: "10px" }}
        >
          Reset Game
        </button>
        
        <button
          onClick={onBackToSetup}
          style={{ 
            backgroundColor: '#6c757d',
            color: 'white',
            border: 'none',
            padding: '8px 16px',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Back to Setup
        </button>
        
        <p style={{ marginTop: '20px', fontSize: '14px', color: '#666' }}>
          Current FEN: {game.fen()}
        </p>

        {isLoading && <p style={{ color: '#007bff', fontWeight: 'bold' }}>Waiting for AI move...</p>}
        {backendError && <p style={{ color: "red" }}>Error: {backendError}</p>}
        {backendResponse && (
          <div style={{ 
            marginTop: "15px", 
            padding: "10px", 
            backgroundColor: "#d4edda", 
            borderRadius: "5px",
            border: "1px solid #c3e6cb"
          }}>
            <p style={{ margin: 0, color: "#155724" }}>AI response: {backendResponse.message}</p>
          </div>
        )}
        
        {game.isCheckmate() && (
          <div style={{ marginTop: "20px", padding: "15px", backgroundColor: "#f8d7da", borderRadius: "8px", border: "1px solid #f5c6cb" }}>
            <h3 style={{ margin: "0 0 10px 0", color: "#721c24" }}>
              Checkmate! {game.turn() === 'w' ? 'Black' : 'White'} wins! 🎉
            </h3>
          </div>
        )}
        
        {game.isStalemate() && (
          <div style={{ marginTop: "20px", padding: "15px", backgroundColor: "#fff3cd", borderRadius: "8px", border: "1px solid #ffeaa7" }}>
            <h3 style={{ margin: "0 0 10px 0", color: "#856404" }}>
              Stalemate! Game is a draw. 🤝
            </h3>
          </div>
        )}
      </div>
    </div>
  );
}
