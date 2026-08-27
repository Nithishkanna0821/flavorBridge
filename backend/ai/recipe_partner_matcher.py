import re
from backend.models import FoodMaker, Product

def match_recipe_partners(requested_dish: str, customer_city: str = None, limit: int = 10) -> list[dict]:
    """
    Ranks verified and experienced food makers based on:
    - Speciality & Cuisine keyword match (35%)
    - Location proximity / city match (30%)
    - Verification score & status (20%)
    - Customer ratings & review count (15%)
    """
    dish_clean = (requested_dish or '').lower().strip()
    city_clean = (customer_city or '').lower().strip()
    
    food_makers = FoodMaker.query.all()
    if not food_makers:
        return []
        
    dish_tokens = set(re.findall(r'\w+', dish_clean))
    
    ranked_results = []
    
    for maker in food_makers:
        maker_user = maker.user
        maker_city = (maker_user.city or '').lower() if maker_user else ''
        speciality = (maker.speciality or '').lower()
        cuisines = (maker.cuisines or '').lower()
        description = (maker.description or '').lower()
        
        match_score = 0.0
        reasons = []
        
        # 1. Location match (up to 30 points)
        if city_clean and maker_city:
            if city_clean in maker_city or maker_city in city_clean:
                match_score += 30.0
                reasons.append(f"Located in your city ({maker_user.city})")
            else:
                match_score += 10.0  # Regional proximity within India
        else:
            match_score += 15.0
            
        # 2. Speciality & Cuisine Match (up to 35 points)
        speciality_text = f"{speciality} {cuisines} {description}"
        matched_tokens = [t for t in dish_tokens if len(t) > 2 and t in speciality_text]
        
        # Also check product names of the maker
        maker_product_names = [p.name.lower() for p in maker.products]
        maker_product_categories = [p.category.lower() for p in maker.products]
        all_maker_prod_text = " ".join(maker_product_names + maker_product_categories)
        
        prod_matched_tokens = [t for t in dish_tokens if len(t) > 2 and t in all_maker_prod_text]
        
        if matched_tokens or prod_matched_tokens:
            token_count = len(set(matched_tokens + prod_matched_tokens))
            score_gain = min(35.0, 15.0 + (token_count * 10.0))
            match_score += score_gain
            reasons.append(f"Specializes in {maker.speciality or maker.cuisines}")
        elif not dish_tokens:
            match_score += 20.0
            reasons.append("Experienced regional maker")
        else:
            # Baseline domain match
            match_score += 5.0
            
        # 3. Verification status & score (up to 20 points)
        if maker.is_verified:
            match_score += 20.0
            reasons.append(f"✓ Platform Verified Maker (Score: {maker.verification_score}%)")
        else:
            scaled_v = (maker.verification_score / 100.0) * 15.0
            match_score += scaled_v
            
        # 4. Rating & Reviews (up to 15 points)
        avg_rating = maker.average_rating
        rating_score = (avg_rating / 5.0) * 15.0
        match_score += rating_score
        if avg_rating >= 4.5:
            reasons.append(f"Top-rated culinary maker ({avg_rating}★)")
            
        # Clip score between 10 and 99
        final_score = int(min(99, max(15, round(match_score))))
        
        # Check if maker already has exact or related products
        related_products = []
        for p in maker.products:
            p_text = f"{p.name} {p.category} {p.description}".lower()
            if any(t in p_text for t in dish_tokens) or not dish_tokens:
                related_products.append(p)
                
        ranked_results.append({
            'maker': maker,
            'user': maker_user,
            'match_score': final_score,
            'reasons': reasons,
            'matching_products': related_products[:3],
            'experience_years': maker.years_experience,
            'cuisines': maker.cuisines,
            'speciality': maker.speciality
        })
        
    # Sort by match score descending
    ranked_results.sort(key=lambda x: x['match_score'], reverse=True)
    return ranked_results[:limit]
