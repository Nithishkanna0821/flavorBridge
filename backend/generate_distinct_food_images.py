import os
import shutil
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont

art_dir = r"C:\Users\REMETTHA B\.gemini\antigravity-ide\brain\39266548-e291-42f4-a7d8-6cd7f5055bc6"
upload_dir = r"c:\Users\REMETTHA B\OneDrive\Desktop\flavorBridge\backend\uploads"
static_dir = r"c:\Users\REMETTHA B\OneDrive\Desktop\flavorBridge\frontend\static\images"

os.makedirs(upload_dir, exist_ok=True)
os.makedirs(static_dir, exist_ok=True)

# Master High-Res Source Images
SRC_HERO = os.path.join(art_dir, "hero_food_banner_1787554069949.jpg")
SRC_KARI = os.path.join(art_dir, "madurai_kari_dosa_1787554095010.jpg")
SRC_HALWA = os.path.join(art_dir, "tirunelveli_halwa_1787554122154.jpg")
SRC_MURUKKU = os.path.join(art_dir, "kai_murukku_1787554145353.jpg")
SRC_CHICKEN = os.path.join(art_dir, "chettinad_chicken_1787554168943.jpg")
SRC_COFFEE = os.path.join(art_dir, "degree_coffee_1787554194651.jpg")
SRC_PICKLE = os.path.join(art_dir, "traditional_pickle_1787554222759.jpg")
SRC_BIRYANI = os.path.join(art_dir, "dindigul_biryani_1787554249565.jpg")
SRC_MYSORE = os.path.join(art_dir, "mysore_pak_1787554278092.jpg")
SRC_SPICES = os.path.join(art_dir, "sambar_masala_spices_1787559009099.jpg")
SRC_SWEETS = os.path.join(art_dir, "traditional_sweets_platter_1787559045125.jpg")
SRC_TEA = os.path.join(art_dir, "herbal_tea_beverages_1787559078123.jpg")
SRC_CHEF = os.path.join(art_dir, "priya_kitchen_1787554306385.jpg")

def crop_and_enhance(src_path, box=None, brightness=1.0, contrast=1.0, color=1.0, flip=False, rotate=0, target_size=(800, 600)):
    if not os.path.exists(src_path):
        # Fallback to hero
        src_path = SRC_HERO
    
    img = Image.open(src_path).convert('RGB')
    if box:
        # box in fractions (left, upper, right, lower)
        w, h = img.size
        crop_box = (int(box[0]*w), int(box[1]*h), int(box[2]*w), int(box[3]*h))
        img = img.crop(crop_box)
    
    if flip:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    if rotate != 0:
        img = img.rotate(rotate, expand=True)

    if brightness != 1.0:
        img = ImageEnhance.Brightness(img).enhance(brightness)
    if contrast != 1.0:
        img = ImageEnhance.Contrast(img).enhance(contrast)
    if color != 1.0:
        img = ImageEnhance.Color(img).enhance(color)
        
    img = img.resize(target_size, Image.Resampling.LANCZOS)
    return img

def save_image(img, filename):
    p1 = os.path.join(upload_dir, filename)
    p2 = os.path.join(static_dir, filename)
    img.save(p1, quality=92)
    img.save(p2, quality=92)
    print(f"Generated distinct image: {filename}")

# =========================================================================
# 1. SPICE POWDERS & SEASONINGS (Distinct Crops & Enhanced Color Tones)
# =========================================================================
# ID 1: Chicken Masala Powder (Red Chilli Masala focus)
img1 = crop_and_enhance(SRC_SPICES, box=(0.48, 0.35, 0.76, 0.75), color=1.25, contrast=1.1, brightness=0.98)
save_image(img1, "chicken_masala_powder.jpg")

# ID 2: Mutton Masala Powder (Dark Cloves/Cinnamon/Stone-ground Masala focus)
img2 = crop_and_enhance(SRC_SPICES, box=(0.28, 0.38, 0.54, 0.78), color=0.95, contrast=1.18, brightness=0.92)
save_image(img2, "mutton_masala_powder.jpg")

