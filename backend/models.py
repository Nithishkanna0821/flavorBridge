from datetime import datetime
from backend.extensions import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='customer')  # 'customer' or 'food_maker'
    phone = db.Column(db.String(20), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    address = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    food_maker_profile = db.relationship('FoodMaker', backref='user', uselist=False, cascade='all, delete-orphan')
    cart = db.relationship('Cart', backref='customer', uselist=False, cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='customer', lazy=True)
    reviews = db.relationship('Review', backref='customer', lazy=True)
    interactions = db.relationship('Interaction', backref='customer', lazy=True)

    def is_food_maker(self):
        return self.role == 'food_maker'

    def is_customer(self):
        return self.role == 'customer'

    def __repr__(self):
        return f'<User {self.email} ({self.role})>'


class FoodMaker(db.Model):
    __tablename__ = 'food_makers'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    speciality = db.Column(db.String(200), nullable=True)
    years_experience = db.Column(db.Integer, default=0)
    cuisines = db.Column(db.String(255), nullable=True)  # e.g., 'Chettinad, Madurai, South Indian'
    description = db.Column(db.Text, nullable=True)
    verification_status = db.Column(db.String(30), default='Verification Pending')  # 'Verification Pending' or 'Verified'
    verification_score = db.Column(db.Integer, default=0)  # 0 to 100
    is_verified = db.Column(db.Boolean, default=False)
    profile_image = db.Column(db.String(255), nullable=True)

    # Relationships
    products = db.relationship('Product', backref='food_maker', lazy=True, cascade='all, delete-orphan')
    order_items = db.relationship('OrderItem', backref='food_maker', lazy=True)
    reviews = db.relationship('Review', backref='food_maker', lazy=True)
    daily_verifications = db.relationship('DailyVerification', backref='food_maker', lazy=True, cascade='all, delete-orphan', order_by='desc(DailyVerification.created_at)')

    @property
    def today_verification(self):
        """Fetch today's daily ingredient & dish verification log if submitted today."""
        today_str = datetime.utcnow().strftime('%Y-%m-%d')
        return DailyVerification.query.filter_by(food_maker_id=self.id, log_date=today_str).first()

    @property
    def is_daily_verified(self):
        """Returns True if the food maker has completed their daily ingredients & dish log today."""
        return self.today_verification is not None

    def calculate_verification_score(self):
        """
        Scoring out of 100:
        - Profile completed (name, address, city, phone) +20
        - Speciality provided +20
        - Experience provided (> 0) +20
        - Food/profile images provided +20
        - Food details/description provided +20
        Score >= 80 -> Verified Food Maker (is_verified = True)
        """
        score = 0
        user = self.user
        
        # 1. Profile completed (+20)
        if user and user.name and user.city and user.address and user.phone:
            score += 20
        
        # 2. Speciality provided (+20)
        if self.speciality and len(self.speciality.strip()) > 3:
            score += 20
            
        # 3. Experience provided (+20)
        if self.years_experience and self.years_experience > 0:
            score += 20
            
        # 4. Images provided (+20)
        has_prod_image = any(p.image for p in self.products) if self.products else False
        has_daily_image = bool(self.today_verification and self.today_verification.dish_image)
        if self.profile_image or has_prod_image or has_daily_image:
            score += 20
            
        # 5. Food details / description provided (+20)
        if (self.description and len(self.description.strip()) > 15) or (self.products and len(self.products) > 0) or self.is_daily_verified:
            score += 20
            
        self.verification_score = score
        self.is_verified = score >= 80
        self.verification_status = 'Verified' if self.is_verified else 'Verification Pending'
        return score

    @property
    def average_rating(self):
        all_reviews = self.reviews
        if not all_reviews:
            prod_reviews = [r for p in self.products for r in p.reviews]
            if prod_reviews:
                return round(sum(r.rating for r in prod_reviews) / len(prod_reviews), 1)
            return 5.0
        return round(sum(r.rating for r in all_reviews) / len(all_reviews), 1)

    @property
    def total_reviews_count(self):
        prod_reviews_count = sum(len(p.reviews) for p in self.products)
        return len(self.reviews) + prod_reviews_count

    def __repr__(self):
        return f'<FoodMaker {self.id} (Verified: {self.is_verified})>'


class DailyVerification(db.Model):
    __tablename__ = 'daily_verifications'

    id = db.Column(db.Integer, primary_key=True)
    food_maker_id = db.Column(db.Integer, db.ForeignKey('food_makers.id', ondelete='CASCADE'), nullable=False, index=True)
    log_date = db.Column(db.String(20), nullable=False, index=True)  # YYYY-MM-DD
    ingredients_used = db.Column(db.Text, nullable=False)
    dishes_prepared = db.Column(db.String(255), nullable=True)
    dish_image = db.Column(db.String(255), nullable=True)
    sourcing_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<DailyVerification maker={self.food_maker_id} date={self.log_date}>'


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    food_maker_id = db.Column(db.Integer, db.ForeignKey('food_makers.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(150), nullable=False, index=True)
    category = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    ingredients = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    city = db.Column(db.String(100), nullable=False, index=True)
    region = db.Column(db.String(100), nullable=True)
    image = db.Column(db.String(255), nullable=True)
    stock = db.Column(db.Integer, default=10)
    product_type = db.Column(db.String(50), nullable=False, default='Packaged Food')  # 'Packaged Food' or 'Fresh Food'
    preparation_time = db.Column(db.String(50), nullable=True, default='1-2 days')
    net_quantity = db.Column(db.String(50), nullable=True, default='250g')  # e.g., '500g', '150g', '250g', '1 kg', '1 Plate'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    cart_items = db.relationship('CartItem', backref='product', lazy=True, cascade='all, delete-orphan')
    order_items = db.relationship('OrderItem', backref='product', lazy=True)
    reviews = db.relationship('Review', backref='product', lazy=True, cascade='all, delete-orphan')
    interactions = db.relationship('Interaction', backref='product', lazy=True, cascade='all, delete-orphan')

    @property
    def average_rating(self):
        if not self.reviews:
            return 4.8  # Default positive score for new listings
        return round(sum(r.rating for r in self.reviews) / len(self.reviews), 1)

    @property
    def rating_count(self):
        return len(self.reviews)

    def __repr__(self):
        return f'<Product {self.name} - ₹{self.price}>'


class Cart(db.Model):
    __tablename__ = 'cart'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)

    # Relationships
    items = db.relationship('CartItem', backref='cart', lazy=True, cascade='all, delete-orphan')

    @property
    def total_amount(self):
        return sum(item.quantity * item.product.price for item in self.items if item.product)

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items)

    @property
    def food_maker(self):
        """Returns the FoodMaker instance for the items currently in the cart."""
        for item in self.items:
            if item.product and item.product.food_maker:
                return item.product.food_maker
        return None

    @property
    def food_maker_id(self):
        maker = self.food_maker
        return maker.id if maker else None

    def __repr__(self):
        return f'<Cart {self.id} for User {self.customer_id}>'


class CartItem(db.Model):
    __tablename__ = 'cart_items'

    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id', ondelete='CASCADE'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)

    @property
    def subtotal(self):
        if self.product:
            return self.quantity * self.product.price
        return 0.0

    def __repr__(self):
        return f'<CartItem prod={self.product_id} qty={self.quantity}>'


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    address = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False, default='Tamil Nadu')
    pincode = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False, default='Cash on Delivery')
    # Status options: 'Pending', 'Accepted', 'Preparing', 'Shipped', 'Out for Delivery', 'Delivered', 'Cancelled'
    status = db.Column(db.String(50), nullable=False, default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

    @property
    def has_fresh_food(self):
        return any(item.product and item.product.product_type == 'Fresh Food' for item in self.items)

    @property
    def food_maker(self):
        """Returns the primary FoodMaker for this order."""
        for item in self.items:
            if item.food_maker:
                return item.food_maker
        return None

    @property
    def status_step(self):
        # Steps for progress display: 1=Pending, 2=Accepted, 3=Preparing, 4=Shipped/Out for Delivery, 5=Delivered
        order_status = self.status.lower()
        if 'pending' in order_status:
            return 1
        elif 'accepted' in order_status:
            return 2
        elif 'preparing' in order_status:
            return 3
        elif 'shipped' in order_status or 'out for delivery' in order_status:
            return 4
        elif 'delivered' in order_status:
            return 5
        return 1

    def __repr__(self):
        return f'<Order #{self.id} status={self.status} total=₹{self.total_amount}>'


class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    food_maker_id = db.Column(db.Integer, db.ForeignKey('food_makers.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False)  # Unit price at time of purchase

    @property
    def subtotal(self):
        return self.quantity * self.price

    def __repr__(self):
        return f'<OrderItem order={self.order_id} prod={self.product_id} qty={self.quantity}>'


class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), nullable=True)
    food_maker_id = db.Column(db.Integer, db.ForeignKey('food_makers.id', ondelete='CASCADE'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1 to 5
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Review {self.rating}* by user {self.customer_id}>'


class Interaction(db.Model):
    __tablename__ = 'interactions'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    # Types: 'VIEW', 'CART', 'PURCHASE', 'LIKE'
    interaction_type = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Interaction {self.interaction_type} user={self.customer_id} prod={self.product_id}>'
