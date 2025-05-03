# app/game/constants.py
LEVEL_SETTINGS = {
    'easy': {
        'range': (1, 10),
        'attempts': 5,
        'multiplier': 1,
        'points_per_attempt': 10
    },
    'medium': {
        'range': (1, 50),
        'attempts': 7, 
        'multiplier': 2,
        'points_per_attempt': 15
    },
    'hard': {
        'range': (1, 100),
        'attempts': 10,
        'multiplier': 3,
        'points_per_attempt': 20
    }
}