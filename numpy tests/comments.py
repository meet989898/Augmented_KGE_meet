# ---------------------------------------------------------------
# 1. Overlap Coefficient:
# The overlap coefficient measures how much one set is a subset of another.
# It is useful when we expect one set to be contained within the other.
#
# Formula:
#     Overlap(A, B) = |A ∩ B| / min(|A|, |B|)
#
# Properties:
# - Ranges from 0 (no overlap) to 1 (one set is a complete subset of the other).
# - Works best when comparing hierarchical relationships or strict subsets.
#
# Use Case:
# - Taxonomy comparisons (e.g., knowledge graph embeddings).
# - NLP tasks where strict term overlap is needed.
#
# Reference:
# - https://en.wikipedia.org/wiki/Overlap_coefficient
# ---------------------------------------------------------------

# ---------------------------------------------------------------
# 2. Jaccard Similarity (Jaccard Index):
# Measures the proportion of common elements relative to the total unique elements.
# Unlike the overlap coefficient, it accounts for both intersection and union.
#
# Formula:
#     Jaccard(A, B) = |A ∩ B| / |A ∪ B|
#
# Properties:
# - Ranges from 0 (completely disjoint sets) to 1 (identical sets).
# - More sensitive to the total number of elements in both sets.
#
# Use Case:
# - Used in **machine learning** for clustering and classification.
# - Document similarity in **information retrieval**.
#
# Reference:
# - https://en.wikipedia.org/wiki/Jaccard_index
# ---------------------------------------------------------------

# ---------------------------------------------------------------
# 3. Sørensen-Dice Coefficient (Dice Similarity):
# Similar to Jaccard but weighs the intersection more heavily.
# This makes it more sensitive to smaller sets compared to Jaccard.
#
# Formula:
#     Dice(A, B) = (2 * |A ∩ B|) / (|A| + |B|)
#
# Properties:
# - Ranges from 0 (no overlap) to 1 (identical sets).
# - Gives more importance to matching elements than Jaccard.
#
# Use Case:
# - Used in **bioinformatics** for genetic similarity detection.
# - Image processing and **computer vision** for pattern matching.
#
# Reference:
# - https://en.wikipedia.org/wiki/S%C3%B8rensen%E2%80%93Dice_coefficient
# ---------------------------------------------------------------

# ---------------------------------------------------------------
# 4. Cosine Similarity:
# Measures similarity based on the angle between two vectorized sets.
# It treats the sets as high-dimensional vectors rather than using set size directly.
#
# Formula:
#     Cosine(A, B) = |A ∩ B| / (sqrt(|A|) * sqrt(|B|))
#
# Properties:
# - Ranges from 0 (completely different) to 1 (identical).
# - Not sensitive to absolute set sizes, only relative overlap.
#
# Use Case:
# - Commonly used in **text mining and NLP** (e.g., TF-IDF vector comparisons).
# - High-dimensional **vector similarity** in recommendation systems.
#
# Reference:
# - https://en.wikipedia.org/wiki/Cosine_similarity
# ---------------------------------------------------------------

# ---------------------------------------------------------------
# 5. Tversky Index (Asymmetric Similarity Measure):
# A generalization of Jaccard and Dice that allows asymmetric weighting.
# It controls how much of A-B and B-A differences affect the similarity score.
#
# Formula:
#     Tversky(A, B) = |A ∩ B| / (|A ∩ B| + α |A - B| + β |B - A|)
#
# Properties:
# - α and β control the asymmetry:
#   - If α = β = 0.5 → behaves like Dice Similarity.
#   - If α = β = 1 → behaves like Jaccard Index.
# - Allows biasing towards one set over the other.
#
# Use Case:
# - **Medical studies** where symptoms of diseases may be asymmetrical.
# - **Cognitive science** where perception of similarity is not symmetric.
#
# Reference:
# - https://en.wikipedia.org/wiki/Tversky_index
# ---------------------------------------------------------------
