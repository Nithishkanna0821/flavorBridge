import re
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from backend.models import Product

def build_product_corpus(products: list[Product]) -> list[str]:
    """
    Constructs a rich text document for each product incorporating name,
    category, description, ingredients, city, region, and food type.
    """
    corpus = []
    for p in products:
        text_elements = [
            p.name or '',
            p.name or '',  # boost name
            p.category or '',
            p.product_type or '',
            p.city or '',
            p.region or '',
            p.description or '',
            p.ingredients or '',
        ]
        # Clean and combine
        combined = " ".join(text_elements).lower()
        combined = re.sub(r'[^a-zA-Z0-9\s]', ' ', combined)
        corpus.append(combined)
    return corpus

def search_products(query: str, products: list[Product] = None, top_k: int = 20) -> list[tuple[Product, float]]:
    """
    Performs TF-IDF Vectorization and Cosine Similarity to find products
    matching a free-form natural language query.
    Returns list of (Product, similarity_score).
    """
    if not query or not query.strip():
        if products is None:
            products = Product.query.all()
        return [(p, 1.0) for p in products[:top_k]]
        
    if products is None:
        products = Product.query.all()
        
    if not products:
        return []

    corpus = build_product_corpus(products)
    
    clean_query = query.lower()
    clean_query = re.sub(r'[^a-zA-Z0-9\s]', ' ', clean_query).strip()
    
    if not clean_query:
        return [(p, 1.0) for p in products[:top_k]]

    try:
        vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            sublinear_tf=True,
            token_pattern=r'(?u)\b\w+\b'
        )
        
        tfidf_matrix = vectorizer.fit_transform(corpus)
        query_vector = vectorizer.transform([clean_query])
        
        similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()
        
        # Pair with products
        scored_products = []
        for idx, score in enumerate(similarities):
            # Check for direct keyword substring hits to boost exact matches
            boost = 0.0
            p = products[idx]
            q_tokens = clean_query.split()
            p_text = f"{p.name} {p.category} {p.city} {p.region} {p.ingredients}".lower()
            
            for token in q_tokens:
                if len(token) > 2 and token in p_text:
                    boost += 0.15
                    
            final_score = float(score + boost)
            if final_score > 0.02:
                scored_products.append((p, final_score))
                
        # Sort by similarity score descending
        scored_products.sort(key=lambda x: x[1], reverse=True)
        return scored_products[:top_k]
        
    except Exception as e:
        # Fallback to simple substring match
        matched = []
        for p in products:
            p_text = f"{p.name} {p.category} {p.description} {p.ingredients} {p.city} {p.region}".lower()
            if any(term in p_text for term in clean_query.split()):
                matched.append((p, 0.5))
        return matched[:top_k]
