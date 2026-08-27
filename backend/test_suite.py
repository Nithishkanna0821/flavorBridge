import unittest
import sys
import os

# Add workspace root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import create_app
from backend.extensions import db
from backend.models import User, FoodMaker, Product, Order, OrderItem, Review, Interaction, Cart, CartItem
from backend.ai.smart_search import search_products
from backend.ai.recommender import get_personalized_recommendations, get_similar_products
from backend.ai.recipe_partner_matcher import match_recipe_partners
from backend.ai.food_assistant import process_food_assistant_query, parse_user_query
from backend.utils.security import hash_password, verify_password

class FlavorBridgeTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_01_database_seed_integrity(self):
        """Verify seeded food makers, customers, and categories exist."""
        users_count = User.query.count()
        makers_count = FoodMaker.query.count()
        products_count = Product.query.count()

        self.assertGreaterEqual(users_count, 7, "Expected at least 7 users (5 makers + 2 customers)")
        self.assertGreaterEqual(makers_count, 5, "Expected at least 5 food makers")
        self.assertGreaterEqual(products_count, 35, "Expected at least 35 products")

        # Verify all 7 categories are present
        categories = db.session.query(Product.category).distinct().all()
        cat_names = [c[0] for c in categories]
        expected_cats = [
            "Spice Powders & Seasonings",
            "Traditional Snacks",
            "Traditional Sweets",
            "Pickles",
            "Beverages",
            "Homemade Food Products",
            "Fresh Regional Foods"
        ]
        for ec in expected_cats:
            self.assertIn(ec, cat_names, f"Missing category: {ec}")

        # Verify net_quantity and unique non-repeated images on every product
        all_products = Product.query.all()
        prod_images = []
        for prod in all_products:
            self.assertIsNotNone(prod.net_quantity, f"Product {prod.name} is missing net_quantity")
            self.assertGreater(len(prod.net_quantity.strip()), 0)
            self.assertIsNotNone(prod.image, f"Product {prod.name} is missing an image")
            prod_images.append(prod.image)
        
        # Verify 100% distinct, non-repeated images
        self.assertEqual(len(prod_images), len(set(prod_images)), "Duplicate images detected among products!")
        print(f"[TEST PASS] Database seed integrity verified (all {len(all_products)} products have unique non-repeated images and net_quantity configured).")

    def test_02_password_hashing(self):
        """Verify Werkzeug password hashing."""
        pwd = "testpassword123"
        h = hash_password(pwd)
        self.assertNotEqual(pwd, h)
        self.assertTrue(verify_password(h, pwd))
        self.assertFalse(verify_password(h, "wrongpassword"))
        print("[TEST PASS] Password hashing verified.")

    def test_03_ai_smart_search(self):
        """Verify Scikit-Learn TF-IDF Smart Search."""
        all_prods = Product.query.all()
        
        # Test search for spicy Tamil food
        results = search_products("spicy Tamil chicken", all_prods)
        self.assertTrue(len(results) > 0)
        top_prod, score = results[0]
        self.assertTrue("chicken" in top_prod.name.lower() or "masala" in top_prod.name.lower() or "chettinad" in top_prod.name.lower())
        print(f"[TEST PASS] Smart Search match: '{top_prod.name}' (Score: {score:.2f})")

    def test_04_ai_recommender(self):
        """Verify AI personalized hybrid recommendations."""
        customer = User.query.filter_by(role='customer').first()
        recs = get_personalized_recommendations(user_id=customer.id, user_city=customer.city)
        
        self.assertIn('for_you', recs)
        self.assertIn('trending', recs)
        self.assertIn('regional_delicacies', recs)
        self.assertIn('fresh_specials', recs)
        self.assertTrue(len(recs['for_you']) > 0)
        print(f"[TEST PASS] AI Recommendations generated: {len(recs['for_you'])} personalized picks.")

    def test_05_ai_recipe_partner_matcher(self):
        """Verify Local Recipe Partner Matcher ranking."""
        matches = match_recipe_partners("Madurai Kari Dosa", customer_city="Madurai")
        self.assertTrue(len(matches) > 0)
        top_match = matches[0]
        self.assertGreaterEqual(top_match['match_score'], 50)
        self.assertTrue(top_match['maker'].is_verified)
        print(f"[TEST PASS] Recipe Partner Matcher: {top_match['user'].name} (Score: {top_match['match_score']}%)")

    def test_06_ai_food_assistant(self):
        """Verify Rule-Based NLP Food Assistant query parsing and response."""
        res = process_food_assistant_query("I want spicy food from Tamil Nadu under ₹300", customer_city="Chennai")
        self.assertTrue(len(res['products']) > 0)
        self.assertIn('spicy', res['filters']['tastes'])
        self.assertEqual(res['filters']['max_budget'], 300.0)
        self.assertIn("confirmation", res['safety_note'])
        print(f"[TEST PASS] AI Food Assistant parsed query and returned {len(res['products'])} recommendations.")

    def test_07_http_routes_and_checkout_flow(self):
        """Verify end-to-end Flask routes: index, login, cart, order placement, order detail."""
        # 1. Homepage
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Discover the Taste of", resp.data)

        # 2. Products List
        resp = self.client.get('/products')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"All Regional Delicacies", resp.data)

        # 3. Customer Login
        resp = self.client.post('/login', data={
            'email': 'ananya@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

        # 4. Add to Cart
        prod = Product.query.first()
        resp = self.client.post('/add-to-cart', json={
            'product_id': prod.id,
            'quantity': 2
        })
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json['success'])

        # 5. Place Order (COD)
        resp = self.client.post('/place-order', data={
            'name': 'Ananya Sharma',
            'phone': '9876543210',
            'address': '402, Anna Nagar',
            'city': 'Chennai',
            'state': 'Tamil Nadu',
            'pincode': '600040',
            'payment_method': 'Cash on Delivery'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Order Placed Successfully", resp.data)

        # 6. Food Maker Verification Calculation
        maker = FoodMaker.query.first()
        score = maker.calculate_verification_score()
        self.assertGreaterEqual(score, 80)
        self.assertTrue(maker.is_verified)
        print("[TEST PASS] Full customer cart, checkout, and verification flows executed successfully.")

    def test_08_daily_verification_system(self):
        """Verify Daily Ingredients & Final Dish Upload, daily refresh logic, and status."""
        maker = FoodMaker.query.filter_by(user_id=3).first()  # Priya (maker1)
        self.assertIsNotNone(maker)

        # 1. Log in as Food Maker Priya
        login_resp = self.client.post('/login', data={
            'email': 'priya@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(login_resp.status_code, 200)

        # 2. View Verification Page
        resp = self.client.get('/verification')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Daily Ingredients", resp.data)

        # 3. Post Daily Verification Log
        import io
        fake_image = (io.BytesIO(b"fake image data"), "fresh_kari_dosa.jpg")
        upload_resp = self.client.post('/verification/daily-upload', data={
            'ingredients_used': 'Fresh farm country eggs, minced mutton, stone-ground Chettinad kalpasi masala, cold-pressed sesame oil',
            'dishes_prepared': 'Madurai Kari Dosa, Chettinad Chicken Curry',
            'sourcing_notes': '100% natural oil from Chettinad village mill',
            'dish_image': fake_image
        }, follow_redirects=True)
        self.assertEqual(upload_resp.status_code, 200)
        self.assertIn(b"Fresh Batch Verified Today", upload_resp.data)

        # 4. Verify helper property
        self.assertTrue(maker.is_daily_verified)
        self.assertIsNotNone(maker.today_verification)
        self.assertIn("country eggs", maker.today_verification.ingredients_used.lower())
        print(f"[TEST PASS] Daily Verification System: Logged for {maker.today_verification.log_date} with dish '{maker.today_verification.dishes_prepared}'.")

    def test_09_separate_login_portals_and_role_scoping(self):
        """Verify distinct Customer and Food Maker login portals and role-restricted routes."""
        # 1. Customer Login Portal View
        resp_cust_page = self.client.get('/login?role=customer')
        self.assertEqual(resp_cust_page.status_code, 200)
        self.assertIn(b"Customer Sign In", resp_cust_page.data)

        # 2. Food Maker Login Portal View
        resp_maker_page = self.client.get('/login?role=food_maker')
        self.assertEqual(resp_maker_page.status_code, 200)
        self.assertIn(b"Food Maker Partner Portal", resp_maker_page.data)

        # 3. Direct Maker Portal Shortcut Routes
        resp_maker_shortcut = self.client.get('/maker-login', follow_redirects=True)
        self.assertEqual(resp_maker_shortcut.status_code, 200)
        self.assertIn(b"Food Maker Partner Portal", resp_maker_shortcut.data)

        # 4. Customer Login Flow
        cust_login = self.client.post('/login', data={
            'email': 'ananya@example.com',
            'password': 'password123',
            'role': 'customer'
        }, follow_redirects=True)
        self.assertEqual(cust_login.status_code, 200)
        self.assertIn(b"Welcome back, Ananya Sharma", cust_login.data)

        # 5. Role Security: Customer cannot access Food Maker dashboard
        restricted_resp = self.client.get('/food-maker/dashboard', follow_redirects=True)
        self.assertEqual(restricted_resp.status_code, 200)
        self.assertIn(b"Access restricted", restricted_resp.data)

        # 6. Logout
        self.client.get('/logout')

        # 7. Food Maker Login Flow -> Direct to Maker Dashboard
        maker_login = self.client.post('/login', data={
            'email': 'priya@example.com',
            'password': 'password123',
            'role': 'food_maker'
        }, follow_redirects=True)
        self.assertEqual(maker_login.status_code, 200)
        self.assertIn(b"Welcome to your Kitchen Dashboard", maker_login.data)
        self.assertIn(b"Daily Ingredients & Dish Log", maker_login.data)
        print("[TEST PASS] Separate login portals, shortcuts, and role-scoped route protection verified.")

    def test_10_forgot_and_reset_password_flow(self):
        """Verify Forgot Password account recovery and password reset flow."""
        # 1. Access Forgot Password page
        resp_forgot = self.client.get('/forgot-password')
        self.assertEqual(resp_forgot.status_code, 200)
        self.assertIn(b"Reset Your Password", resp_forgot.data)

        # 2. Submit registered email
        resp_verify = self.client.post('/forgot-password', data={
            'email': 'rajesh@example.com'
        }, follow_redirects=True)
        self.assertEqual(resp_verify.status_code, 200)
        self.assertIn(b"Set New Password", resp_verify.data)

        # 3. Submit new matching password
        resp_reset = self.client.post('/reset-password', data={
            'password': 'newsecretpassword123',
            'confirm_password': 'newsecretpassword123'
        }, follow_redirects=True)
        self.assertEqual(resp_reset.status_code, 200)
        self.assertIn(b"Your password has been successfully reset", resp_reset.data)

        # 4. Login with newly updated password
        new_login = self.client.post('/login', data={
            'email': 'rajesh@example.com',
            'password': 'newsecretpassword123'
        }, follow_redirects=True)
        self.assertEqual(new_login.status_code, 200)
        self.assertIn(b"Welcome back, Rajesh Kumar", new_login.data)

        # Reset password back to password123 for test reproducibility
        user = User.query.filter_by(email='rajesh@example.com').first()
        user.password_hash = hash_password('password123')
        db.session.commit()
        print("[TEST PASS] Forgot password verification and reset flow validated end-to-end.")

    def test_11_single_kitchen_cart_enforcement(self):
        """Verify that customers can only order from one kitchen at a time, conflict detection, and reset."""
        # 1. Log in as Customer Ananya
        self.client.post('/login', data={
            'email': 'ananya@example.com',
            'password': 'password123',
            'role': 'customer'
        }, follow_redirects=True)

        # Clear any existing cart items for customer
        user = User.query.filter_by(email='ananya@example.com').first()
        cart = Cart.query.filter_by(customer_id=user.id).first()
        if cart:
            for item in list(cart.items):
                db.session.delete(item)
            db.session.commit()

        # Find two products from two different food makers
        prod_maker1 = Product.query.filter_by(food_maker_id=1).first()
        prod_maker2 = Product.query.filter_by(food_maker_id=2).first()
        self.assertIsNotNone(prod_maker1)
        self.assertIsNotNone(prod_maker2)
        self.assertNotEqual(prod_maker1.food_maker_id, prod_maker2.food_maker_id)

        # 2. Add product from Kitchen 1 -> Should succeed (200 OK)
        resp1 = self.client.post('/add-to-cart', json={
            'product_id': prod_maker1.id,
            'quantity': 1
        })
        self.assertEqual(resp1.status_code, 200)
        self.assertTrue(resp1.json['success'])

        # Check cart maker
        cart = Cart.query.filter_by(customer_id=user.id).first()
        self.assertEqual(cart.food_maker_id, prod_maker1.food_maker_id)

        # 3. Attempt to add product from Kitchen 2 without reset -> Should return 409 Conflict
        resp2 = self.client.post('/add-to-cart', json={
            'product_id': prod_maker2.id,
            'quantity': 1,
            'reset_cart': False
        })
        self.assertEqual(resp2.status_code, 409)
        self.assertFalse(resp2.json['success'])
        self.assertTrue(resp2.json['conflict'])
        self.assertIn("one kitchen", resp2.json['message'].lower())

        # 4. Add product from Kitchen 2 with reset_cart: True -> Should succeed and replace cart
        resp3 = self.client.post('/add-to-cart', json={
            'product_id': prod_maker2.id,
            'quantity': 2,
            'reset_cart': True
        })
        self.assertEqual(resp3.status_code, 200)
        self.assertTrue(resp3.json['success'])

        # Check cart updated to Kitchen 2
        cart = Cart.query.filter_by(customer_id=user.id).first()
        self.assertEqual(cart.food_maker_id, prod_maker2.food_maker_id)
        self.assertEqual(cart.total_items, 2)
        self.assertEqual(len(cart.items), 1)
        self.assertEqual(cart.items[0].product_id, prod_maker2.id)

        # 5. Place order for Kitchen 2
        order_resp = self.client.post('/place-order', data={
            'name': 'Ananya Sharma',
            'phone': '9876543210',
            'address': '402, Anna Nagar',
            'city': 'Chennai',
            'state': 'Tamil Nadu',
            'pincode': '600040',
            'payment_method': 'Cash on Delivery'
        }, follow_redirects=True)
        self.assertEqual(order_resp.status_code, 200)
        self.assertIn(b"Order Placed Successfully", order_resp.data)

        # Verify order belongs strictly to Kitchen 2
        last_order = Order.query.filter_by(customer_id=user.id).order_by(Order.created_at.desc()).first()
        self.assertIsNotNone(last_order)
        self.assertEqual(last_order.food_maker.id, prod_maker2.food_maker_id)
        print(f"[TEST PASS] Single Kitchen Cart Enforcement: Successfully prevented mixed-kitchen carts, resolved conflict with reset, and placed single-kitchen order #{last_order.id}.")

if __name__ == '__main__':
    unittest.main()



