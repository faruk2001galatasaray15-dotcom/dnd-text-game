#!/usr/bin/env python3
"""
D&D Text Game - Main Entry Point
Tamamıyla metin tabanlı, D&D 5e mekaniklerine sahip tek oyunculu bilgisayar oyunu
"""

from game.game import Game

def main():
    """Start the game"""
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
