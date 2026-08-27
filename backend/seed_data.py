from datetime import datetime, timedelta
from backend.extensions import db
from backend.models import User, FoodMaker, Product, Review, Interaction, Order, OrderItem, DailyVerification
from backend.utils.security import hash_password

def seed_database():
    """Populates the database with demo users, food makers, authentic products, and reviews."""
    print("[INFO] Checking database and seeding sample data...")
    
    # Check if data already exists
    if User.query.first():
        print("[INFO] Database already contains data. Skipping seed.")
        return

    # -------------------------------------------------------------
    # 1. CREATE DEMO CUSTOMERS
    # -------------------------------------------------------------
    customer1 = User(
        name="Ananya Sharma",
        email="ananya@example.com",
        password_hash=hash_password("password123"),
        role="customer",
        phone="9876543210",
        city="Chennai",
        address="Flat 402, Royal Palms, Anna Nagar, Chennai",
        created_at=datetime.utcnow() - timedelta(days=30)
    )
    
    customer2 = User(
        name="Rajesh Kumar",
        email="rajesh@example.com",
        password_hash=hash_password("password123"),
        role="customer",
        phone="9845123456",
        city="Madurai",
        address="14/B, West Masi Street, Madurai",
        created_at=datetime.utcnow() - timedelta(days=20)
    )
    
    db.session.add_all([customer1, customer2])
    db.session.flush()

    # -------------------------------------------------------------
    # 2. CREATE 5 VERIFIED FOOD MAKERS
    # -------------------------------------------------------------
    # 1. Priya Traditional Foods (Chennai, Madurai Cuisine)
    maker1_user = User(
        name="Priya Sundaram",
        email="priya@example.com",
        password_hash=hash_password("password123"),
        role="food_maker",
        phone="9884011223",
        city="Chennai",
        address="No. 12, Temple View Avenue, Mylapore, Chennai",
        created_at=datetime.utcnow() - timedelta(days=60)
    )
    db.session.add(maker1_user)
    db.session.flush()
    
    maker1 = FoodMaker(
        user_id=maker1_user.id,
        speciality="Madurai & Chettinad Gravies, Kari Dosa, and Fresh Biryani",
        years_experience=12,
        cuisines="Madurai, Chettinad, South Indian",
        description="Priya Traditional Foods brings time-honored Chettinad & Madurai heirloom recipes to your dining table. Everything is prepared in brass and clay cookware with stone-ground natural spices.",
        verification_status="Verified",
        verification_score=100,
        is_verified=True,
        profile_image="priya_kitchen.jpg"
    )
    
    # 2. Kumar Homemade Foods (Madurai, Traditional Snacks)
    maker2_user = User(
        name="Kumaravel M",
        email="kumar@example.com",
        password_hash=hash_password("password123"),
        role="food_maker",
        phone="9789012345",
        city="Madurai",
        address="45, South Veli Street, Madurai",
        created_at=datetime.utcnow() - timedelta(days=50)
    )
    db.session.add(maker2_user)
    db.session.flush()
    
    maker2 = FoodMaker(
        user_id=maker2_user.id,
        speciality="Crispy Murukku, Thattai, and Authentic Southern Crisps",
        years_experience=15,
        cuisines="Madurai, Tamil Nadu Snacks",
        description="Kumar Homemade Foods is famous for traditional wood-pressed groundnut oil fried snacks made with stone-milled rice flour and fragrant sesame seeds.",
        verification_status="Verified",
        verification_score=100,
        is_verified=True,
        profile_image="kumar_foods.jpg"
    )

    # 3. Lakshmi Regional Kitchen (Dindigul, Dindigul Masala)
    maker3_user = User(
        name="Lakshmi Narayanan",
        email="lakshmi@example.com",
        password_hash=hash_password("password123"),
        role="food_maker",
        phone="9443012345",
        city="Dindigul",
        address="8/2, Round Road, Dindigul",
        created_at=datetime.utcnow() - timedelta(days=45)
    )
    db.session.add(maker3_user)
    db.session.flush()
    
    maker3 = FoodMaker(
        user_id=maker3_user.id,
        speciality="Dindigul Biryani Masalas, Sun-dried Spices & Podis",
        years_experience=10,
        cuisines="Dindigul, Tamil Nadu",
        description="Handcrafted spice blends sun-dried in the foothills of Sirumalai. Famous for original Dindigul biryani spices and fragrant idli podis.",
        verification_status="Verified",
        verification_score=95,
        is_verified=True,
        profile_image="lakshmi_kitchen.jpg"
    )

    # 4. Arun Home Foods (Tirunelveli, Traditional Sweets)
    maker4_user = User(
        name="Arunachalam S",
        email="arun@example.com",
        password_hash=hash_password("password123"),
        role="food_maker",
        phone="9381012345",
        city="Tirunelveli",
        address="23, Swamy Sannathi Street, Tirunelveli Town",
        created_at=datetime.utcnow() - timedelta(days=70)
    )
    db.session.add(maker4_user)
    db.session.flush()
    
    maker4 = FoodMaker(
        user_id=maker4_user.id,
        speciality="Authentic Tirunelveli Wheat Halwa & Traditional Sweets",
        years_experience=18,
        cuisines="Tirunelveli, South Indian Sweets",
        description="Using mineral-rich Thamirabarani water, fermented whole samba wheat milk, and pure country ghee to create melt-in-the-mouth Tirunelveli halwa.",
        verification_status="Verified",
        verification_score=100,
        is_verified=True,
        profile_image="arun_sweets.jpg"
    )

    # 5. Meena Traditional Foods (Kumbakonam, Traditional Coffee)
    maker5_user = User(
        name="Meenakshi R",
        email="meena@example.com",
        password_hash=hash_password("password123"),
        role="food_maker",
        phone="9176012345",
        city="Kumbakonam",
        address="55, Mahamaham Tank South, Kumbakonam",
        created_at=datetime.utcnow() - timedelta(days=40)
    )
    db.session.add(maker5_user)
    db.session.flush()
    
    maker5 = FoodMaker(
        user_id=maker5_user.id,
        speciality="Kumbakonam Degree Coffee & Natural Pickles",
        years_experience=8,
        cuisines="Kumbakonam, Thanjavur, Cauvery Delta",
        description="Freshly roasted plantation peaberry coffee beans slow-ground to perfection, along with cold-pressed gingelly oil pickles made in traditional ceramic jars (bharanis).",
        verification_status="Verified",
        verification_score=90,
        is_verified=True,
        profile_image="meena_foods.jpg"
    )

    db.session.add_all([maker1, maker2, maker3, maker4, maker5])
    db.session.flush()

    # -------------------------------------------------------------
    # 3. SEED PRODUCTS ACROSS ALL 7 CATEGORIES
    # -------------------------------------------------------------
    products_data = [
        # Category 1: Spice Powders & Seasonings
        {
            "maker": maker3,
            "name": "Chicken Masala Powder",
            "category": "Spice Powders & Seasonings",
            "price": 140.0,
            "stock": 35,
            "product_type": "Packaged Food",
            "city": "Dindigul",
            "region": "Sirumalai Region",
            "prep_time": "1 day",
            "description": "Slow-roasted whole spices including coriander, black pepper, cinnamon, and cumin blended for deep, aromatic chicken curries.",
            "ingredients": "Coriander, Cumin, Black Pepper, Cinnamon, Cardamom, Fennel, Curry Leaves, Red Chilli",
            "image": "chicken_masala_powder.jpg"
        },
        {
            "maker": maker3,
            "name": "Mutton Masala Powder",
            "category": "Spice Powders & Seasonings",
            "price": 160.0,
            "stock": 30,
            "product_type": "Packaged Food",
            "city": "Dindigul",
            "region": "Sirumalai Region",
            "prep_time": "1 day",
            "description": "Signature Dindigul style mutton masala mix with stone-ground cloves, star anise, and roasted dry coconut.",
            "ingredients": "Stone Ground Cloves, Star Anise, Black Cardamom, Dry Ginger, Coriander, Pepper",
            "image": "mutton_masala_powder.jpg"
        },
        {
            "maker": maker3,
            "name": "Sambar Powder",
            "category": "Spice Powders & Seasonings",
            "price": 120.0,
            "stock": 50,
            "product_type": "Packaged Food",
            "city": "Dindigul",
            "region": "Tamil Nadu",
            "prep_time": "1 day",
            "description": "Grandma's recipe sambar podi made with Guntur chillies, split chickpeas, toor dal, and aromatic coriander.",
            "ingredients": "Toor Dal, Chana Dal, Coriander Seeds, Guntur Red Chillies, Fenugreek, Asafoetida, Turmeric",
            "image": "sambar_powder.jpg"
        },
        {
            "maker": maker3,
            "name": "Rasam Powder",
            "category": "Spice Powders & Seasonings",
            "price": 110.0,
            "stock": 45,
            "product_type": "Packaged Food",
            "city": "Dindigul",
            "region": "Sirumalai Region",
            "prep_time": "1 day",
            "description": "Spicy and digestive rasam podi with Tellicherry black pepper, cumin seeds, and mountain garlic.",
            "ingredients": "Black Pepper, Cumin, Toor Dal, Red Chilli, Curry Leaves, Asafoetida",
            "image": "rasam_powder.jpg"
        },
        {
            "maker": maker3,
            "name": "Biryani Masala",
            "category": "Spice Powders & Seasonings",
            "price": 180.0,
            "stock": 40,
            "product_type": "Packaged Food",
            "city": "Dindigul",
            "region": "Dindigul",
            "prep_time": "1 day",
            "description": "The secret blend behind famous South Indian Seeraga Samba Biryani with mace, nutmeg, and stone flowers (kalpasi).",
            "ingredients": "Kalpasi (Stone Flower), Mace, Nutmeg, Cinnamon, Green Cardamom, Cloves, Bay Leaf, Star Anise",
            "image": "biryani_masala.jpg"
        },
        {
            "maker": maker3,
            "name": "Curry Masala",
            "category": "Spice Powders & Seasonings",
            "price": 130.0,
            "stock": 25,
            "product_type": "Packaged Food",
            "city": "Dindigul",
            "region": "Tamil Nadu",
            "prep_time": "1 day",
            "description": "All-purpose vegetable and egg curry blend with balanced heat and warm earthy aroma.",
            "ingredients": "Coriander, Cumin, Mustard, Fenugreek, Turmeric, Black Pepper, Dried Curry Leaves",
            "image": "curry_masala.jpg"
        },
        {
            "maker": maker3,
            "name": "Pepper Powder",
            "category": "Spice Powders & Seasonings",
            "price": 150.0,
            "stock": 60,
            "product_type": "Packaged Food",
            "city": "Dindigul",
            "region": "Western Ghats",
            "prep_time": "1 day",
            "description": "Freshly crushed premium Malabar black peppercorns, packed with natural essential oils.",
            "ingredients": "100% Pure Black Peppercorns",
            "image": "pepper_powder.jpg"
        },
        {
            "maker": maker3,
            "name": "Idli Podi",
            "category": "Spice Powders & Seasonings",
            "price": 115.0,
            "stock": 55,
            "product_type": "Packaged Food",
            "city": "Dindigul",
            "region": "Tamil Nadu",
            "prep_time": "1 day",
            "description": "Gunpowder spiced chutney powder roasted in cold-pressed sesame oil. Perfect with warm soft idlis and crispy dosas.",
            "ingredients": "Urad Dal, Chana Dal, Roasted Sesame Seeds, Red Chillies, Salt, Asafoetida",
            "image": "idli_podi.jpg"
        },

        # Category 2: Traditional Snacks
        {
            "maker": maker2,
            "name": "Murukku",
            "category": "Traditional Snacks",
            "price": 95.0,
            "stock": 50,
            "product_type": "Packaged Food",
            "city": "Madurai",
            "region": "Madurai",
            "prep_time": "1 day",
            "description": "Traditional crunchy spiral snacks made with raw rice flour, urad dal, cumin seeds, and ajwain.",
            "ingredients": "Rice Flour, Urad Dal Flour, Butter, Cumin Seeds, Carom Seeds, Cold Pressed Oil, Salt",
            "image": "murukku.jpg"
        },
        {
            "maker": maker2,
            "name": "Kai Murukku",
            "category": "Traditional Snacks",
            "price": 120.0,
            "stock": 30,
            "product_type": "Packaged Food",
            "city": "Madurai",
            "region": "Chettinad",
            "prep_time": "2 days",
            "description": "Hand-twisted artisanal murukku made by master village women with rich butter aroma and crisp crunch.",
            "ingredients": "Parboiled Rice, Pure Ghee, Cumin, Sesame Seeds, Salt, Groundnut Oil",
            "image": "kai_murukku.jpg"
        },
        {
            "maker": maker2,
            "name": "Thattai",
            "category": "Traditional Snacks",
            "price": 100.0,
            "stock": 40,
            "product_type": "Packaged Food",
            "city": "Madurai",
            "region": "Tamil Nadu",
            "prep_time": "1 day",
            "description": "Flat, crunchy deep-fried savoury cracker loaded with soaked chana dal, curry leaves, and red chilli flakes.",
            "ingredients": "Rice Flour, Urad Dal, Soaked Chana Dal, Curry Leaves, Red Chilli Powder, Asafoetida",
            "image": "thattai.jpg"
        },
        {
            "maker": maker2,
            "name": "Seedai",
            "category": "Traditional Snacks",
            "price": 90.0,
            "stock": 35,
            "product_type": "Packaged Food",
            "city": "Madurai",
            "region": "Tamil Nadu",
            "prep_time": "1 day",
            "description": "Bite-sized crisp savoury snack balls packed with coconut bits and roasted sesame seeds.",
            "ingredients": "Processed Rice Flour, Roasted Gram Flour, Grated Coconut, Sesame Seeds, Butter",
            "image": "seedai.jpg"
        },
        {
            "maker": maker2,
            "name": "Mixture",
            "category": "Traditional Snacks",
            "price": 110.0,
            "stock": 45,
            "product_type": "Packaged Food",
            "city": "Madurai",
            "region": "Madurai",
            "prep_time": "1 day",
            "description": "Madurai style spicy mixture blend featuring sev, boondi, roasted peanuts, cashews, and crisp curry leaves.",
            "ingredients": "Gram Flour, Peanuts, Fried Gram, Roasted Cashews, Curry Leaves, Chilli, Garlic",
            "image": "mixture.jpg"
        },
        {
            "maker": maker2,
            "name": "Banana Chips",
            "category": "Traditional Snacks",
            "price": 130.0,
            "stock": 60,
            "product_type": "Packaged Food",
            "city": "Madurai",
            "region": "Kerala & Tamil Nadu",
            "prep_time": "1 day",
            "description": "Thin-sliced raw Nendran bananas crisped in 100% pure virgin coconut oil with a pinch of turmeric and rock salt.",
            "ingredients": "Nendran Bananas, Pure Coconut Oil, Rock Salt, Turmeric",
            "image": "banana_chips.jpg"
        },
        {
            "maker": maker2,
            "name": "Jackfruit Chips",
            "category": "Traditional Snacks",
            "price": 150.0,
            "stock": 25,
            "product_type": "Packaged Food",
            "city": "Madurai",
            "region": "Western Ghats",
            "prep_time": "2 days",
            "description": "Seasonal ripened raw jackfruit strands fried to a golden crunch. Highly aromatic and fiber-rich.",
            "ingredients": "Raw Wild Jackfruit, Coconut Oil, Sea Salt",
            "image": "jackfruit_chips.jpg"
        },

        # Category 3: Traditional Sweets
        {
            "maker": maker4,
            "name": "Tirunelveli Halwa",
            "category": "Traditional Sweets",
            "price": 220.0,
            "stock": 50,
            "product_type": "Packaged Food",
            "city": "Tirunelveli",
            "region": "Tirunelveli",
            "prep_time": "1 day",
            "description": "World-famous glossy, melt-in-mouth wheat halwa cooked in pure country ghee with Thamirabarani river water.",
            "ingredients": "Fermented Whole Wheat Milk, Pure Desi Ghee, Sugar, Cashew Nuts, Cardamom",
            "image": "tirunelveli_halwa.jpg"
        },
        {
            "maker": maker4,
            "name": "Mysore Pak",
            "category": "Traditional Sweets",
            "price": 190.0,
            "stock": 40,
            "product_type": "Packaged Food",
            "city": "Tirunelveli",
            "region": "South India",
            "prep_time": "1 day",
            "description": "Rich, porous and ghee-dripping royal sweet made with fine gram flour and aromatic cardamom.",
            "ingredients": "Besan (Gram Flour), Pure Ghee, Sugar, Cardamom",
            "image": "mysore_pak.jpg"
        },
        {
            "maker": maker4,
            "name": "Kovilpatti Kadalai Mittai",
            "category": "Traditional Sweets",
            "price": 85.0,
            "stock": 70,
            "product_type": "Packaged Food",
            "city": "Tirunelveli",
            "region": "Kovilpatti",
            "prep_time": "1 day",
            "description": "GI-tagged Kovilpatti peanut brittle made with organic dark sugarcane jaggery and dry ginger.",
            "ingredients": "Roasted Peanuts, Organic Sugarcane Jaggery, Cardamom, Dry Ginger",
            "image": "kadalai_mittai.jpg"
        },
        {
            "maker": maker4,
            "name": "Adhirasam",
            "category": "Traditional Sweets",
            "price": 140.0,
            "stock": 30,
            "product_type": "Packaged Food",
            "city": "Tirunelveli",
            "region": "Tamil Nadu",
            "prep_time": "2 days",
            "description": "Festive sweet pastry made from fermented raw rice dough and organic jaggery syrup with a soft chewy core.",
            "ingredients": "Raw Rice Flour, Palm Jaggery, Cardamom, Dry Ginger, Sesame Seeds, Ghee",
            "image": "adhirasam.jpg"
        },
        {
            "maker": maker4,
            "name": "Jangiri",
            "category": "Traditional Sweets",
            "price": 160.0,
            "stock": 25,
            "product_type": "Packaged Food",
            "city": "Tirunelveli",
            "region": "South India",
            "prep_time": "1 day",
            "description": "Juicy saffron-tinted floral swirls made of stone-ground urad dal batter soaked in rose-flavored sugar syrup.",
            "ingredients": "Urad Dal, Sugar Syrup, Rose Water, Saffron, Cardamom, Refined Oil",
            "image": "jangiri.jpg"
        },
        {
            "maker": maker4,
            "name": "Laddu",
            "category": "Traditional Sweets",
            "price": 150.0,
            "stock": 40,
            "product_type": "Packaged Food",
            "city": "Tirunelveli",
            "region": "South India",
            "prep_time": "1 day",
            "description": "Moti-choor style ghee laddus studded with plump raisins, melon seeds, and fragrant cloves.",
            "ingredients": "Gram Flour, Ghee, Sugar Syrup, Raisins, Cashews, Cloves, Edible Camphor",
            "image": "laddu.jpg"
        },
        {
            "maker": maker4,
            "name": "Palkova",
            "category": "Traditional Sweets",
            "price": 180.0,
            "stock": 35,
            "product_type": "Packaged Food",
            "city": "Tirunelveli",
            "region": "Srivilliputhur",
            "prep_time": "1 day",
            "description": "Authentic Srivilliputhur style condensed milk fudge prepared by slow simmering rich cow's milk for 4 hours.",
            "ingredients": "Full Cream Farm Milk, Organic Sugar, Ghee, Cardamom",
            "image": "palkova.jpg"
        },

        # Category 4: Pickles
        {
            "maker": maker5,
            "name": "Mango Pickle",
            "category": "Pickles",
            "price": 120.0,
            "stock": 45,
            "product_type": "Packaged Food",
            "city": "Kumbakonam",
            "region": "Thanjavur Delta",
            "prep_time": "1 day",
            "description": "Spicy and tangy tender cut raw mangoes cured with roasted fenugreek, mustard, and wood-pressed sesame oil.",
            "ingredients": "Raw Mangoes, Gingelly Oil, Red Chilli Powder, Fenugreek, Mustard Seeds, Asafoetida, Rock Salt",
            "image": "mango_pickle.jpg"
        },
        {
            "maker": maker5,
            "name": "Lemon Pickle",
            "category": "Pickles",
            "price": 110.0,
            "stock": 40,
            "product_type": "Packaged Food",
            "city": "Kumbakonam",
            "region": "Kumbakonam",
            "prep_time": "1 day",
            "description": "Sun-cured yellow lemons in ginger and green chilli spiced oil. Rich in Vitamin C and natural probitotics.",
            "ingredients": "Sun Cured Lemons, Green Chillies, Ginger, Mustard, Fenugreek, Sesame Oil, Rock Salt",
            "image": "lemon_pickle.jpg"
        },
        {
            "maker": maker5,
            "name": "Garlic Pickle",
            "category": "Pickles",
            "price": 150.0,
            "stock": 35,
            "product_type": "Packaged Food",
            "city": "Kumbakonam",
            "region": "Tamil Nadu",
            "prep_time": "1 day",
            "description": "Whole mountain garlic cloves slow-cooked in thick tamarind and red chilli reduction with cold-pressed oil.",
            "ingredients": "Whole Peeled Garlic, Tamarind Pulp, Red Chilli Powder, Fenugreek, Mustard, Gingelly Oil",
            "image": "garlic_pickle.jpg"
        },
        {
            "maker": maker5,
            "name": "Gooseberry Pickle",
            "category": "Pickles",
            "price": 135.0,
            "stock": 30,
            "product_type": "Packaged Food",
            "city": "Kumbakonam",
            "region": "Tamil Nadu",
            "prep_time": "1 day",
            "description": "Fresh whole Indian amla (gooseberries) steam-cooked and seasoned with traditional south Indian pickle spices.",
            "ingredients": "Indian Amla (Gooseberry), Fenugreek, Mustard, Red Chilli, Sesame Oil, Turmeric, Salt",
            "image": "gooseberry_pickle.jpg"
        },
        {
            "maker": maker5,
            "name": "Fish Pickle",
            "category": "Pickles",
            "price": 240.0,
            "stock": 25,
            "product_type": "Packaged Food",
            "city": "Kumbakonam",
            "region": "Coastal Tamil Nadu",
            "prep_time": "2 days",
            "description": "Boneless seer fish cubes marinated in fiery Malabar spices and preserved in ginger-garlic sesame gravy.",
            "ingredients": "Fresh Boneless Fish, Ginger, Garlic, Curry Leaves, Green Chilli, Vinegar, Sesame Oil, Spices",
            "image": "fish_pickle.jpg"
        },
        {
            "maker": maker5,
            "name": "Prawn Pickle",
            "category": "Pickles",
            "price": 260.0,
            "stock": 20,
            "product_type": "Packaged Food",
            "city": "Kumbakonam",
            "region": "Coastal Tamil Nadu",
            "prep_time": "2 days",
            "description": "Juicy bay prawns pan-seared with shallots, curry leaves, and spicy red pepper vinegar marinade.",
            "ingredients": "Fresh Prawns, Small Onions, Garlic, Red Chilli Powder, Mustard, Curry Leaves, Pure Oil",
            "image": "prawn_pickle.jpg"
        },

        # Category 5: Beverages
        {
            "maker": maker5,
            "name": "Kumbakonam Degree Coffee Powder",
            "category": "Beverages",
            "price": 190.0,
            "stock": 60,
            "product_type": "Packaged Food",
            "city": "Kumbakonam",
            "region": "Cauvery Delta",
            "prep_time": "1 day",
            "description": "Iconic Kumbakonam 80:20 blend of gourmet plantation Arabica/Robusta coffee and hand-roasted chicory for thick frothy decoction.",
            "ingredients": "80% Pure Arabica & Robusta Coffee Beans, 20% Roasted Chicory",
            "image": "degree_coffee.jpg"
        },
        {
            "maker": maker5,
            "name": "Nilgiri Tea",
            "category": "Beverages",
            "price": 160.0,
            "stock": 45,
            "product_type": "Packaged Food",
            "city": "Kumbakonam",
            "region": "Nilgiri Hills",
            "prep_time": "1 day",
            "description": "Single-origin high-altitude Nilgiri black tea leaves with a floral aroma and bright golden liquor.",
            "ingredients": "100% Orthodox High Altitude Nilgiri Black Tea",
            "image": "nilgiri_tea.jpg"
        },
        {
            "maker": maker5,
            "name": "Herbal Tea",
            "category": "Beverages",
            "price": 140.0,
            "stock": 40,
            "product_type": "Packaged Food",
            "city": "Kumbakonam",
            "region": "Western Ghats",
            "prep_time": "1 day",
            "description": "Ayurvedic immunity tea blend containing holy basil (tulsi), dry ginger, licorice, lemongrass, and black pepper.",
            "ingredients": "Tulsi Leaves, Dry Ginger (Sukku), Licorice, Lemongrass, Black Pepper, Cardamom",
            "image": "herbal_tea.jpg"
        },
        {
            "maker": maker5,
            "name": "Palm Jaggery Drink Mix",
            "category": "Beverages",
            "price": 130.0,
            "stock": 50,
            "product_type": "Packaged Food",
            "city": "Kumbakonam",
            "region": "Tirunelveli Palm Groves",
            "prep_time": "1 day",
            "description": "Traditional Panakarkandu & Sukku Kaapi powder with unrefined palm jaggery, dry ginger, and coriander seeds.",
            "ingredients": "Pure Palm Jaggery (Karupatti), Dry Ginger, Coriander Seeds, Long Pepper, Cardamom",
            "image": "palm_jaggery_drink.jpg"
        },

        # Category 6: Homemade Food Products
        {
            "maker": maker1,
            "name": "Homemade Spice Mixes",
            "category": "Homemade Food Products",
            "price": 145.0,
            "stock": 30,
            "product_type": "Packaged Food",
            "city": "Chennai",
            "region": "Tamil Nadu",
            "prep_time": "1 day",
            "description": "Hand-pounded multi-purpose spice mix for vegetable stir-fries, poriyal, and egg roasts.",
            "ingredients": "Coriander, Cumin, Pepper, Fennel, Garlic, Curry Leaves, Red Chilli",
            "image": "spice_mixes.jpg"
        },
        {
            "maker": maker1,
            "name": "Traditional Rice Mixes",
            "category": "Homemade Food Products",
            "price": 130.0,
            "stock": 40,
            "product_type": "Packaged Food",
            "city": "Chennai",
            "region": "South India",
            "prep_time": "1 day",
            "description": "Ready-to-mix spicy tamarind paste (Puliyodharai thokku) and coriander rice paste made in sesame oil.",
            "ingredients": "Tamarind Pulp, Jaggery, Peanuts, Mustard, Red Chilli, Curry Leaves, Sesame Oil",
            "image": "rice_mixes.jpg"
        },
        {
            "maker": maker1,
            "name": "Millet Mixes",
            "category": "Homemade Food Products",
            "price": 150.0,
            "stock": 35,
            "product_type": "Packaged Food",
            "city": "Chennai",
            "region": "Tamil Nadu",
            "prep_time": "1 day",
            "description": "Nutrient-dense multi-millet health mix containing ragi, kodo millet, foxtail millet, and roasted nuts.",
            "ingredients": "Finger Millet (Ragi), Kodo Millet, Foxtail Millet, Almonds, Cashews, Cardamom, Dry Ginger",
            "image": "millet_mixes.jpg"
        },
        {
            "maker": maker1,
            "name": "Dry Chutney Powders",
            "category": "Homemade Food Products",
            "price": 110.0,
            "stock": 50,
            "product_type": "Packaged Food",
            "city": "Chennai",
            "region": "South India",
            "prep_time": "1 day",
            "description": "Spicy garlic and roasted gram dry chutney podi, delicious when sprinkled on hot rice with ghee.",
            "ingredients": "Fried Gram, Garlic, Dry Coconut, Red Chilli, Salt, Cumin",
            "image": "dry_chutney_powders.jpg"
        },
        {
            "maker": maker1,
            "name": "Homemade Sauces",
            "category": "Homemade Food Products",
            "price": 125.0,
            "stock": 25,
            "product_type": "Packaged Food",
            "city": "Chennai",
            "region": "South India",
            "prep_time": "1 day",
            "description": "Authentic regional spicy mint-coriander and sweet tamarind-date cooking sauces made without artificial preservatives.",
            "ingredients": "Fresh Mint, Coriander, Tamarind, Dates, Green Chilli, Cumin, Black Salt",
            "image": "homemade_sauces.jpg"
        },

        # Category 7: Fresh Regional Foods
        {
            "maker": maker1,
            "name": "Madurai Kari Dosa",
            "category": "Fresh Regional Foods",
            "price": 210.0,
            "stock": 20,
            "product_type": "Fresh Food",
            "city": "Madurai",
            "region": "Madurai",
            "prep_time": "30 mins",
            "description": "Iconic three-tier Madurai street delicacy: thick sponge dosa layered with fluffy egg omelette and spicy minced mutton salna.",
            "ingredients": "Fermented Dosa Batter, Country Eggs, Minced Meat/Mutton Gravy, Shallots, Green Chillies, Pepper",
            "image": "kari_dosa.jpg"
        },
        {
            "maker": maker1,
            "name": "Chettinad Chicken Curry",
            "category": "Fresh Regional Foods",
            "price": 280.0,
            "stock": 15,
            "product_type": "Fresh Food",
            "city": "Chennai",
            "region": "Chettinad",
            "prep_time": "45 mins",
            "description": "Fiery and intensely aromatic chicken curry simmered with fresh ground coconut, kalpasi, star anise, and whole shallots.",
            "ingredients": "Tender Country Chicken, Shallots, Tomato, Fresh Coconut Paste, Chettinad Spices, Curry Leaves",
            "image": "chettinad_chicken.jpg"
        },
        {
            "maker": maker3,
            "name": "Ambur Biryani",
            "category": "Fresh Regional Foods",
            "price": 260.0,
            "stock": 25,
            "product_type": "Fresh Food",
            "city": "Dindigul",
            "region": "Arcot / Ambur",
            "prep_time": "45 mins",
            "description": "Traditional Seeraga Samba dum biryani prepared with tender meat, curd, tomato, and ground red chilli paste. Served with brinjal gravy (dalcha).",
            "ingredients": "Seeraga Samba Rice, Tender Meat, Red Chilli Paste, Curd, Mint, Coriander, Ghee, Brinjal Gravy",
            "image": "ambur_biryani.jpg"
        },
        {
            "maker": maker3,
            "name": "Hyderabadi Biryani",
            "category": "Fresh Regional Foods",
            "price": 290.0,
            "stock": 20,
            "product_type": "Fresh Food",
            "city": "Chennai",
            "region": "Hyderabad / Deccan",
            "prep_time": "50 mins",
            "description": "Kachchi dum biryani layered with fragrant aged Basmati rice, saffron-infused milk, fried golden onions (birista), and marinated meat.",
            "ingredients": "Aged Long Grain Basmati Rice, Marinated Meat, Saffron, Ghee, Fried Onions, Green Cardamom, Mint",
            "image": "hyderabadi_biryani.jpg"
        },
        {
            "maker": maker1,
            "name": "Kolkata Kathi Roll",
            "category": "Fresh Regional Foods",
            "price": 140.0,
            "stock": 30,
            "product_type": "Fresh Food",
            "city": "Chennai",
            "region": "Kolkata",
            "prep_time": "20 mins",
            "description": "Crispy flaky paratha coated with egg, wrapped around spiced grilled kebab skewers, crunchy onion rings, and tangy green chutney.",
            "ingredients": "Flaky Paratha, Egg, Spiced Kebab Chunks, Sliced Onions, Green Chillies, Lemon Juice, Chaat Masala",
            "image": "kathi_roll.jpg"
        },
        {
            "maker": maker2,
            "name": "Pani Puri",
            "category": "Fresh Regional Foods",
            "price": 80.0,
            "stock": 40,
            "product_type": "Fresh Food",
            "city": "Madurai",
            "region": "North & West India",
            "prep_time": "15 mins",
            "description": "Crispy hollow puris filled with spiced potato-chickpea mash, paired with tangy tamarind water and zesty mint-coriander pani.",
            "ingredients": "Semolina Puris, Spiced Potato Mash, Boiled Chickpeas, Mint Water, Tamarind Saunth, Boondi",
            "image": "pani_puri.jpg"
        },
        {
            "maker": maker2,
            "name": "Misal Pav",
            "category": "Fresh Regional Foods",
            "price": 120.0,
            "stock": 25,
            "product_type": "Fresh Food",
            "city": "Madurai",
            "region": "Maharashtra",
            "prep_time": "25 mins",
            "description": "Spicy sprouted moth bean curry topped with farsan, chopped onions, and lemon, served with butter-toasted soft ladi pavs.",
            "ingredients": "Sprouted Moth Beans, Spicy Kat/Rassa Gravy, Farsan/Chivda, Ladi Pav, Coriander, Lemon",
            "image": "misal_pav.jpg"
        },
        {
            "maker": maker2,
            "name": "Dhokla",
            "category": "Fresh Regional Foods",
            "price": 90.0,
            "stock": 35,
            "product_type": "Fresh Food",
            "city": "Madurai",
            "region": "Gujarat",
            "prep_time": "20 mins",
            "description": "Spongy, savory steamed gram flour cakes tempered with mustard seeds, green chillies, curry leaves, and fresh grated coconut.",
            "ingredients": "Gram Flour (Besan), Lemon, Green Chillies, Mustard Tempering, Fresh Grated Coconut, Coriander",
            "image": "dhokla.jpg"
        },
        {
            "maker": maker1,
            "name": "Litti Chokha",
            "category": "Fresh Regional Foods",
            "price": 160.0,
            "stock": 20,
            "product_type": "Fresh Food",
            "city": "Chennai",
            "region": "Bihar",
            "prep_time": "30 mins",
            "description": "Traditional roasted whole wheat dough balls stuffed with spiced sattu (roasted gram flour), served with smoky roasted eggplant and tomato mash (chokha) and desi ghee.",
            "ingredients": "Whole Wheat Flour, Roasted Gram Sattu, Ajwain, Mustard Oil, Roasted Baingan, Tomatoes, Desi Ghee",
            "image": "litti_chokha.jpg"
        },
        {
            "maker": maker1,
            "name": "Appam with Stew",
            "category": "Fresh Regional Foods",
            "price": 175.0,
            "stock": 25,
            "product_type": "Fresh Food",
            "city": "Chennai",
            "region": "Kerala",
            "prep_time": "25 mins",
            "description": "Lacy, soft-centered fermented rice hopper pancakes served with fragrant mild coconut milk vegetable or chicken stew.",
            "ingredients": "Fermented Rice & Coconut Batter, Coconut Milk, Carrots, Potatoes, Green Chillies, Curry Leaves, Whole Spices",
            "image": "appam_stew.jpg"
        }
    ]

    saved_products = []
    for p_data in products_data:
        # Determine authentic package weight/quantity based on category and item
        cat = p_data["category"]
        name = p_data["name"]
        
        if "Halwa" in name:
            net_qty = "500g"
        elif "Biryani Masala" in name or "Pepper Powder" in name or "Herbal Tea" in name or "Chutney" in name:
            net_qty = "150g"
        elif "Masala" in name or "Rasam" in name or "Thattai" in name or "Seedai" in name or "Jackfruit" in name:
            net_qty = "200g"
        elif "Pickle" in name or "Kadalai Mittai" in name:
            net_qty = "300g"
        elif "Millet" in name:
            net_qty = "500g"
        elif cat == "Fresh Regional Foods":
            if "Dosa" in name or "Roll" in name:
                net_qty = "2 Pcs / 1 Plate"
            elif "Curry" in name:
                net_qty = "500 ml Bowl"
            elif "Biryani" in name:
                net_qty = "Serves 1-2 (450g)"
            elif "Puri" in name:
                net_qty = "10 Puris Set"
            elif "Dhokla" in name:
                net_qty = "250g (4 Pcs)"
            else:
                net_qty = "1 Set (Serves 1)"
        else:
            net_qty = p_data.get("net_quantity", "250g")

        prod = Product(
            food_maker_id=p_data["maker"].id,
            name=p_data["name"],
            category=p_data["category"],
            price=p_data["price"],
            stock=p_data["stock"],
            product_type=p_data["product_type"],
            city=p_data["city"],
            region=p_data["region"],
            preparation_time=p_data["prep_time"],
            net_quantity=net_qty,
            description=p_data["description"],
            ingredients=p_data["ingredients"],
            image=p_data["image"],
            created_at=datetime.utcnow() - timedelta(days=15)
        )
        db.session.add(prod)
        saved_products.append(prod)
        
    db.session.flush()

    # -------------------------------------------------------------
    # 4. SEED SAMPLE REVIEWS & RATINGS
    # -------------------------------------------------------------
    sample_reviews = [
        Review(customer_id=customer1.id, product_id=saved_products[0].id, food_maker_id=maker3.id, rating=5, comment="Incredible authentic aroma! Made Sunday chicken curry taste just like my grandmother's cooking in Dindigul.", created_at=datetime.utcnow() - timedelta(days=10)),
        Review(customer_id=customer2.id, product_id=saved_products[8].id, food_maker_id=maker2.id, rating=5, comment="Crispy, fresh, and not oily at all. You can taste the genuine wood-pressed oil.", created_at=datetime.utcnow() - timedelta(days=8)),
        Review(customer_id=customer1.id, product_id=saved_products[15].id, food_maker_id=maker4.id, rating=5, comment="Mouth-watering Tirunelveli Halwa! Arrived warm and fresh in perfect packaging. 10/10 recommend.", created_at=datetime.utcnow() - timedelta(days=6)),
        Review(customer_id=customer2.id, product_id=saved_products[22].id, food_maker_id=maker5.id, rating=5, comment="The degree coffee powder produces such thick and fragrant decoction. Truly brings the Kumbakonam taste home!", created_at=datetime.utcnow() - timedelta(days=5)),
        Review(customer_id=customer1.id, product_id=saved_products[31].id, food_maker_id=maker1.id, rating=5, comment="Madurai Kari Dosa was outstanding! Spicy, meaty, and delivered piping hot.", created_at=datetime.utcnow() - timedelta(days=3)),
    ]
    db.session.add_all(sample_reviews)

    # -------------------------------------------------------------
    # 5. SEED INITIAL INTERACTIONS (FOR AI ENGINE BASELINE)
    # -------------------------------------------------------------
    interactions = [
        Interaction(customer_id=customer1.id, product_id=saved_products[0].id, interaction_type="PURCHASE"),
        Interaction(customer_id=customer1.id, product_id=saved_products[4].id, interaction_type="CART"),
        Interaction(customer_id=customer1.id, product_id=saved_products[6].id, interaction_type="VIEW"),
        Interaction(customer_id=customer1.id, product_id=saved_products[15].id, interaction_type="PURCHASE"),
        Interaction(customer_id=customer1.id, product_id=saved_products[31].id, interaction_type="PURCHASE"),
        Interaction(customer_id=customer2.id, product_id=saved_products[8].id, interaction_type="PURCHASE"),
        Interaction(customer_id=customer2.id, product_id=saved_products[9].id, interaction_type="CART"),
        Interaction(customer_id=customer2.id, product_id=saved_products[22].id, interaction_type="PURCHASE"),
    ]
    db.session.add_all(interactions)

    # -------------------------------------------------------------
    # 6. SEED SAMPLE ORDER FOR DEMO TRACKING
    # -------------------------------------------------------------
    sample_order = Order(
        customer_id=customer1.id,
        total_amount=570.0,
        address="Flat 402, Royal Palms, Anna Nagar",
        city="Chennai",
        state="Tamil Nadu",
        pincode="600040",
        phone="9876543210",
        payment_method="Cash on Delivery",
        status="Preparing",
        created_at=datetime.utcnow() - timedelta(hours=3)
    )
    db.session.add(sample_order)
    db.session.flush()

    order_items = [
        OrderItem(order_id=sample_order.id, product_id=saved_products[31].id, food_maker_id=maker1.id, quantity=2, price=210.0),
        OrderItem(order_id=sample_order.id, product_id=saved_products[6].id, food_maker_id=maker3.id, quantity=1, price=150.0)
    ]
    db.session.add_all(order_items)

    # -------------------------------------------------------------
    # 7. SEED TODAY'S DAILY INGREDIENTS & DISH VERIFICATION LOGS
    # -------------------------------------------------------------
    today_str = datetime.utcnow().strftime('%Y-%m-%d')
    yesterday_str = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')

    daily_logs = [
        DailyVerification(
            food_maker_id=maker1.id,
            log_date=today_str,
            ingredients_used="Country eggs, tender minced mutton, stone-ground Chettinad kalpasi masala, wood-pressed sesame oil, fresh shallots & curry leaves",
            dishes_prepared="Madurai Kari Dosa, Chettinad Chicken Curry",
            dish_image="kari_dosa.jpg",
            sourcing_notes="Sesame oil pressed at local Chettinad mill, farm-fresh eggs sourced daily",
            created_at=datetime.utcnow() - timedelta(hours=2)
        ),
        DailyVerification(
            food_maker_id=maker1.id,
            log_date=yesterday_str,
            ingredients_used="Seeraga Samba rice, whole spices, desi ghee, fresh mint, coriander, tender country meat",
            dishes_prepared="Ambur Biryani, Kari Dosa",
            dish_image="kari_dosa.jpg",
            sourcing_notes="Traditional wood fire cooking batch",
            created_at=datetime.utcnow() - timedelta(days=1, hours=4)
        ),
        DailyVerification(
            food_maker_id=maker2.id,
            log_date=today_str,
            ingredients_used="Freshly stone-milled raw rice flour, urad dal, carom seeds (ajwain), white sesame seeds, pure butter, cold-pressed groundnut oil",
            dishes_prepared="Hand-twisted Kai Murukku, Spicy Mixture, Thattai",
            dish_image="kai_murukku.jpg",
            sourcing_notes="Zero preservatives, 100% cold-pressed groundnut oil",
            created_at=datetime.utcnow() - timedelta(hours=3)
        ),
        DailyVerification(
            food_maker_id=maker4.id,
            log_date=today_str,
            ingredients_used="Freshly extracted whole samba wheat milk, pure country cow ghee, organic palm jaggery, cardamom pods",
            dishes_prepared="Tirunelveli Wheat Halwa",
            dish_image="tirunelveli_halwa.jpg",
            sourcing_notes="Simmered for 3.5 hours using Thamirabarani mineral water",
            created_at=datetime.utcnow() - timedelta(hours=4)
        )
    ]
    db.session.add_all(daily_logs)

    db.session.commit()
    print("[SUCCESS] Successfully seeded demo users, food makers, daily verification logs, 35+ products, reviews, and sample orders!")

if __name__ == '__main__':
    from backend.app import create_app
    app = create_app()
    with app.app_context():
        seed_database()
