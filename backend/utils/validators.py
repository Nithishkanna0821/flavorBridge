import os
import re
import uuid
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB

def allowed_file(filename: str) -> bool:
    """Check if uploaded file has a permitted extension."""
    if not filename or '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS

def validate_email(email: str) -> bool:
    """Basic email regex validation."""
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(pattern, email.strip()))

def validate_phone(phone: str) -> bool:
    """Validate 10-digit Indian phone numbers."""
    if not phone:
        return False
    clean = re.sub(r'[\s\-+]', '', phone)
    return len(clean) >= 10 and clean[-10:].isdigit()

def validate_product_data(data: dict) -> tuple[bool, str]:
    """Validate incoming product form data."""
    name = data.get('name', '').strip()
    category = data.get('category', '').strip()
    price = data.get('price', '')
    product_type = data.get('product_type', '').strip()
    
    if not name:
        return False, "Product name is required."
    if not category:
        return False, "Category is required."
    if not product_type:
        return False, "Product type is required."
    
    try:
        price_val = float(price)
        if price_val <= 0:
            return False, "Price must be greater than zero."
    except (ValueError, TypeError):
        return False, "Price must be a valid number."
        
    stock = data.get('stock')
    if stock is not None and str(stock).strip():
        try:
            stock_val = int(stock)
            if stock_val < 0:
                return False, "Stock cannot be negative."
        except ValueError:
            return False, "Stock must be an integer."
            
    return True, ""

def save_uploaded_image(file_storage, target_directory: str) -> str:
    """
    Safely save an uploaded image file with a unique filename and return the relative path.
    """
    if not file_storage or not file_storage.filename:
        return ""
        
    if not allowed_file(file_storage.filename):
        return ""
        
    os.makedirs(target_directory, exist_ok=True)
    
    original_name = secure_filename(file_storage.filename)
    ext = original_name.rsplit('.', 1)[1].lower() if '.' in original_name else 'jpg'
    unique_filename = f"{uuid.uuid4().hex[:12]}_{original_name}"
    
    full_path = os.path.join(target_directory, unique_filename)
    file_storage.save(full_path)
    
    return unique_filename
