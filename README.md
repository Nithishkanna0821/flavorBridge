# FlavorBridge — Regional Food Marketplace MVP

> **Discover the Taste of Every Region**  
> An authentic regional food marketplace connecting traditional culinary makers, home chefs, and spice artisans directly with customers across India.

---

## 📌 Project Overview

- **Objective**: Preserve and celebrate India's hyper-local culinary heritage by providing an accessible, AI-augmented marketplace platform where traditional food makers can showcase their handcrafted recipes and customers can discover verified regional delicacies.
- **The Problem**: Traditional, generational food makers (such as halwa artisans in Tirunelveli, spice blenders in Dindigul, and home cooks in Madurai) lack digital visibility, while regional food lovers cannot easily source verified, authentic local specialties.
- **The Solution**: **FlavorBridge** provides a direct marketplace with internal quality verification scoring, Cash on Delivery (COD) order management, and built-in Python machine learning tools for smart culinary discovery.

---

## 🛠️ Mandatory Tech Stack & Architecture

- **Frontend**: HTML5, CSS3 (Modern custom design system), Vanilla JavaScript (No React/Angular/Vue).
- **Backend**: Python 3.13+ with Flask, Flask-SQLAlchemy, and Werkzeug password hashing.
- **Database**: SQLite (local single-file database in `database/database.db`).
- **AI / Machine Learning**: Scikit-Learn (TF-IDF Vectorization + Cosine Similarity), Pandas, NumPy. *100% local, no paid APIs or external dependencies.*
- **Roles**: Two distinct roles — **Customer** and **Food Maker** (no admin panel).

### Three-Folder Project Layout

```
flavorbridge/
├── frontend/
│   ├── templates/          # All 25 Jinja2 HTML templates
│   └── static/
│       ├── css/style.css   # Custom CSS3 warm culinary design system
│       ├── js/             # Vanilla JS: cart, search, filters, validation, AI assistant
│       └── images/         # Static visual assets
│
├── backend/
│   ├── app.py              # Flask app factory & blueprint registration
│   ├── models.py           # 9 SQLAlchemy database models
│   ├── extensions.py       # Shared db instance
│   ├── routes/             # Auth, Product, Cart, Order, Maker, Review, AI blueprints
│   ├── ai/                 # Recommender, Smart Search, Recipe Matcher, Food Assistant
│   ├── utils/              # Password hashing, decorators, upload validators
│   ├── seed_data.py        # 5 verified makers, demo customers, 35+ authentic products
│   ├── requirements.txt    # Python dependencies
│   └── uploads/            # Uploaded product and profile images
│
├── database/
│   ├── database.db         # Generated SQLite database
│   ├── schema.sql          # Reference SQL schema matching models.py
│   └── init_db.py          # Database initializer and seeder
│
├── README.md
└── .gitignore
```

---

## 🌟 Key Features

### 1. User Roles & Authentication
- **Customer**: Register, login, browse catalog, dynamic filtering, live cart, Cash on Delivery checkout, visual order tracking timeline, product reviews, and personalized AI recommendations.
- **Food Maker**: Register with kitchen details, build profile, add/edit/delete products with image upload, manage stock, view incoming orders, update live order status (Packaged vs Fresh flow), apply for Quality Verification.

### 2. Authentic Regional Categories
- **Spice Powders & Seasonings**: Chicken Masala Powder, Mutton Masala Powder, Sambar Powder, Rasam Powder, Biryani Masala, Curry Masala, Pepper Powder, Idli Podi.
- **Traditional Snacks**: Murukku, Kai Murukku, Thattai, Seedai, Mixture, Banana Chips, Jackfruit Chips.
- **Traditional Sweets**: Tirunelveli Halwa, Mysore Pak, Kovilpatti Kadalai Mittai, Adhirasam, Jangiri, Laddu, Palkova.
- **Pickles**: Mango, Lemon, Garlic, Gooseberry, Fish, Prawn.
- **Beverages**: Kumbakonam Degree Coffee Powder, Nilgiri Tea, Herbal Tea, Palm Jaggery Drink Mix.
- **Homemade Food Products**: Homemade Spice Mixes, Traditional Rice Mixes, Millet Mixes, Dry Chutney Powders, Homemade Sauces.
- **Fresh Regional Foods**: Madurai Kari Dosa, Chettinad Chicken Curry, Ambur Biryani, Hyderabadi Biryani, Kolkata Kathi Roll, Pani Puri, Misal Pav, Dhokla, Litti Chokha, Appam with Stew.

### 3. Quality Verification System
- **Scoring (Out of 100)**:
  - Profile completed (Name, Address, City, Phone): `+20`
  - Speciality defined: `+20`
  - Experience provided: `+20`
  - Food / Profile images provided: `+20`
  - Food details / Story provided: `+20`
- **Threshold**: Score $\ge 80 \rightarrow$ **"✓ Verified Food Maker"** badge.
- *Notice: Clearly labeled as an internal platform authenticity rating.*

