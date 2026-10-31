import os
import sys

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, render_template, session, send_from_directory
from backend.extensions import db
from backend.models import User, Product, FoodMaker, Cart

def create_app():
    import shutil

    # Configure template and static directories pointing to frontend/
    base_dir = os.path.abspath(os.path.dirname(__file__))
    frontend_dir = os.path.abspath(os.path.join(base_dir, '..', 'frontend'))
    database_dir = os.path.abspath(os.path.join(base_dir, '..', 'database'))
    db_file_path = os.path.join(database_dir, 'database.db')

    # Handle Vercel Serverless environment
    if os.environ.get('VERCEL'):
        tmp_db_path = '/tmp/database.db'
        if os.path.exists(db_file_path):
            try:
                if not os.path.exists(tmp_db_path) or os.path.getmtime(db_file_path) > os.path.getmtime(tmp_db_path):
                    shutil.copyfile(db_file_path, tmp_db_path)
            except Exception:
                pass
        db_file_path = tmp_db_path if os.path.exists(tmp_db_path) else db_file_path
        upload_folder = '/tmp/uploads'
        os.makedirs(upload_folder, exist_ok=True)
    else:
        # Ensure database and upload directories exist
        os.makedirs(database_dir, exist_ok=True)
        upload_folder = os.path.join(base_dir, 'uploads')
        os.makedirs(upload_folder, exist_ok=True)

    app = Flask(
        __name__,
        template_folder=os.path.join(frontend_dir, 'templates'),
        static_folder=os.path.join(frontend_dir, 'static'),
        static_url_path='/static'
    )

    # App configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'flavorbridge-super-secret-key-2026-production-ready')
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_SECURE'] = True if os.environ.get('VERCEL') else False
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = 86400 * 30  # 30 days

    # Support reverse proxies like Vercel edge/AWS API Gateway
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    
    # Database configuration (supports Supabase/Neon PostgreSQL or local SQLite)
    database_url = os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL')
    if database_url:
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        try:
            app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        except Exception:
            app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_file_path}"
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_file_path}"

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = upload_folder
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB

    # Optimize SQLite performance with WAL mode and cache sizing
    from sqlalchemy import event
    from sqlalchemy.engine import Engine

    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        uri = str(app.config.get('SQLALCHEMY_DATABASE_URI', ''))
        if uri.startswith('sqlite'):
            try:
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA journal_mode = WAL")
                cursor.execute("PRAGMA synchronous = NORMAL")
                cursor.execute("PRAGMA cache_size = 10000")
                cursor.close()
            except Exception:
                pass

    # Initialize extensions
    db.init_app(app)

    # Register Blueprints
    from backend.routes.auth_routes import auth_bp
    from backend.routes.product_routes import product_bp
    from backend.routes.cart_routes import cart_bp
    from backend.routes.order_routes import order_bp
    from backend.routes.food_maker_routes import food_maker_bp
    from backend.routes.review_routes import review_bp
    from backend.routes.ai_routes import ai_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(food_maker_bp)
    app.register_blueprint(review_bp)
    app.register_blueprint(ai_bp)

    # Custom Jinja Filter for Safe, Instant Image URL Resolution
    @app.template_filter('img_url')
    def img_url_filter(img_val, default='hero_food_banner.jpg'):
        if not img_val:
            return f'/static/images/{default}'
        img_str = str(img_val).strip()
        if img_str.startswith('data:') or img_str.startswith('http://') or img_str.startswith('https://'):
            return img_str
        backend_uploads = os.path.join(base_dir, 'uploads')
        if os.path.exists(os.path.join(backend_uploads, img_str)):
            return f'/uploads/{img_str}'
        static_images = os.path.join(frontend_dir, 'static', 'images')
        if os.path.exists(os.path.join(static_images, img_str)):
            return f'/static/images/{img_str}'
        return f'/uploads/{img_str}'

    # Global Context Processor for Templates
    @app.context_processor
    def inject_globals():
        user_id = session.get('user_id')
        current_user = None
        if user_id:
            current_user = User.query.get(user_id)
            if not current_user:
                # Clear invalid/orphaned session to prevent zombie lockout
                session.clear()
                user_id = None
        
        cart_count = 0
        if current_user:
            cart = Cart.query.filter_by(customer_id=current_user.id).first()
            if cart:
                cart_count = cart.total_items

        categories = [
            "Spice Powders & Seasonings",
            "Traditional Snacks",
            "Traditional Sweets",
            "Pickles",
            "Beverages",
            "Homemade Food Products",
            "Fresh Regional Foods"
        ]

        return dict(
            current_user=current_user,
            cart_count=cart_count,
            categories_list=categories
        )

    # Route for serving uploaded images with automatic graceful fallback
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        backend_uploads = os.path.join(base_dir, 'uploads')
        if os.path.exists(os.path.join(backend_uploads, filename)):
            return send_from_directory(backend_uploads, filename)
        static_images = os.path.join(frontend_dir, 'static', 'images')
        if os.path.exists(os.path.join(static_images, filename)):
            return send_from_directory(static_images, filename)
        upload_folder = app.config.get('UPLOAD_FOLDER', '')
        if upload_folder and os.path.exists(os.path.join(upload_folder, filename)):
            return send_from_directory(upload_folder, filename)
        # Safe fallback: return authentic regional banner instead of 404
        return send_from_directory(static_images, 'hero_food_banner.jpg')

    # Homepage Route
    @app.route('/')
    def index():
        all_products = Product.query.all()
        featured_makers = FoodMaker.query.filter_by(is_verified=True).limit(5).all()
        fresh_foods = Product.query.filter_by(product_type='Fresh Food').limit(6).all()
        popular_foods = sorted(all_products, key=lambda p: (p.average_rating, p.rating_count), reverse=True)[:8]
        
        # Category preview data
        category_highlights = [
            {"name": "Spice Powders & Seasonings", "desc": "Stone-ground masalas & podis", "icon": "fa-pepper-hot", "bg": "spice-bg"},
            {"name": "Traditional Snacks", "desc": "Wood-pressed oil murukku & chips", "icon": "fa-cookie-bite", "bg": "snack-bg"},
            {"name": "Traditional Sweets", "desc": "Pure ghee halwa & mysore pak", "icon": "fa-candy-cane", "bg": "sweet-bg"},
            {"name": "Pickles", "desc": "Clay jar sun-cured traditional thokku", "icon": "fa-jar", "bg": "pickle-bg"},
            {"name": "Beverages", "desc": "Kumbakonam degree coffee & Nilgiri tea", "icon": "fa-mug-hot", "bg": "coffee-bg"},
            {"name": "Homemade Food Products", "desc": "Handcrafted rice & millet mixes", "icon": "fa-bowl-rice", "bg": "millet-bg"},
            {"name": "Fresh Regional Foods", "desc": "Madurai Kari Dosa, Biryani & regional meals", "icon": "fa-utensils", "bg": "fresh-bg"}
        ]

        popular_cities = [
            {"name": "Chennai", "cuisine": "Chettinad & South Delicacies", "count": "15+ Makers"},
            {"name": "Madurai", "cuisine": "Kari Dosa & Traditional Crisps", "count": "12+ Makers"},
            {"name": "Dindigul", "cuisine": "Authentic Biryani Spices", "count": "8+ Makers"},
            {"name": "Tirunelveli", "cuisine": "Ghee Halwa & Palm Sweets", "count": "10+ Makers"},
            {"name": "Kumbakonam", "cuisine": "Degree Coffee & Delta Pickles", "count": "6+ Makers"}
        ]

        return render_template(
            'index.html',
            popular_foods=popular_foods,
            featured_makers=featured_makers,
            fresh_foods=fresh_foods,
            category_highlights=category_highlights,
            popular_cities=popular_cities
        )

    @app.route('/api/system-diag')
    def system_diag():
        from flask import jsonify
        env_keys = [k for k in os.environ.keys() if not k.startswith('_') and 'SECRET' not in k and 'KEY' not in k and 'TOKEN' not in k]
        return jsonify({
            'keys': env_keys,
            'has_database_url': 'DATABASE_URL' in os.environ,
            'has_postgres_url': 'POSTGRES_URL' in os.environ,
            'has_kv_url': 'KV_URL' in os.environ or 'KV_REST_API_URL' in os.environ,
            'db_val': os.environ.get('DATABASE_URL', '')[:20] if 'DATABASE_URL' in os.environ else ''
        })

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('base.html', error_title="404 - Page Not Found", error_msg="The regional recipe or page you are looking for could not be found."), 404

    @app.errorhandler(403)
    def access_forbidden(e):
        return render_template('base.html', error_title="403 - Access Denied", error_msg="You do not have permission to view this section."), 403

    @app.errorhandler(500)
    def internal_error(e):
        return render_template('base.html', error_title="500 - Server Error", error_msg="Something went wrong while processing your culinary request. Please try again."), 500

    return app

def get_local_ip():
    """Detect local LAN IP address for network sharing."""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'

if __name__ == '__main__':
    local_ip = get_local_ip()
    port = 5000
    print("\n=======================================================")
    print("  FlavorBridge Server is running on your Local Network!")
    print("=======================================================")
    print(f"  * Local machine URL:  http://127.0.0.1:{port} or http://localhost:{port}")
    print(f"  * Network device URL: http://{local_ip}:{port}")
    print("  (Any phone, tablet, or laptop on the same Wi-Fi can now open the Network URL)")
    print("=======================================================\n")

    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=port)
