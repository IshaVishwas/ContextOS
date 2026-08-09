def calculate_savings(original: int, compressed: int) -> int:
    """Calculates the absolute token savings."""
    savings = original - compressed
    return max(0, savings)

def calculate_ratio(original: int, compressed: int) -> float:
    """Calculates the compression ratio (0.0 to 1.0)"""
    if original == 0:
        return 0.0
    # Lower is better (e.g. 0.2 means compressed is 20% of original)
    return compressed / original
