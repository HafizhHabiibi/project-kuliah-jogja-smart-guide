# utils/similarity_engine.py
"""
Engine for calculating Cosine Similarity between user preferences and destination DNA.
Implements the vector similarity formula without external libraries like numpy.
"""

import math

def calculate_cosine_similarity(user_vector, dest_vector):
    """
    Calculate Cosine Similarity between two 5-dimensional vectors.
    
    Args:
        user_vector (list or tuple): User's preference values for [Nature, Culture, Culinary, Crowd, Effort].
                                     Values are integers from 1 to 5.
        dest_vector (list or tuple): Destination's DNA scores for [Nature, Culture, Culinary, Crowd, Effort].
                                     Values are floats from 1.0 to 5.0.
                                     
    Returns:
        float: Cosine similarity score between -1.0 and 1.0. (Practically between -1.0 and 1.0 after centering).
    """
    if len(user_vector) != 5 or len(dest_vector) != 5:
        raise ValueError("Both vectors must be exactly 5 dimensions.")

    # Mean-center the vectors around 3.0 (midpoint of Likert scale 1-5)
    u_centered = [float(u) - 3.0 for u in user_vector]
    d_centered = [float(d) - 3.0 for d in dest_vector]

    # Dot product of centered vectors
    dot_product = sum(u * d for u, d in zip(u_centered, d_centered))
    
    # Magnitudes (Euclidean norms) of centered vectors
    magnitude_u = math.sqrt(sum(u ** 2 for u in u_centered))
    magnitude_d = math.sqrt(sum(d ** 2 for d in d_centered))
    
    # Handle zero vectors safely (returns 0.0 which corresponds to "Cukup Cocok" neutral match)
    if magnitude_u == 0.0 or magnitude_d == 0.0:
        return 0.0
        
    similarity = dot_product / (magnitude_u * magnitude_d)
    return round(similarity, 4)