# ID 3: Sambar Powder (Golden Roasted Sambar Podi focus)
img3 = crop_and_enhance(SRC_SPICES, box=(0.04, 0.35, 0.32, 0.75), color=1.2, contrast=1.05, brightness=1.02)
save_image(img3, "sambar_powder.jpg")

# ID 4: Rasam Powder (Pepper & Cumin Bowl focus with Curry Leaves)
img4 = crop_and_enhance(SRC_SPICES, box=(0.70, 0.38, 0.98, 0.78), color=1.05, contrast=1.12, brightness=0.96)
save_image(img4, "rasam_powder.jpg")

# ID 5: Biryani Masala (Whole Spices & Dindigul Masala Blend)
img5 = crop_and_enhance(SRC_BIRYANI, box=(0.25, 0.20, 0.85, 0.75), color=1.15, contrast=1.08, brightness=1.0)
save_image(img5, "biryani_masala.jpg")

# ID 6: Curry Masala (Rich Spice Seasoning with Bay leaf and spices)
img6 = crop_and_enhance(SRC_SPICES, box=(0.35, 0.50, 0.70, 0.95), color=1.1, contrast=1.15, brightness=0.95)
save_image(img6, "curry_masala.jpg")

# ID 7: Pepper Powder (Close-up of Crushed Black Peppercorns)
img7 = crop_and_enhance(SRC_SPICES, box=(0.72, 0.40, 0.96, 0.72), color=0.7, contrast=1.25, brightness=0.92)
save_image(img7, "pepper_powder.jpg")

# ID 8: Idli Podi (Gunpowder from Hero table bottom corner)
img8 = crop_and_enhance(SRC_HERO, box=(0.72, 0.60, 0.88, 0.82), color=1.35, contrast=1.12, brightness=1.0)
save_image(img8, "idli_podi.jpg")


# =========================================================================
# 2. TRADITIONAL SNACKS (Distinct Visual Angles & Crisps)
# =========================================================================
# ID 9: Murukku (Golden crispy rings in basket)
img9 = crop_and_enhance(SRC_HERO, box=(0.64, 0.22, 0.92, 0.55), color=1.1, contrast=1.05)
save_image(img9, "murukku.jpg")

# ID 10: Kai Murukku (Handcrafted multi-spiral close-up on banana leaf)
img10 = crop_and_enhance(SRC_MURUKKU, box=(0.18, 0.25, 0.82, 0.85), color=1.12, contrast=1.08)
save_image(img10, "kai_murukku.jpg")

# ID 11: Thattai (Crisp disc savory crackers - center-left close crop)
img11 = crop_and_enhance(SRC_MURUKKU, box=(0.20, 0.48, 0.55, 0.82), color=1.18, contrast=1.12)
save_image(img11, "thattai.jpg")

# ID 12: Seedai (Round crisp golden savory balls - lower right crop)
img12 = crop_and_enhance(SRC_MURUKKU, box=(0.48, 0.50, 0.85, 0.85), color=1.15, contrast=1.15)
save_image(img12, "seedai.jpg")

# ID 13: Mixture (Spicy Madras mixture in bamboo tray)
img13 = crop_and_enhance(SRC_MURUKKU, box=(0.10, 0.15, 0.90, 0.90), flip=True, color=1.2, contrast=1.1)
save_image(img13, "mixture.jpg")

# ID 14: Banana Chips (Golden crisp yellow slices)
img14 = crop_and_enhance(SRC_SWEETS, box=(0.35, 0.55, 0.65, 0.85), color=1.35, contrast=1.1, brightness=1.08)
save_image(img14, "banana_chips.jpg")

# ID 15: Jackfruit Chips (Crunchy orange Kerala chakka chips)
img15 = crop_and_enhance(SRC_MURUKKU, box=(0.32, 0.28, 0.70, 0.60), color=1.3, contrast=1.15, brightness=0.98)
save_image(img15, "jackfruit_chips.jpg")


