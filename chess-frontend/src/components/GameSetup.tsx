import React from 'react';

interface GameSetupProps {
  onGameStart: (playerColor: 'white' | 'black') => void;
}

export default function GameSetup({ onGameStart }: GameSetupProps) {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      height: '100vh',
      width: '100vw',
      backgroundImage: 'url(/test2.png)',
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      backgroundRepeat: 'no-repeat',
      backgroundAttachment: 'fixed',
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      margin: 0,
      padding: 0
    }}>
      {/* Overlay for better text readability */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.4)',
        zIndex: 1
      }} />
      
      <div style={{ position: 'relative', zIndex: 2 }}>
        
        <div style={{
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          padding: '2rem',
          borderRadius: '15px',
          boxShadow: '0 8px 20px rgba(0, 0, 0, 0.3)',
          textAlign: 'center',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.2)'
        }}>
          <h2 style={{
            fontSize: '1.5rem',
            marginBottom: '1.5rem',
            color: '#333'
          }}>
            a small chess bot project
          </h2>
          
          <div style={{
            display: 'flex',
            gap: '2rem',
            justifyContent: 'center'
          }}>
            <button
              onClick={() => onGameStart('white')}
              style={{
                padding: '1rem 2rem',
                fontSize: '1.2rem',
                border: '2px solid #ddd',
                borderRadius: '8px',
                backgroundColor: 'white',
                color: '#333',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                minWidth: '120px',
                boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)'
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.backgroundColor = '#f0f0f0';
                e.currentTarget.style.borderColor = '#333';
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = '0 6px 12px rgba(0, 0, 0, 0.2)';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.backgroundColor = 'white';
                e.currentTarget.style.borderColor = '#ddd';
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.1)';
              }}
            >
             Play as White
            </button>
            
            <button
              onClick={() => onGameStart('black')}
              style={{
                padding: '1rem 2rem',
                fontSize: '1.2rem',
                border: '2px solid #ddd',
                borderRadius: '8px',
                backgroundColor: '#333',
                color: 'white',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                minWidth: '120px',
                boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)'
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.backgroundColor = '#555';
                e.currentTarget.style.borderColor = '#333';
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = '0 6px 12px rgba(0, 0, 0, 0.2)';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.backgroundColor = '#333';
                e.currentTarget.style.borderColor = '#ddd';
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.1)';
              }}
            >
              Play as Black
            </button>
          </div>
          
          <p style={{
            marginTop: '1rem',
            color: '#666',
            fontSize: '0.9rem'
          }}>
            made by{' '}
            <a 
              href="https://x.com/danielung19" 
              target="_blank" 
              rel="noopener noreferrer"
              style={{
                color: '#1da1f2',
                textDecoration: 'none',
                fontWeight: 'bold',
                transition: 'color 0.3s ease'
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.color = '#0d8bd9';
                e.currentTarget.style.textDecoration = 'underline';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.color = '#1da1f2';
                e.currentTarget.style.textDecoration = 'none';
              }}
            >
              @danielung19
            </a>
          </p>
        </div>
      </div>
    </div>
  );
} 