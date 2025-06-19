#pragma once
#include <cstdint>

class Piece {
private:
    uint8_t data;  // 4 bits: type (0-6), 1 bit: color, 3 bits: unused, use 8 bits for memory efficiency
    
public:
    static constexpr uint8_t TYPE_MASK = 0x07;   // 0b00000111
    static constexpr uint8_t COLOR_MASK = 0x08;  // 0b00001000
    
    enum Type : uint8_t {
        NONE = 0, PAWN = 1, KNIGHT = 2, BISHOP = 3,
        ROOK = 4, QUEEN = 5, KING = 6
    };
    
    enum Color : uint8_t {
        WHITE = 0, BLACK = 8 // Use 8 for the color bit
    };

    constexpr Piece() : data(0) {}
    // The constructor now uses the inner enums
    constexpr Piece(Color color, Type type) : data(static_cast<uint8_t>(color) | static_cast<uint8_t>(type)) {}
    
    constexpr Type type() const { return Type(data & TYPE_MASK); }
    constexpr Color color() const { return Color(data & COLOR_MASK); }
    constexpr bool is_empty() const { return data == 0; }
    constexpr uint8_t raw() const { return data; }
    
    constexpr bool operator==(Piece other) const { return data == other.data; }
    constexpr bool operator!=(Piece other) const { return data != other.data; }
};