### 4. Order Status Flow
- **Packaged Food**: `Pending` $\rightarrow$ `Accepted` $\rightarrow$ `Preparing` $\rightarrow$ `Shipped` $\rightarrow$ `Delivered`
- **Fresh Food (Hot Meals)**: `Pending` $\rightarrow$ `Accepted` $\rightarrow$ `Preparing` $\rightarrow$ `Out for Delivery` $\rightarrow$ `Delivered`

---

## 🤖 4 Built-In Local AI Features (No External APIs)

1. **Personalized Hybrid Recommender** (`backend/ai/recommender.py`):
   - Computes TF-IDF similarity vectors across product tags, ingredients, and categories.
   - Weighted interaction scores: `VIEW` (1x), `LIKE` (2x), `CART` (3x), `PURCHASE` (5x).
   - Cold-start handling for new users with trending and local city delicacies.
2. **Smart TF-IDF Search** (`backend/ai/smart_search.py`):
   - Scikit-learn `TfidfVectorizer` + `cosine_similarity` across multi-field corpus.
   - Handles natural language queries like *"spicy Tamil food"* or *"healthy millet snacks"*.
3. **Local Recipe Partner Matcher** (`backend/ai/recipe_partner_matcher.py`):
   - Ranks food makers based on locality proximity (30%), speciality match (35%), verification status (20%), and ratings (15%).
4. **Regional Food Assistant** (`backend/ai/food_assistant.py`):
   - Rule-based NLP assistant parsing regions, taste attributes (spicy, sweet, tangy, crispy), and budget caps (e.g. *"I want spicy food from Tamil Nadu under ₹300"*).
   - Conversational responses with direct product cards. *Never automatically places an order.*

---

## 🔑 Demo Account Credentials

| Role | Name | Email | Password | Details |
| :--- | :--- | :--- | :--- | :--- |
| **Customer** | Ananya Sharma | `ananya@example.com` | `password123` | Chennai, active order history |
| **Customer** | Rajesh Kumar | `rajesh@example.com` | `password123` | Madurai, traditional snack lover |
| **Food Maker** | Priya Sundaram | `priya@example.com` | `password123` | Chennai, Madurai & Chettinad Cuisine (Score 100) |
| **Food Maker** | Kumaravel M | `kumar@example.com` | `password123` | Madurai, Traditional Snacks (Score 100) |
| **Food Maker** | Lakshmi Narayanan | `lakshmi@example.com` | `password123` | Dindigul, Biryani Spices & Masala (Score 95) |
| **Food Maker** | Arunachalam S | `arun@example.com` | `password123` | Tirunelveli, Traditional Sweets (Score 100) |
| **Food Maker** | Meenakshi R | `meena@example.com` | `password123` | Kumbakonam, Degree Coffee & Pickles (Score 90) |

---

## 🚀 Quick Start & Exact Terminal Commands

### Step 1: Clone / Navigate to Project Root
```bash
cd flavorbridge
```

### Step 2: (Optional) Create & Activate Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### Step 4: Initialize Database & Seed Demo Data
```bash
python database/init_db.py
```

### Step 5: Run the FlavorBridge Web Application (Local & LAN Network)
```bash
python backend/app.py
```
When started, the server binds to `0.0.0.0:5000` and displays both local and network URLs:
- **On this computer**: [`http://127.0.0.1:5000`](http://127.0.0.1:5000) or [`http://localhost:5000`](http://localhost:5000)
- **On other devices (Phones, Tablets, Laptops on same Wi-Fi)**: `http://<YOUR_IP>:5000` (e.g. `http://10.132.160.116:5000`)

> **Note for Windows Firewall**: If other devices on your Wi-Fi cannot connect initially, allow Python through the Windows Firewall prompt or verify both devices are on the same Wi-Fi network.

---

## 🧪 Comprehensive Feature Testing Guide

1. **Customer Flow**:
   - Log in with `ananya@example.com` / `password123`.
   - Go to **Explore Foods** (`/products`). Test category filters, city selector, and price range.
   - Use the **Smart Search** (`/smart-search`) for *"spicy Tamil food"*.
   - Open **Food Assistant** (`/food-assistant`) and ask *"Spicy food under 300"*.
   - Add items to cart, proceed to **Checkout** (`/checkout`), and place order with **Cash on Delivery**.
   - View live timeline tracker on **Order Details** (`/order/<id>`).
2. **Food Maker Flow**:
   - Log in with `priya@example.com` / `password123`.
   - Open **Maker Dashboard** (`/food-maker/dashboard`) to view revenue, active orders, and verification progress.
   - Update order status (e.g. from `Pending` $\rightarrow$ `Accepted` $\rightarrow$ `Preparing` $\rightarrow$ `Out for Delivery` $\rightarrow$ `Delivered`).
   - Add a new product via **Add New Product** (`/add-product`).
   - Check **Verification System** (`/verification`) and see the 100-point scoring checklist.

---

## 🔮 Future Enhancements
- Integration of regional multi-language localization (Tamil, Telugu, Hindi, Kannada, Malayalam).
- Hyper-local GPS courier routing and live delivery driver integration.
- Offline SMS order alerts for rural village home chefs.