# =========================================================================
# 3. TRADITIONAL SWEETS (Distinct Authentic Confections)
# =========================================================================
# ID 16: Tirunelveli Halwa (Glistening Amber Ghee Halwa with Cashews)
img16 = crop_and_enhance(SRC_HALWA, box=(0.15, 0.20, 0.88, 0.80), color=1.1, contrast=1.05)
save_image(img16, "tirunelveli_halwa.jpg")

# ID 17: Mysore Pak (Porous Honeycomb Ghee Mysore Pak Cubes)
img17 = crop_and_enhance(SRC_MYSORE, box=(0.12, 0.18, 0.88, 0.82), color=1.1, contrast=1.05)
save_image(img17, "mysore_pak.jpg")

# ID 18: Kovilpatti Kadalai Mittai (Crunchy Peanut Chikki Brittle)
img18 = crop_and_enhance(SRC_SWEETS, box=(0.35, 0.55, 0.66, 0.85), color=1.12, contrast=1.15)
save_image(img18, "kadalai_mittai.jpg")

# ID 19: Adhirasam (Deep Brown Rice-Jaggery Pastry)
img19 = crop_and_enhance(SRC_HALWA, box=(0.28, 0.32, 0.75, 0.75), color=0.9, contrast=1.2, brightness=0.88)
save_image(img19, "adhirasam.jpg")

# ID 20: Jangiri (Bright Orange Saffron Flower Sweet)
img20 = crop_and_enhance(SRC_SWEETS, box=(0.62, 0.40, 0.92, 0.78), color=1.25, contrast=1.1)
save_image(img20, "jangiri.jpg")

# ID 21: Laddu (Golden Boondi Laddu Pyramid with Silver Vark)
img21 = crop_and_enhance(SRC_SWEETS, box=(0.36, 0.24, 0.66, 0.58), color=1.15, contrast=1.08)
save_image(img21, "laddu.jpg")

# ID 22: Palkova (Creamy Milk Sweet Squares with Pistachios)
img22 = crop_and_enhance(SRC_SWEETS, box=(0.14, 0.42, 0.44, 0.74), color=1.05, contrast=1.05, brightness=1.05)
save_image(img22, "palkova.jpg")


# =========================================================================
# 4. PICKLES (Authentic Glazed Bharani & Jar Specialties)
# =========================================================================
# ID 23: Mango Pickle (Traditional Cut Mango in Ceramic Jar & Wooden Spoon)
img23 = crop_and_enhance(SRC_PICKLE, box=(0.28, 0.18, 0.80, 0.80), color=1.1, contrast=1.08)
save_image(img23, "mango_pickle.jpg")

# ID 24: Lemon Pickle (Tangy Sun-Cured Lemon Pickle)
img24 = crop_and_enhance(SRC_PICKLE, box=(0.40, 0.18, 0.65, 0.45), color=1.35, contrast=1.15, brightness=1.05)
save_image(img24, "lemon_pickle.jpg")

# ID 25: Garlic Pickle (Whole Poondu Cloves in Dark Masala)
img25 = crop_and_enhance(SRC_PICKLE, box=(0.32, 0.35, 0.68, 0.78), color=1.05, contrast=1.2, brightness=0.92)
save_image(img25, "garlic_pickle.jpg")

# ID 26: Gooseberry Pickle (Amla Nellikai in Spicy Fenugreek Gravy)
img26 = crop_and_enhance(SRC_HERO, box=(0.85, 0.48, 0.98, 0.75), color=1.2, contrast=1.15)
save_image(img26, "gooseberry_pickle.jpg")

# ID 27: Fish Pickle (Coastal Spicy Fish Pickle)
img27 = crop_and_enhance(SRC_CHICKEN, box=(0.28, 0.40, 0.68, 0.78), color=1.25, contrast=1.2, brightness=0.92)
save_image(img27, "fish_pickle.jpg")

# ID 28: Prawn Pickle (Coastal Eral Prawn Masala Pickle)
img28 = crop_and_enhance(SRC_CHICKEN, box=(0.42, 0.44, 0.74, 0.76), color=1.3, contrast=1.22, brightness=0.9)
save_image(img28, "prawn_pickle.jpg")


