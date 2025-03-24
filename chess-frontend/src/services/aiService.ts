import axios from 'axios';

const API_URL = 'http://localhost:8000'; // adjust this to match your Rust backend URL

export const getAIMove = async (fen: string): Promise<string> => {
  try {
    const response = await axios.post(`${API_URL}/get-move`, { fen });
    return response.data.move;
  } catch (error) {
    console.error('Error getting AI move:', error);
    throw error;
  }
}; 