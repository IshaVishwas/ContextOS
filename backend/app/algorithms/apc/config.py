class APCConfig:
    MAX_TOKENS = 8192
    ALLOCATION = {
        "system": 0.15,
        "conversation": 0.25,
        "memory": 0.50,
        "user_query": 0.10
    }
    CHARS_PER_TOKEN = 4