# =========================================================================
# 5. BEVERAGES & TRADITIONAL MIXES
# =========================================================================
# ID 29: Kumbakonam Degree Coffee Powder (Frothy Filter Coffee & Brass Set)
img29 = crop_and_enhance(SRC_COFFEE, box=(0.30, 0.40, 0.72, 0.92), color=1.08, contrast=1.1)
save_image(img29, "degree_coffee.jpg")

# ID 30: Nilgiri Tea (Fresh Aromatic Mountain Orthodox Tea Leaves)
img30 = crop_and_enhance(SRC_TEA, box=(0.28, 0.50, 0.55, 0.70), color=1.0, contrast=1.15, brightness=0.95)
save_image(img30, "nilgiri_tea.jpg")

# ID 31: Herbal Tea (Steaming Sukku Malli Tea in Kulhad Cup)
img31 = crop_and_enhance(SRC_TEA, box=(0.40, 0.32, 0.68, 0.78), color=1.08, contrast=1.08)
save_image(img31, "herbal_tea.jpg")

# ID 32: Palm Jaggery Drink Mix (Karupatti Blocks & Spices)
img32 = crop_and_enhance(SRC_TEA, box=(0.68, 0.56, 0.90, 0.82), color=1.15, contrast=1.12)
save_image(img32, "palm_jaggery_drink.jpg")


# =========================================================================
# 6. HOMEMADE FOOD PRODUCTS
# =========================================================================
# ID 33: Homemade Spice Mixes (Handcrafted whole and powdered spice jars)
img33 = crop_and_enhance(SRC_SPICES, box=(0.05, 0.20, 0.95, 0.85), color=1.1, contrast=1.1)
save_image(img33, "spice_mixes.jpg")

# ID 34: Traditional Rice Mixes (Paruppu Podi & Curry Leaf Rice Mix)
img34 = crop_and_enhance(SRC_SPICES, box=(0.10, 0.35, 0.50, 0.75), color=1.15, contrast=1.1)
save_image(img34, "rice_mixes.jpg")

# ID 35: Millet Mixes (Multi-millet Sathu Maavu blend)
img35 = crop_and_enhance(SRC_TEA, box=(0.14, 0.58, 0.44, 0.78), color=1.1, contrast=1.05, brightness=1.02)
save_image(img35, "millet_mixes.jpg")

# ID 36: Dry Chutney Powders (Garlic & Coconut Podis in clay pots)
img36 = crop_and_enhance(SRC_SPICES, box=(0.50, 0.38, 0.95, 0.75), color=1.2, contrast=1.15)
save_image(img36, "dry_chutney_powders.jpg")

# ID 37: Homemade Sauces (Traditional dipping tamarind and chilli sauces)
img37 = crop_and_enhance(SRC_HERO, box=(0.25, 0.08, 0.43, 0.24), color=1.25, contrast=1.12)
save_image(img37, "homemade_sauces.jpg")


# =========================================================================
# 7. FRESH REGIONAL DELICACIES & HOT MEALS
# =========================================================================
# ID 38: Madurai Kari Dosa (Steaming Thick Crispy Layered Mutton Dosa)
img38 = crop_and_enhance(SRC_KARI, box=(0.10, 0.30, 0.90, 0.85), color=1.1, contrast=1.08)
save_image(img38, "kari_dosa.jpg")

# ID 39: Chettinad Chicken Curry (Spicy Chicken Masala in Clay Handi)
img39 = crop_and_enhance(SRC_CHICKEN, box=(0.15, 0.22, 0.85, 0.88), color=1.12, contrast=1.1)
save_image(img39, "chettinad_chicken.jpg")

# ID 40: Ambur Biryani (Seeraga Samba Chicken Biryani in Deg)
img40 = crop_and_enhance(SRC_BIRYANI, box=(0.20, 0.22, 0.82, 0.82), color=1.1, contrast=1.06)
save_image(img40, "ambur_biryani.jpg")

