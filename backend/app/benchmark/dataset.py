import random

# Ground truth facts that must be present in the benchmark queries
FACTS = [
    "The user's primary programming language is Python.",
    "The critical threshold for scaling is 95%.",
    "The database uses PostgreSQL version 15.",
    "The maximum latency allowed is 200ms.",
    "User prefers dark mode for all UI elements."
]

IRRELEVANT_FILLERS = [
    "The weather is really nice today, isn't it?",
    "I had pizza for lunch and it was amazing.",
    "Did you see the latest movie that came out?",
    "My dog is barking at the mailman again.",
    "I need to buy some groceries later.",
    "Can't believe it's already Friday.",
    "I'm planning a vacation to Japan next year.",
    "Coffee is the only thing keeping me awake.",
    "Just finished reading a really good sci-fi book.",
    "My keyboard is starting to break, need a new one."
]

def generate_conversation(size: int):
    """
    Generate a deterministic synthetic conversation of exactly `size` messages.
    Ensures that all FACTS are embedded at some point, surrounded by irrelevant info.
    """
    random.seed(42 + size) # Deterministic based on size
    
    messages = []
    
    # We will distribute the facts across the conversation
    # ensuring they fit within the size limit.
    fact_indices = random.sample(range(size), min(size, len(FACTS)))
    fact_dict = {idx: FACTS[i] for i, idx in enumerate(fact_indices)}
    
    for i in range(size):
        if i in fact_dict:
            content = f"Important note: {fact_dict[i]} Please remember this."
        else:
            # Pick a random filler, sometimes repeating
            filler = random.choice(IRRELEVANT_FILLERS)
            content = f"Just thinking... {filler}"
            
        messages.append({
            "role": "user" if i % 2 == 0 else "assistant",
            "content": content
        })
        
    query = "Please summarize the critical system requirements including language, scaling threshold, database version, maximum latency, and UI preferences."
    
    return {
        "size": size,
        "messages": messages,
        "query": query,
        "expected_facts": FACTS[:min(size, len(FACTS))]
    }

def get_benchmark_datasets():
    return [
        generate_conversation(10),
        generate_conversation(25),
        generate_conversation(50),
        generate_conversation(100),
        generate_conversation(250)
    ]
