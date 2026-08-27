import re
from backend.models import Product

# Keyword maps for Rule-Based NLP parsing
REGIONS_MAP = {
    'tamil nadu': ['tamil nadu', 'tamilnadu', 'tn', 'chennai', 'madurai', 'chettinad', 'dindigul', 'tirunelveli', 'kumbakonam', 'salem', 'coimbatore'],
    'chennai': ['chennai', 'madras'],
    'madurai': ['madurai', 'kari dosa', 'jigarthanda'],
    'chettinad': ['chettinad', 'karaikudi'],
    'dindigul': ['dindigul', 'thalappakatti'],
    'tirunelveli': ['tirunelveli', 'halwa', 'nellai'],
    'kumbakonam': ['kumbakonam', 'degree coffee'],
    'kerala': ['kerala', 'malabar', 'kochi', 'calicut', 'appam', 'stew', 'banana chips'],
    'hyderabad': ['hyderabad', 'hyderabadi', 'andhra', 'telangana'],
    'bengal': ['kolkata', 'bengal', 'bengali', 'kathi roll'],
    'maharashtra': ['maharashtra', 'mumbai', 'misal', 'pav'],
    'gujarat': ['gujarat', 'gujarati', 'dhokla'],
    'bihar': ['bihar', 'litti', 'chokha'],
    'delhi': ['delhi', 'chaat', 'pani puri', 'golgappa']
}

TASTE_MAP = {
    'spicy': ['spicy', 'hot', 'masala', 'pepper', 'chili', 'chilli', 'karam', 'fiery', 'zesty'],
    'sweet': ['sweet', 'halwa', 'mysore pak', 'mithai', 'dessert', 'palkova', 'laddu', 'sugar', 'jaggery'],
    'tangy': ['tangy', 'pickle', 'sour', 'mango', 'lemon', 'tamarind', 'rasam', 'gooseberry'],
    'crispy': ['crispy', 'crunchy', 'snack', 'murukku', 'chips', 'thattai', 'mixture', 'seedai'],
    'beverage': ['beverage', 'drink', 'coffee', 'tea', 'herbal', 'jaggery drink'],
    'healthy': ['healthy', 'millet', 'diet', 'organic', 'traditional', 'herbal', 'oil-free', 'natural'],
    'fresh': ['fresh', 'hot meal', 'lunch', 'dinner', 'breakfast', 'ready to eat', 'curry', 'biryani', 'dosa']
}

CATEGORY_MAP = {
    'Spice Powders & Seasonings': ['spice', 'masala', 'powder', 'podi', 'sambar', 'rasam', 'pepper'],
    'Traditional Snacks': ['snack', 'murukku', 'chips', 'thattai', 'mixture', 'crispy'],
    'Traditional Sweets': ['sweet', 'halwa', 'mysore pak', 'mithai', 'laddu', 'palkova'],
    'Pickles': ['pickle', 'pickles', 'achar', 'thokku', 'mango', 'garlic pickle', 'fish pickle', 'prawn pickle'],
    'Beverages': ['coffee', 'tea', 'beverage', 'drink', 'chai'],
    'Homemade Food Products': ['homemade', 'rice mix', 'millet', 'chutney powder', 'sauce'],
    'Fresh Regional Foods': ['fresh', 'curry', 'biryani', 'dosa', 'roll', 'misal', 'dhokla', 'litti', 'appam', 'puri']
}

def parse_user_query(query: str) -> dict:
    """
    Extracts structured taste, region, price, and category constraints from natural language.
    """
    q = query.lower()
    
    extracted = {
        'detected_regions': [],
        'detected_tastes': [],
        'detected_categories': [],
        'max_budget': None,
        'product_type': None,
        'raw_query': query
    }
    
    # 1. Budget extraction
    # Matches patterns like: under 300, below 500, less than 200, within 400, rs 300, inr 250, <= 300, 300 rs, 300 rupees
    budget_patterns = [
        r'(?:under|below|less\s+than|within|max|budget\s+of|budget|upto|up\s+to|<=?)\s*(?:rs\.?|inr|₹)?\s*(\d+)',
        r'(?:rs\.?|inr|₹)\s*(\d+)',
        r'(\d+)\s*(?:rs|rupees|bucks|inr)'
    ]
    for pattern in budget_patterns:
        match = re.search(pattern, q)
        if match:
            try:
                extracted['max_budget'] = float(match.group(1))
                break
            except ValueError:
                pass
                
    # 2. Region detection
    for region_name, keywords in REGIONS_MAP.items():
        if any(re.search(rf'\b{re.escape(k)}\b', q) for k in keywords):
            extracted['detected_regions'].append(region_name)
            
    # 3. Taste & Attribute detection
    for taste_name, keywords in TASTE_MAP.items():
        if any(re.search(rf'\b{re.escape(k)}\b', q) for k in keywords):
            extracted['detected_tastes'].append(taste_name)
            
    # 4. Category detection
    for cat_name, keywords in CATEGORY_MAP.items():
        if any(re.search(rf'\b{re.escape(k)}\b', q) for k in keywords):
            extracted['detected_categories'].append(cat_name)
            
    # 5. Food type detection (Packaged vs Fresh)
    if 'fresh' in q or 'cooked' in q or 'hot' in q or 'meal' in q or 'ready to eat' in q or 'curry' in q or 'biryani' in q:
        extracted['product_type'] = 'Fresh Food'
    elif 'packaged' in q or 'packet' in q or 'powder' in q or 'shelf' in q or 'dry' in q:
        extracted['product_type'] = 'Packaged Food'
        
    return extracted