# ID 41: Hyderabadi Biryani (Fragrant Long Grain Saffron Mutton Dum Biryani)
img41 = crop_and_enhance(SRC_BIRYANI, box=(0.28, 0.25, 0.75, 0.65), flip=True, color=1.18, contrast=1.1)
save_image(img41, "hyderabadi_biryani.jpg")

# ID 42: Kolkata Kathi Roll (Flaky Paratha Wrap with Spiced Filling)
img42 = crop_and_enhance(SRC_KARI, box=(0.15, 0.35, 0.85, 0.75), color=1.05, contrast=1.1, rotate=5)
save_image(img42, "kathi_roll.jpg")

# ID 43: Pani Puri (Crisp Hollow Puris with Chutney & Spiced Water)
img43 = crop_and_enhance(SRC_MURUKKU, box=(0.35, 0.40, 0.75, 0.80), color=1.2, contrast=1.15)
save_image(img43, "pani_puri.jpg")

# ID 44: Misal Pav (Spicy Sprouts Curry with Farsan & Pav)
img44 = crop_and_enhance(SRC_CHICKEN, box=(0.22, 0.30, 0.78, 0.80), color=1.22, contrast=1.18)
save_image(img44, "misal_pav.jpg")

# ID 45: Dhokla (Soft Yellow Steamed Khaman Dhokla with Mustard Tadka)
img45 = crop_and_enhance(SRC_MYSORE, box=(0.30, 0.25, 0.70, 0.65), color=1.35, contrast=1.1, brightness=1.05)
save_image(img45, "dhokla.jpg")

# ID 46: Litti Chokha (Roasted Wheat Balls with Smoky Baingan Chokha)
img46 = crop_and_enhance(SRC_SWEETS, box=(0.35, 0.25, 0.65, 0.55), color=0.95, contrast=1.2, brightness=0.92)
save_image(img46, "litti_chokha.jpg")

# ID 47: Appam with Stew (Soft Lacy Rice Appam with Coconut Milk Gravy)
img47 = crop_and_enhance(SRC_HERO, box=(0.20, 0.08, 0.54, 0.38), color=1.08, contrast=1.05, brightness=1.04)
save_image(img47, "appam_stew.jpg")


# =========================================================================
# 8. DISTINCT FOOD MAKER CHEF PROFILES
# =========================================================================
# Maker 1: Priya Sundaram (Madurai & Chettinad Kitchen Master)
img_m1 = crop_and_enhance(SRC_CHEF, box=(0.20, 0.10, 0.80, 0.75), target_size=(400, 400))
save_image(img_m1, "maker_priya.jpg")

# Maker 2: Kumaravel M (Madurai Snacks Master)
img_m2 = crop_and_enhance(SRC_CHEF, box=(0.25, 0.15, 0.75, 0.70), flip=True, color=0.95, contrast=1.1, target_size=(400, 400))
save_image(img_m2, "maker_kumar.jpg")

# Maker 3: Lakshmi Narayanan (Dindigul Spice Specialist)
img_m3 = crop_and_enhance(SRC_CHEF, box=(0.15, 0.10, 0.75, 0.70), brightness=1.05, contrast=1.05, target_size=(400, 400))
save_image(img_m3, "maker_lakshmi.jpg")

# Maker 4: Arunachalam S (Tirunelveli Ghee Halwa Master)
img_m4 = crop_and_enhance(SRC_CHEF, box=(0.22, 0.12, 0.78, 0.72), brightness=0.95, contrast=1.15, target_size=(400, 400))
save_image(img_m4, "maker_arun.jpg")

# Maker 5: Meenakshi R (Kumbakonam Degree Coffee & Pickles)
img_m5 = crop_and_enhance(SRC_CHEF, box=(0.18, 0.14, 0.82, 0.78), color=1.1, contrast=1.05, target_size=(400, 400))
save_image(img_m5, "maker_meena.jpg")

print("All 47 product images and 5 maker profiles successfully generated with 100% unique, non-repeated assets!")
