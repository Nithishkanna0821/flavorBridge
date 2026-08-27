import numpy as np
import pandas as pd
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from backend.models import Product, Interaction, Order, OrderItem, Review, User

INTERACTION_WEIGHTS = {
    'VIEW': 1.0,
    'LIKE': 2.0,
    'CART': 3.0,
    'PURCHASE': 5.0
}

def calculate_product_similarity_matrix(products: list[Product]):
    """
    Computes a pairwise content similarity matrix across all products
    using TF-IDF vectors of category, region, type, ingredients, and description.
    """
    if not products:
        return np.array([]), {}
        
    corpus = []
    prod_id_to_idx = {}
    idx_to_prod_id = {}
    
    for idx, p in enumerate(products):
        prod_id_to_idx[p.id] = idx
        idx_to_prod_id[idx] = p.id
        text = f"{p.name} {p.category} {p.product_type} {p.region} {p.city} {p.ingredients} {p.description}"
        corpus.append(text.lower())
        
    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
    tfidf_matrix = vectorizer.fit_transform(corpus)
    similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
    
    return similarity_matrix, prod_id_to_idx, idx_to_prod_id

def get_similar_products(product_id: int, top_k: int = 4) -> list[Product]:
    """
    Find products similar to a given product (Content-based filtering).
    E.g. Chicken Masala -> Biryani Masala, Pepper Powder, Curry Masala.
    """
    all_products = Product.query.all()
    if not all_products:
        return []
        
    sim_matrix, prod_id_to_idx, idx_to_prod_id = calculate_product_similarity_matrix(all_products)
    
    if product_id not in prod_id_to_idx:
        # Fallback to category match
        target = Product.query.get(product_id)
        if not target:
            return all_products[:top_k]
        return [p for p in all_products if p.id != product_id and p.category == target.category][:top_k]
        
    target_idx = prod_id_to_idx[product_id]
    scores = list(enumerate(sim_matrix[target_idx]))
    
    # Sort descending by score, excluding self
    scores.sort(key=lambda x: x[1], reverse=True)
    
    similar_prods = []
    for idx, score in scores:
        p_id = idx_to_prod_id[idx]
        if p_id != product_id:
            prod = Product.query.get(p_id)
            if prod:
                similar_prods.append(prod)
        if len(similar_prods) >= top_k:
            break
            
    return similar_prods

def get_personalized_recommendations(user_id: int = None, user_city: str = None, top_k: int = 8) -> dict:
    """
    Generates a personalized recommendation payload with multiple curated shelves:
    1. 'for_you': Personalized hybrid recommendations based on user interaction/purchase history.
    2. 'trending': Top-rated & most interacted across the platform.
    3. 'regional_delicacies': Curated authentic items matching user's city/region.
    4. 'fresh_specials': Fresh regional specialties.
    """
    all_products = Product.query.all()
    if not all_products:
        return {'for_you': [], 'trending': [], 'regional_delicacies': [], 'fresh_specials': []}
        
    user = User.query.get(user_id) if user_id else None
    effective_city = user.city if (user and user.city) else (user_city or 'Chennai')
    
    # 1. Cold-start / Trending shelf (Highest average ratings and stock)
    trending = sorted(all_products, key=lambda p: (p.average_rating, p.rating_count), reverse=True)[:top_k]
    
    # 2. Regional Delicacies (Matching user's city or nearby regional favorites)
    regional = [p for p in all_products if effective_city.lower() in (p.city or '').lower() or effective_city.lower() in (p.region or '').lower()]
    if len(regional) < 4:
        # Pad with popular items
        regional += [p for p in trending if p not in regional]
    regional = regional[:top_k]
    
    # 3. Fresh Food specials
    fresh = [p for p in all_products if p.product_type == 'Fresh Food']
    if not fresh:
        fresh = all_products[:top_k]
    fresh = fresh[:top_k]
    
    # 4. Personalized 'For You' shelf
    for_you = []
    if user_id:
        # Collect interaction history
        interactions = Interaction.query.filter_by(customer_id=user_id).all()
        orders = Order.query.filter_by(customer_id=user_id).all()
        
        product_interest_scores = defaultdict(float)
        interacted_product_ids = set()
        
        for inter in interactions:
            w = INTERACTION_WEIGHTS.get(inter.interaction_type, 1.0)
            product_interest_scores[inter.product_id] += w
            interacted_product_ids.add(inter.product_id)
            
        for o in orders:
            for item in o.items:
                product_interest_scores[item.product_id] += INTERACTION_WEIGHTS['PURCHASE']
                interacted_product_ids.add(item.product_id)
                
        if product_interest_scores:
            # Build similarity scoring based on preferred products
            sim_matrix, prod_id_to_idx, idx_to_prod_id = calculate_product_similarity_matrix(all_products)
            
            recommendation_scores = defaultdict(float)
            for p_id, user_weight in product_interest_scores.items():
                if p_id in prod_id_to_idx:
                    p_idx = prod_id_to_idx[p_id]
                    for other_idx, sim_score in enumerate(sim_matrix[p_idx]):
                        other_pid = idx_to_prod_id[other_idx]
                        if other_pid not in interacted_product_ids:
                            recommendation_scores[other_pid] += sim_score * user_weight
                            
            # Rank products by accumulated score
            sorted_rec_ids = sorted(recommendation_scores.items(), key=lambda x: x[1], reverse=True)
            for p_id, _ in sorted_rec_ids:
                prod = Product.query.get(p_id)
                if prod and prod not in for_you:
                    for_you.append(prod)
                if len(for_you) >= top_k:
                    break

    # If user has no history or cold-start, construct diverse top picks
    if not for_you:
        # Mix of top categories + high rated
        category_sample = defaultdict(list)
        for p in all_products:
            category_sample[p.category].append(p)
            
        for cat, prods in category_sample.items():
            if prods:
                for_you.append(prods[0])
            if len(for_you) >= top_k:
                break
                
        if len(for_you) < top_k:
            for_you += [p for p in trending if p not in for_you]
        for_you = for_you[:top_k]

    return {
        'for_you': for_you,
        'trending': trending,
        'regional_delicacies': regional,
        'fresh_specials': fresh
    }