def process_food_assistant_query(query: str, customer_city: str = None) -> dict:
    """
    Analyzes customer request, retrieves relevant food products,
    and constructs a conversational guidance response.
    NOTE: Never automatically orders; returns suggestions for customer selection.
    """
    if not query or not query.strip():
        return {
            'reply': "Hello! I am your Regional Food Assistant. Tell me what flavors you are craving (e.g., 'I want spicy snacks from Madurai under ₹200' or 'Traditional sweets from Tamil Nadu').",
            'products': [],
            'filters': {},
            'safety_note': "FlavorBridge Food Assistant provides regional recommendations. Orders are only placed by you upon confirmation at checkout."
        }
        
    parsed = parse_user_query(query)
    all_products = Product.query.all()
    
    scored_products = []
    
    for p in all_products:
        score = 0.0
        match_details = []
        p_text = f"{p.name} {p.category} {p.description} {p.ingredients} {p.city} {p.region} {p.product_type}".lower()
        
        # Budget check
        if parsed['max_budget'] is not None:
            if p.price <= parsed['max_budget']:
                score += 25.0
                match_details.append(f"Within budget (₹{p.price} <= ₹{parsed['max_budget']})")
            else:
                # Disqualify or penalize heavily if strictly exceeds budget
                continue
                
        # Product type filter
        if parsed['product_type']:
            if p.product_type == parsed['product_type']:
                score += 20.0
                match_details.append(f"{p.product_type} match")
                
        # Region filter
        if parsed['detected_regions']:
            region_hit = False
            for reg in parsed['detected_regions']:
                reg_keywords = REGIONS_MAP.get(reg, [reg])
                if any(rk in p_text for rk in reg_keywords):
                    score += 30.0
                    match_details.append(f"Authentic {reg.title()} origin")
                    region_hit = True
                    break
                    
        # Taste profile filter
        if parsed['detected_tastes']:
            for taste in parsed['detected_tastes']:
                taste_keywords = TASTE_MAP.get(taste, [taste])
                if any(tk in p_text for tk in taste_keywords):
                    score += 20.0
                    match_details.append(f"{taste.title()} flavor profile")
                    
        # Category filter
        if parsed['detected_categories']:
            if p.category in parsed['detected_categories']:
                score += 25.0
                match_details.append(f"Category: {p.category}")
                
        # Maker verification boost
        if p.food_maker and p.food_maker.is_verified:
            score += 10.0
            
        # Rating boost
        score += (p.average_rating * 2.0)
        
        # Exact keyword hit boost from query
        q_tokens = [w for w in re.findall(r'\w+', query.lower()) if len(w) > 3]
        for token in q_tokens:
            if token in p_text:
                score += 5.0
                
        if score > 0:
            scored_products.append({
                'product': p,
                'score': score,
                'reasons': match_details
            })
            
    scored_products.sort(key=lambda x: x['score'], reverse=True)
    top_matches = scored_products[:6]
    
    # Construct conversational response
    reply_parts = []
    
    tastes_str = ", ".join(parsed['detected_tastes']) if parsed['detected_tastes'] else ""
    regions_str = ", ".join(r.title() for r in parsed['detected_regions']) if parsed['detected_regions'] else ""
    
    if parsed['detected_regions'] and parsed['detected_tastes']:
        reply_parts.append(f"I found authentic {tastes_str} specialties from {regions_str}")
    elif parsed['detected_regions']:
        reply_parts.append(f"Here are authentic regional foods from {regions_str}")
    elif parsed['detected_tastes']:
        reply_parts.append(f"Here are top-rated {tastes_str} selections from verified makers")
    else:
        reply_parts.append("Here are some delicious regional delicacies that match your search")
        
    if parsed['max_budget']:
        reply_parts.append(f"priced under ₹{int(parsed['max_budget'])}")
        
    reply_parts.append(f"— handcrafted by local culinary makers:")
    reply_message = " ".join(reply_parts)
    
    if not top_matches:
        reply_message = "I couldn't find an exact item matching all those filters simultaneously. Here are our most popular regional specialties you might enjoy exploring:"
        # Fallback to top products
        top_matches = [{'product': p, 'score': 50.0, 'reasons': ['Popular recommendation']} for p in all_products[:4]]

    # Format products for JSON / template
    formatted_products = []
    for item in top_matches:
        p = item['product']
        formatted_products.append({
            'id': p.id,
            'name': p.name,
            'category': p.category,
            'price': p.price,
            'city': p.city,
            'region': p.region or p.city,
            'product_type': p.product_type,
            'image': p.image,
            'average_rating': p.average_rating,
            'rating_count': p.rating_count,
            'maker_name': p.food_maker.user.name if p.food_maker and p.food_maker.user else 'Verified Maker',
            'maker_verified': p.food_maker.is_verified if p.food_maker else False,
            'match_reason': item['reasons'][0] if item['reasons'] else 'Top culinary recommendation'
        })
        
    return {
        'reply': reply_message,
        'products': formatted_products,
        'filters': {
            'regions': parsed['detected_regions'],
            'tastes': parsed['detected_tastes'],
            'max_budget': parsed['max_budget'],
            'product_type': parsed['product_type']
        },
        'safety_note': "FlavorBridge Food Assistant provides regional recommendations. Orders are only placed by you upon confirmation at checkout."
    }
