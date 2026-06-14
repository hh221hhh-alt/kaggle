# Kaggle Submission

This repository contains `submission.py`, a bot for a planet-conquest strategy game.

## Overview

The bot controls fleets of ships to capture planets on a circular board. It uses:

- **Forward simulation** to project game state several turns ahead
- **Melis evaluator** to score candidate moves
- **Personality modes** (`patient`, `opportunistic`, `pressure`) that adapt to the opponent's behavior

## How it works

Each turn, the bot:

1. Parses the game observation into a `World` snapshot
2. Runs defense checks to protect owned planets
3. Searches for the best capture action using `search_step_action`
4. Optionally executes coordinated multi-planet attacks (Hammer / Mega Hammer)
5. Emits fleet launch commands

## Running

This file is submitted directly to the Kaggle competition environment. It does not require any external dependencies beyond the Python standard library.
