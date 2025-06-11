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
  const [moveFrom, setMoveFrom] = useState<string>('');
  const [moveTo, setMoveTo] = useState<string>('');
  const [showPromotionDialog, setShowPromotionDialog] = useState<boolean>(false);

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

      // Handle game over states from backend
      if (result.game_over || result.game_state?.is_game_over) {
        console.log("Game Over:", result.game_state?.result || result.message);
        return; // Don't make a move if game is over
      }

      // If the backend sent a move, apply it
      if (result.next_move) {
        makeMove({
          from: result.next_move.from,
          to: result.next_move.to,
          promotion: result.next_move.promotion || "q",
          isAiMove: true // Mark as AI move to prevent sending back to backend
        });
        
        // Log game state after AI move
        if (result.game_state) {
          const { is_check, is_checkmate, is_stalemate, result: gameResult } = result.game_state;
          if (is_checkmate) {
            console.log("🎯 CHECKMATE:", gameResult);
          } else if (is_stalemate) {
            console.log("🤝 STALEMATE:", gameResult);
          } else if (is_check) {
            console.log("⚠️ CHECK: Player is in check");
          }
        }
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

  // Handle promotion piece selection
  function onPromotionPieceSelect(piece?: string) {
    // Make the promotion move
    if (moveFrom && moveTo && piece) {
      const move = makeMove({
        from: moveFrom,
        to: moveTo,
        promotion: piece[1].toLowerCase(), // Extract piece type (q, r, b, n)
        isAiMove: false,
      });
      
      setMoveFrom('');
      setMoveTo('');
      setShowPromotionDialog(false);
      
      return move !== null;
    }
    return false;
  }

  function onDrop(sourceSquare: string, targetSquare: string) {
    // Check if it's the player's turn
    const isPlayerTurn = (playerColor === 'white' && game.turn() === 'w') || 
                        (playerColor === 'black' && game.turn() === 'b');
    
    if (!isPlayerTurn) {
      return false; // Not player's turn
    }

    // Check for king-onto-rook castling
    const piece = game.get(sourceSquare as any);
    const targetPiece = game.get(targetSquare as any);
    
    // If dragging king onto rook, convert to castling move
    if (piece && piece.type === 'k' && targetPiece && targetPiece.type === 'r' && piece.color === targetPiece.color) {
      console.log("🏰 King-onto-rook castling detected!");
      
      // Determine castling type and target square
      let castlingTargetSquare: string | undefined;
      if (piece.color === 'w') {
        // White castling
        if (targetSquare === 'h1') {
          castlingTargetSquare = 'g1'; // Kingside
          console.log("🏰 White kingside castling: e1 -> g1");
        } else if (targetSquare === 'a1') {
          castlingTargetSquare = 'c1'; // Queenside  
          console.log("🏰 White queenside castling: e1 -> c1");
        }
      } else {
        // Black castling
        if (targetSquare === 'h8') {
          castlingTargetSquare = 'g8'; // Kingside
          console.log("🏰 Black kingside castling: e8 -> g8");
        } else if (targetSquare === 'a8') {
          castlingTargetSquare = 'c8'; // Queenside
          console.log("🏰 Black queenside castling: e8 -> c8");
        }
      }
      
      if (castlingTargetSquare) {
        // Try the castling move with proper target square
        const possibleMoves = game.moves({ verbose: true });
        const castlingMove = castlingTargetSquare ? possibleMoves.find(move => 
          move.from === sourceSquare && move.to === castlingTargetSquare && 
          (move.flags.includes('k') || move.flags.includes('q'))
        ) : null;
        
        if (castlingMove) {
          console.log("✅ Valid castling move found");
          const move = makeMove({
            from: sourceSquare,
            to: castlingTargetSquare,
            promotion: null,
            isAiMove: false,
          });
          return move !== null;
        } else {
          console.log("❌ Castling not allowed");
          return false;
        }
      }
    }

    // Regular move handling (non-castling)
    // Try to find the exact move including special moves
    const possibleMoves = game.moves({ verbose: true });
    const attemptedMove = possibleMoves.find(move => 
      move.from === sourceSquare && move.to === targetSquare
    );

    if (!attemptedMove) {
      console.log(`Invalid move attempted: ${sourceSquare} -> ${targetSquare}`);
      return false; // Invalid move
    }

    // Log the move type for debugging
    if (attemptedMove.flags.includes('k')) {
      console.log("🏰 Kingside castling detected");
    } else if (attemptedMove.flags.includes('q')) {
      console.log("🏰 Queenside castling detected");
    } else if (attemptedMove.flags.includes('e')) {
      console.log("👻 En passant capture detected");
    } else if (attemptedMove.flags.includes('p')) {
      console.log("👑 Pawn promotion detected");
      // Store the move for promotion dialog
      setMoveFrom(sourceSquare);
      setMoveTo(targetSquare);
      setShowPromotionDialog(true);
      return true; // Return true to allow the move to proceed to promotion selection
    }

    const move = makeMove({
      from: sourceSquare,
      to: targetSquare,
      promotion: attemptedMove.promotion || "q", // Use actual promotion or default to queen
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
    <>
      {/* Background Layer - Completely Separate */}
      <div style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        width: '100vw',
        height: '100vh',
        backgroundImage: 'url(/che.png)',
        backgroundSize: 'cover',
        backgroundPosition: '70% 30%',
        backgroundRepeat: 'no-repeat',
        zIndex: -1
      }} />
      
      {/* Content Layer */}
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '20px'
      }}>
        {/* Chessboard Container - Keep Simple! */}
        <div style={{
          width: '600px',
          height: '600px',
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          padding: '10px',
          borderRadius: '15px',
          boxShadow: '0 8px 20px rgba(0, 0, 0, 0.3)',
          border: '1px solid rgba(255, 255, 255, 0.3)'
        }}>
          <Chessboard 
            position={game.fen()} 
            onPieceDrop={onDrop} 
            boardWidth={580}
            boardOrientation={playerColor}
            onPromotionPieceSelect={onPromotionPieceSelect}
          />
        </div>
        
        {/* Controls */}
        <div style={{ 
          marginTop: "20px", 
          textAlign: "center",
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          padding: '20px',
          borderRadius: '15px',
          boxShadow: '0 8px 20px rgba(0, 0, 0, 0.3)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.3)'
        }}>
          <button onClick={() => {
            setGame(new Chess());
            setBackendResponse(null);
            setBackendError(null);
            setGameStarted(false);
          }} style={{ marginRight: '10px' }}>
            Reset Game
          </button>
          
          <button onClick={onBackToSetup} style={{ 
            backgroundColor: '#6c757d',
            color: 'white',
            border: 'none',
            padding: '8px 16px',
            borderRadius: '4px',
            cursor: 'pointer'
          }}>
            Back to Setup
          </button>
          
          <p style={{ marginTop: '15px', fontSize: '14px', color: '#666' }}>
            Current FEN: {game.fen()}
          </p>

          {/* Reserve consistent space for loading/response messages */}
          <div style={{ minHeight: '60px', marginTop: '10px' }}>
            {isLoading && <p style={{ color: '#007bff', fontWeight: 'bold', margin: '10px 0' }}>
              Waiting for AI move...
            </p>}
            
            {backendError && <p style={{ color: "red", margin: '10px 0' }}>
              Error: {backendError}
            </p>}
            
            {backendResponse && !isLoading && !backendError && (
              <div style={{ 
                padding: "10px", 
                backgroundColor: "#d4edda", 
                borderRadius: "8px",
                border: "1px solid #c3e6cb",
                margin: '10px 0'
              }}>
                <p style={{ margin: 0, color: "#155724" }}>
                  AI response: {backendResponse.message}
                </p>
              </div>
            )}
          </div>
          
          {/* Game over messages - separate fixed space */}
          <div style={{ minHeight: '80px', marginTop: '5px' }}>
            {game.isCheckmate() && (
              <div style={{ 
                padding: "15px", 
                backgroundColor: "#f8d7da", 
                borderRadius: "8px", 
                border: "1px solid #f5c6cb",
                margin: '10px 0'
              }}>
                <h3 style={{ margin: "0", color: "#721c24" }}>
                  Checkmate! {game.turn() === 'w' ? 'Black' : 'White'} wins! 🎉
                </h3>
              </div>
            )}
            
            {game.isStalemate() && (
              <div style={{ 
                padding: "15px", 
                backgroundColor: "#fff3cd", 
                borderRadius: "8px", 
                border: "1px solid #ffeaa7",
                margin: '10px 0'
              }}>
                <h3 style={{ margin: "0", color: "#856404" }}>
                  Stalemate! Game is a draw. 🤝
                </h3>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
