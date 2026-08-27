from flask import Blueprint, render_template, request, session, jsonify
from backend.models import User, Product, FoodMaker
from backend.ai.recommender import get_personalized_recommendations
from backend.ai.smart_search import search_products
from backend.ai.recipe_partner_matcher import match_recipe_partners
from backend.ai.food_assistant import process_food_assistant_query

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/recommendations')
def recommendations():
    user_id = session.get('user_id')
    user = User.query.get(user_id) if user_id else None
    user_city = user.city if user else 'Chennai'

    recs = get_personalized_recommendations(user_id=user_id, user_city=user_city)

    return render_template(
        'recommendations.html',
        user=user,
        for_you=recs['for_you'],
        trending=recs['trending'],
        regional_delicacies=recs['regional_delicacies'],
        fresh_specials=recs['fresh_specials']
    )


@ai_bp.route('/smart-search')
def smart_search_view():
    query = request.args.get('q', '').strip()
    all_products = Product.query.all()
    results = []

    if query:
        scored_results = search_products(query, all_products, top_k=24)
        results = scored_results
    else:
        results = [(p, 1.0) for p in all_products[:12]]

    return render_template(
        'smart_search.html',
        query=query,
        results=results,
        total_results=len(results)
    )


@ai_bp.route('/recipe-partners', methods=['GET', 'POST'])
def recipe_partners():
    dish_query = request.args.get('dish') or (request.form.get('dish') if request.method == 'POST' else '')
    city_query = request.args.get('city') or (request.form.get('city') if request.method == 'POST' else '')

    user_id = session.get('user_id')
    user = User.query.get(user_id) if user_id else None

    if not city_query and user and user.city:
        city_query = user.city

    matched_partners = []
    if dish_query or city_query:
        matched_partners = match_recipe_partners(requested_dish=dish_query, customer_city=city_query)
    else:
        # Default showcase
        matched_partners = match_recipe_partners(requested_dish="Traditional Biryani & Kari Dosa", customer_city="Chennai")

    all_cities = sorted(list(set(m.user.city for m in FoodMaker.query.all() if m.user and m.user.city)))

    return render_template(
        'recipe_partners.html',
        dish_query=dish_query,
        city_query=city_query,
        matched_partners=matched_partners,
        cities=all_cities
    )


@ai_bp.route('/food-assistant')
def food_assistant():
    user_id = session.get('user_id')
    user = User.query.get(user_id) if user_id else None
    initial_query = request.args.get('q', '').strip()
    
    initial_response = None
    if initial_query:
        initial_response = process_food_assistant_query(initial_query, customer_city=user.city if user else None)

    return render_template(
        'food_assistant.html',
        user=user,
        initial_query=initial_query,
        initial_response=initial_response
    )


@ai_bp.route('/api/food-assistant', methods=['POST'])
def api_food_assistant():
    data = request.get_json() or {}
    query = data.get('query', '').strip()
    user_id = session.get('user_id')
    user = User.query.get(user_id) if user_id else None
    customer_city = user.city if user else None

    result = process_food_assistant_query(query, customer_city=customer_city)
    return jsonify(result)
