import hashlib
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import threading
import time
import smtplib
from email.message import EmailMessage
from datetime import datetime
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash 
import mysql.connector
import os
from werkzeug.utils import secure_filename

# --- AI & DATA IMPORTS ---
import pandas as pd
import numpy as np
from PIL import Image
from io import BytesIO
import requests
from sklearn.metrics.pairwise import cosine_similarity
import urllib.parse

# We will use Sentence-Transformers for combined text/image embeddings
from sentence_transformers import SentenceTransformer 
# Note: Sentence-Transformers abstracts away both CLIP and SBERT for multimodal models.

app = Flask(__name__)
CORS(app) 

app.secret_key = '12345'  # For session management, if needed

# --- FILE UPLOAD CONFIGURATION (For saving user's uploaded image) ---
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- DATABASE CONFIGURATION (Remains the same using mysql.connector) ---
# DB_HOST = '127.0.0.1'
# DB_USER = 'root'         
# DB_PASSWORD = ''         
# DB_NAME = 'price_ai_db'
DB_HOST = 'localhost'
DB_USER =   'root'
DB_PASSWORD = ''    
DB_NAME = 'price_ai_db'

def get_db_connection():
    try:
        return mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None 
    
def ensure_alerts_table():
    conn = get_db_connection()
    if conn is None:
        print("Could not ensure alerts table; DB connection failed.")
        return
    try:
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                product_hash VARCHAR(1024) NOT NULL,
                product_name TEXT,
                product_url TEXT,
                target_price DECIMAL(12,2) NOT NULL,
                current_price DECIMAL(12,2) DEFAULT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                notified TINYINT(1) DEFAULT 0,
                notified_at TIMESTAMP NULL DEFAULT NULL
            ) ENGINE=InnoDB;
        ''')
        # Add product_url column if it doesn't exist (for existing databases)
        try:
            cur.execute("ALTER TABLE alerts ADD COLUMN product_url TEXT AFTER product_name")
            conn.commit()
        except Exception:
            # Column already exists, ignore
            pass
        conn.commit()
    except Exception as e:
        print(f"Error creating alerts table: {e}")
    finally:
        if conn: conn.close()

def ensure_queries_table():
    conn = get_db_connection()
    if conn is None:
        print("Could not ensure queries table; DB connection failed.")
        return
    try:
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS queries (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255),
                email VARCHAR(255),
                message TEXT,
                status VARCHAR(50) DEFAULT 'open',
                admin_reply TEXT,
                replied_at DATETIME NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB;
        ''')
        conn.commit()
    except Exception as e:
        print(f"Error creating queries table: {e}")
    finally:
        if conn: conn.close()

def ensure_admins_table():
    conn = get_db_connection()
    if conn is None:
        print("Could not ensure admins table; DB connection failed.")
        return
    try:
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) UNIQUE,
                password_hash VARCHAR(255),
                full_name VARCHAR(255),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB;
        ''')
        conn.commit()
    except Exception as e:
        print(f"Error creating admins table: {e}")
    finally:
        if conn: conn.close()

def create_default_admin_from_env():
    admin_user = os.environ.get('ADMIN_USER')
    admin_pass = os.environ.get('ADMIN_PASS')
    if not admin_user or not admin_pass:
        return
    conn = get_db_connection()
    if conn is None:
        return
    try:
        cur = conn.cursor()
        cur.execute('SELECT id FROM admins WHERE username = %s', (admin_user,))
        if cur.fetchone():
            return
        hashed = generate_password_hash(admin_pass)
        cur.execute('INSERT INTO admins values (username, password_hash, full_name) VALUES (%s, %s, %s)', (admin_user, hashed, 'Admin'))
        conn.commit()
        print(f"Default admin '{admin_user}' created from environment variables.")
    except Exception as e:
        print(f"Error creating default admin: {e}")
    finally:
        if conn: conn.close()

# --- AI MODEL & DATA LOADING ---
# C:\xampp\htdocs\price_compare_system\app.py

# ... (Previous imports and DB config) ...

# --- AI MODEL & DATA LOADING ---
MODEL_NAME = 'clip-ViT-B-32' # A common Sentence-Transformer model for multimodal search
MODEL = None
PRODUCT_DF = None
PRODUCT_EMBEDDINGS = None

def load_ai_model_and_data():
    EMBEDDINGS_FILE = 'product_embeddings.npy'
    global MODEL, PRODUCT_DF, PRODUCT_EMBEDDINGS

    print("--- Loading AI Model and Data ---")
    
    # 1. Load the Multimodal Sentence Transformer Model
    try:
        # --- FIX START: Ensure MODEL is defined here ---
        MODEL = SentenceTransformer(MODEL_NAME) 
        print(f"AI Model ({MODEL_NAME}) loaded successfully.")
        # --- FIX END ---
    except Exception as e:
        print(f"FATAL ERROR: Could not load the SentenceTransformer model '{MODEL_NAME}'.")
        print(f"Details: {e}")
        # If model loading fails, set MODEL to None and stop execution.
        MODEL = None
        return # <--- CRITICAL: Exit the function if model loading fails.

    # 2. Load Product Data from CSV
    try:
        PRODUCT_DF = pd.read_csv('merged_output.csv')
        
        # --- FIX: Clean, Fill, and Lowercase ALL components ---
        PRODUCT_DF['product_name'] = PRODUCT_DF['product_name'].fillna('').str.lower()
        PRODUCT_DF['brand'] = PRODUCT_DF['brand'].fillna('').str.lower()
        PRODUCT_DF['category'] = PRODUCT_DF['category'].fillna('').str.lower()
        
        # 2. Combine the fields 
        PRODUCT_DF['search_text'] = (
            PRODUCT_DF['product_name'].astype(str) + " " + 
            PRODUCT_DF['brand'].astype(str) + " " + 
            PRODUCT_DF['category'].astype(str)
        )
        
        # 3. Trim whitespace
        PRODUCT_DF['search_text'] = PRODUCT_DF['search_text'].str.strip()

        print(f"Loaded {len(PRODUCT_DF)} products.")
        
    except FileNotFoundError:
        print("FATAL ERROR: merged_output.csv not found. Create the mock file.")
        PRODUCT_DF = None
        return
    if os.path.exists(EMBEDDINGS_FILE):
        # OPTION A: Load existing embeddings (FAST!)
        print(f"Loading pre-calculated embeddings from {EMBEDDINGS_FILE}...")
        PRODUCT_EMBEDDINGS = np.load(EMBEDDINGS_FILE,allow_pickle=True)
        print(f"[LOADED  embeddings instantly.")
        # 3. Pre-calculate Embeddings (Text Part)
    else:
        # OPTION B: Calculate and save (SLOW, but only runs once)
        print("Pre-calculating product embeddings (this may take a moment)...")

        PRODUCT_EMBEDDINGS = MODEL.encode(PRODUCT_DF['search_text'].tolist(),convert_to_tensor=False )
        np.save(EMBEDDINGS_FILE, PRODUCT_EMBEDDINGS)
        print(f"[SAVED  new embeddings to {EMBEDDINGS_FILE}.")
    # print("Pre-calculating product embeddings (this may take a moment)...")
    
    # This line (where the original error occurred) now correctly uses the loaded MODEL
    # PRODUCT_EMBEDDINGS = MODEL.encode(
    #     PRODUCT_DF['search_text'].tolist(), 
    #     convert_to_tensor=False
    # )
    # print(f"Loaded {len(PRODUCT_EMBEDDINGS)} text embeddings.")

# ... (Rest of your Flask code remains the same) ...
# --- NEW ROUTE: SERVE INDEX.HTML ---
# @app.route('/')
# def serve_index():
#     """Serves the main HTML file when the root URL is accessed."""
#     # Ensure index.html is in a folder named 'templates'
#     return render_template('index.html')

# --- API ENDPOINT FOR REGISTRATION ---
@app.route('/api/register', methods=['POST'])
def register_user():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Please fill in all required information to create your account."}), 400

    full_name = data.get('fullName')
    email = data.get('email')
    password = data.get('password')

    if not all([full_name, email, password]):
        missing = []
        if not full_name: missing.append("name")
        if not email: missing.append("email")
        if not password: missing.append("password")
        return jsonify({"success": False, "message": f"Please provide your {', '.join(missing)} to continue."}), 400

    conn = None # Initialize connection
    try:
        conn = get_db_connection() # <--- NEW: Get custom connection
        if conn is None:
             # Handle connection failure gracefully
            return jsonify({"success": False, "message": "Could not connect to database."}), 500

        cur = conn.cursor()

        # 1. Check if the user already exists
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        if cur.fetchone():
            return jsonify({"success": False, "message": "This email address is already registered. Please sign in or use a different email address."}), 409

        # 2. Hash the password
        hashed_password = generate_password_hash(password)

        # 3. Insert the new user into the database
        # Note: mysql.connector uses (value,) for single-item tuples
        cur.execute(
            """INSERT INTO users (full_name, email, password_hash, registration_date) 
            VALUES (%s, %s, %s, %s)""", 
            (full_name, email, hashed_password, datetime.now())
        )
        
        # 4. Commit the transaction
        conn.commit()

        # 5. Success response
        return jsonify({
            "success": True, 
            "message": "Registration successful! Welcome.",
            "user": {"fullName": full_name, "email": email}
        }), 201

    except Exception as e:
        print(f"Database error: {e}")
        return jsonify({"success": False, "message": "We encountered an issue while creating your account. Please try again or contact support if the problem continues."}), 500
    
    finally:
        if 'cur' in locals() and cur is not None:
             cur.close()
        if conn is not None:
            conn.close() # <--- NEW: Close connection explicitly

# Optional: Simple Login Endpoint 
@app.route('/api/login', methods=['POST'])
def login_user():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not all([email, password]):
        missing = "email and password" if not email and not password else ("email" if not email else "password")
        return jsonify({"success": False, "message": f"Please enter your {missing} to sign in."}), 400

    conn = None # Initialize connection
    try:
        conn = get_db_connection() # <--- NEW: Get custom connection
        if conn is None:
             # Handle connection failure gracefully
            return jsonify({"success": False, "message": "Could not connect to database."}), 500
        
        # Use buffered=True to fetch results properly, or fetchall/fetchone immediately
        cur = conn.cursor(dictionary=True) # Fetch results as dictionaries

        cur.execute("SELECT id, password_hash, full_name FROM users WHERE email = %s", (email,))
        user_record = cur.fetchone()

        if user_record and check_password_hash(user_record['password_hash'], password):
            # *** CRITICAL: Store user info in the session ***
            session['logged_in'] = True
            session['user_id'] = user_record['id'] # Store the unique user ID
            session['email'] = email
            return jsonify({
                "success": True, 
                "message": "Login successful",
                "user": {"id": user_record['id'], "fullName": user_record['full_name'], "email": email}
            })
        else:
            return jsonify({"success": False, "message": "The email or password you entered is incorrect. Please check your credentials and try again."}), 401
    
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({"success": False, "message": "We encountered an issue while signing you in. Please try again or contact support if the problem continues."}), 500
    
    finally:
        if 'cur' in locals() and cur is not None:
             cur.close()
        if conn is not None:
            conn.close() # <--- NEW: Close connection explicitly

def find_matching_products_by_text(query_text):
    """
    Finds products by text matching in product_name, brand, or category.
    Uses simple text search to find products containing the query text.
    """
    global PRODUCT_DF
    
    if PRODUCT_DF is None or PRODUCT_DF.empty:
        return []
    
    # Normalize query text (lowercase and strip)
    normalized_query = query_text.strip().lower()
    
    if not normalized_query:
        return []
    
    # Filter products where the query text appears in product_name, brand, or category
    # Since PRODUCT_DF columns are already lowercased during loading, we can directly search
    mask = (
        PRODUCT_DF['product_name'].str.contains(normalized_query, na=False, case=False) |
        PRODUCT_DF['brand'].str.contains(normalized_query, na=False, case=False) |
        PRODUCT_DF['category'].str.contains(normalized_query, na=False, case=False)
    )
    
    matching_df = PRODUCT_DF[mask].head(100)  # Limit to 100 results for performance
    
    if matching_df.empty:
        return []
    
    # Group products by normalized name (similar to find_matching_products)
    grouped = {}
    for idx, row in matching_df.iterrows():
        row_dict = row.to_dict()
        
        # Create grouping key (same logic as find_matching_products)
        original_name = row_dict.get('product_name') or ""
        group_key = "".join(filter(str.isalnum, str(original_name).lower()))
        
        if not group_key:
            group_key = f"product_{idx}"
        
        # Normalize price
        price_val = None
        try:
            price_val = float(row_dict.get('price'))
        except Exception:
            try:
                price_val = float(str(row_dict.get('price')).replace('Rs.', '').replace(',', '').strip())
            except Exception:
                price_val = None
        
        # Derive domain and favicon
        url_raw = row_dict.get('url') or ''
        domain = ''
        site_icon = ''
        try:
            parsed = urllib.parse.urlparse(url_raw)
            domain = parsed.netloc.lower().replace('www.', '')
            if domain:
                site_icon = f"https://www.google.com/s2/favicons?domain={domain}&sz=128"
        except Exception:
            pass
        
        listing = {
            'source': row_dict.get('source'),
            'price': price_val if price_val is not None else row_dict.get('price'),
            'price_raw': row_dict.get('price'),
            'image_src': row_dict.get('image_src'),
            'url': url_raw,
            'domain': domain,
            'site_icon': site_icon
        }
        
        if group_key not in grouped:
            # Calculate a simple relevance score based on where the match occurred
            score = 1.0
            if normalized_query in (row_dict.get('product_name') or '').lower():
                score = 1.0  # Highest score for name match
            elif normalized_query in (row_dict.get('brand') or '').lower():
                score = 0.8  # Lower score for brand match
            else:
                score = 0.6  # Lowest score for category match
            
            grouped[group_key] = {
                'product_name': original_name,
                'brand': row_dict.get('brand'),
                'similarity_score': score,
                'listings': [listing],
                'seen_domains': {domain: listing} if domain else {},
                'category': row_dict.get('category')
            }
        else:
            # Grouping: Deduplicate by domain
            seen = grouped[group_key].get('seen_domains', {})
            if domain:
                existing = seen.get(domain)
                if existing is None:
                    grouped[group_key]['listings'].append(listing)
                    seen[domain] = listing
                else:
                    # Keep cheapest for same domain
                    try:
                        new_p = float(listing['price'])
                        old_p = float(existing['price'])
                        if new_p < old_p:
                            for list_idx, it in enumerate(grouped[group_key]['listings']):
                                if it.get('domain') == domain:
                                    grouped[group_key]['listings'][list_idx] = listing
                                    break
                            seen[domain] = listing
                    except: pass
            else:
                grouped[group_key]['listings'].append(listing)
    
    # Prepare final results list
    results = []
    for g in grouped.values():
        # Find the "best" (cheapest) listing
        best = None
        for l in g['listings']:
            if isinstance(l.get('price'), (int, float)):
                if best is None or l['price'] < best['price']:
                    best = l
        if best is None and g['listings']:
            best = g['listings'][0]
        
        results.append({
            'product_name': g['product_name'],
            'brand': g.get('brand'),
            'similarity_score': g['similarity_score'],
            'listings': g['listings'],
            'price': best.get('price_raw') if best else None,
            'image_src': best.get('image_src') if best else None,
            'url': best.get('url') if best else None,
            'source': best.get('source') if best else None,
            'category': g.get('category')
        })
    
    return sorted(results, key=lambda x: x['similarity_score'], reverse=True)

def find_matching_products(query_embedding):
    """
    Finds and groups products closest to the query embedding.
    Ensures different sources for the same product are grouped into one card.
    """
    global PRODUCT_EMBEDDINGS
    
    if PRODUCT_EMBEDDINGS is None:
        return []

    # Calculate cosine similarity
    similarities = cosine_similarity([query_embedding], PRODUCT_EMBEDDINGS)[0]
    top_indices = np.argsort(similarities)[::-1][:30] # Increased limit to find more matches across sites

    grouped = {}
    for i in top_indices:
        row = PRODUCT_DF.iloc[i].to_dict()
        row_similarity = float(similarities[i])
        
        # --- IMPROVED GROUPING KEY ---
        # Normalize the name (lowercase, remove non-alphanumeric, and strip)
        # This makes "iPhone 15" and "iphone 15!" group into the same key: "iphone15"
        original_name = row.get('product_name') or ""
        group_key = "".join(filter(str.isalnum, str(original_name).lower()))
        
        if not group_key:
            group_key = f"product_{i}"

        # Normalize price
        price_val = None
        try:
            price_val = float(row.get('price'))
        except Exception:
            try:
                # Handle "Rs. 1,000" formats
                price_val = float(str(row.get('price')).replace('Rs.', '').replace(',', '').strip())
            except Exception:
                price_val = None

        # Derive domain and favicon
        url_raw = row.get('url') or ''
        domain = ''
        site_icon = ''
        try:
            parsed = urllib.parse.urlparse(url_raw)
            domain = parsed.netloc.lower().replace('www.', '')
            if domain:
                site_icon = f"https://www.google.com/s2/favicons?domain={domain}&sz=128"
        except Exception:
            pass

        listing = {
            'source': row.get('source'),
            'price': price_val if price_val is not None else row.get('price'),
            'price_raw': row.get('price'),
            'image_src': row.get('image_src'),
            'url': url_raw,
            'domain': domain,
            'site_icon': site_icon
        }

        if group_key not in grouped:
            grouped[group_key] = {
                'product_name': original_name, # Keep original name for display
                'brand': row.get('brand'),
                'similarity_score': row_similarity,
                'listings': [listing],
                'seen_domains': {domain: listing} if domain else {}
            }
        else:
            # Grouping: Deduplicate by domain (keep cheapest if same site lists it twice)
            seen = grouped[group_key].get('seen_domains', {})
            if domain:
                existing = seen.get(domain)
                if existing is None:
                    grouped[group_key]['listings'].append(listing)
                    seen[domain] = listing
                else:
                    # Compare and keep cheapest for this specific domain
                    try:
                        new_p = float(listing['price'])
                        old_p = float(existing['price'])
                        if new_p < old_p:
                            for idx, it in enumerate(grouped[group_key]['listings']):
                                if it.get('domain') == domain:
                                    grouped[group_key]['listings'][idx] = listing
                                    break
                            seen[domain] = listing
                    except: pass
            else:
                grouped[group_key]['listings'].append(listing)

            if row_similarity > grouped[group_key]['similarity_score']:
                grouped[group_key]['similarity_score'] = row_similarity

    # Prepare final results list
    results = []
    for g in grouped.values():
        # Find the "best" (cheapest) listing to show as the main face of the card
        best = None
        for l in g['listings']:
            if isinstance(l.get('price'), (int, float)):
                if best is None or l['price'] < best['price']:
                    best = l
        if best is None and g['listings']:
            best = g['listings'][0]

        results.append({
            'product_name': g['product_name'],
            'brand': g.get('brand'),
            'similarity_score': g['similarity_score'],
            'listings': g['listings'],
            'price': best.get('price_raw') if best else None,
            'image_src': best.get('image_src') if best else None,
            'url': best.get('url') if best else None,
            'source': best.get('source') if best else None
        })

    return sorted(results, key=lambda x: x['similarity_score'], reverse=True)

# --- API ENDPOINT FOR SEARCH (Handles both text and image search) ---
@app.route('/api/search', methods=['POST'])
def search_products():
    query_embedding = None

    # A. HANDLE IMAGE UPLOAD (The client will use FormData)
    if 'product_image' in request.files:
        if MODEL is None or PRODUCT_EMBEDDINGS is None:
            return jsonify({"success": False, "message": "Our search system is temporarily unavailable. Please try again in a few moments or contact support."}), 503
        file = request.files['product_image']
        if file.filename != '' and allowed_file(file.filename):
            try:
                # Read image directly from memory (faster than saving to disk)
                image = Image.open(BytesIO(file.read()))
                query_embedding = MODEL.encode(image, convert_to_tensor=False)
                search_type = "Image"
            except Exception as e:
                print(f"Image processing error: {e}")
                return jsonify({"success": False, "message": "We couldn't process your image. Please make sure it's a valid image file (PNG, JPG, or JPEG) and try again."}), 400
        else:
            return jsonify({"success": False, "message": "Please select a valid image file (PNG, JPG, or JPEG) to search."}), 400

    # B. HANDLE TEXT QUERY (The client will use JSON data)
    elif request.data:
        if PRODUCT_DF is None:
            return jsonify({"success": False, "message": "Our product database is temporarily unavailable. Please try again in a few moments."}), 503
            
        data = request.get_json()
        query_text = data.get('query')
        
        if query_text:
            # Use text-based search for text queries
            normalized_query = query_text.strip()
            results = find_matching_products_by_text(normalized_query)
            search_type = "Text"
            
            # Format results to include only relevant columns
            formatted_results = []
            for res in results:
                # Format listings (if present) and create a best-price summary for the card
                listings = []
                for l in res.get('listings', []):
                    listings.append({
                        'source': l.get('source'),
                        'price': f"Rs.{l['price']:.2f}" if isinstance(l.get('price'), (int, float)) else l.get('price'),
                        'image_src': l.get('image_src'),
                        'url': l.get('url'),
                        'site_icon': l.get('site_icon')
                    })

                # Backwards-compatible top-level fields use the best listing returned by the grouping
                formatted_results.append({
                    "product_name": res.get('product_name'),
                    "brand": res.get('brand'),
                    "price": res.get('price'),
                    "rating": res.get('rating'),
                    "image_src": res.get('image_src'),
                    "url": res.get('url'),
                    "source": res.get('source'),
                    "category": res.get('category'),
                    "similarity_score": f"{res.get('similarity_score')*100:.2f}%",
                    "listings": listings
                })

            return jsonify({
                "success": True, 
                "message": f"{search_type} search complete.", 
                "results": formatted_results,
                "products_fetched_count": len(results)
            }), 200
        else:
            return jsonify({"success": False, "message": "Please enter a product name or search term to find products."}), 400
    
    # C. Perform Search and Return Results (for image search using embeddings)
    if query_embedding is not None:
        results = find_matching_products(query_embedding)
        
        # Format results to include only relevant columns
        formatted_results = []
        for res in results:
            # Format listings (if present) and create a best-price summary for the card
            listings = []
            for l in res.get('listings', []):
                listings.append({
                    'source': l.get('source'),
                    'price': f"Rs.{l['price']:.2f}" if isinstance(l.get('price'), (int, float)) else l.get('price'),
                    'image_src': l.get('image_src'),
                    'url': l.get('url'),
                    'site_icon': l.get('site_icon')
                })

            # Backwards-compatible top-level fields use the best listing returned by the grouping
            formatted_results.append({
                "product_name": res.get('product_name'),
                "brand": res.get('brand'),
                "price": res.get('price'),
                "rating": res.get('rating'),
                "image_src": res.get('image_src'),
                "url": res.get('url'),
                "source": res.get('source'),
                "category": res.get('category'),
                "similarity_score": f"{res.get('similarity_score')*100:.2f}%",
                "listings": listings
            })

        return jsonify({
            "success": True, 
            "message": f"{search_type} search complete.", 
            "results": formatted_results,
            "products_fetched_count": len(results)
        }), 200
    
    return jsonify({"success": False, "message": "An unexpected error occurred during your search. Please try again or contact support if the problem persists."}), 500

# app.py
def get_tracked_items_count(user_id):
    conn = get_db_connection()
    if conn is None: return 0
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM wishlist WHERE user_id = %s", (user_id,))
        count = cur.fetchone()[0]
        return count
    except Exception as e:
        print(f"Error getting tracked count: {e}")
        return 0
    finally:
        if conn: conn.close()

def send_email_notification(to_email, subject, body):
    SMTP_HOST = os.environ.get('SMTP_HOST')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
    SMTP_USER = os.environ.get('SMTP_USER')
    SMTP_PASS = os.environ.get('SMTP_PASS')
    FROM_EMAIL = os.environ.get('FROM_EMAIL', SMTP_USER)

    if not SMTP_HOST or not SMTP_USER or not SMTP_PASS:
        print('SMTP not configured; skipping email send.')
        return False

    try:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = FROM_EMAIL
        msg['To'] = to_email
        msg.set_content(body)

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(SMTP_USER, SMTP_PASS)
            smtp.send_message(msg)

        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def check_alerts_loop(poll_interval=60):
    print('Starting alerts background checker thread...')
    while True:
        conn = None
        try:
            conn = get_db_connection()
            if conn is None:
                time.sleep(poll_interval)
                continue
            # FIX: Use transaction and proper locking to prevent race conditions
            conn.start_transaction()
            cur = conn.cursor(dictionary=True)
            cur.execute('SELECT * FROM alerts WHERE notified = 0 FOR UPDATE')
            alerts = cur.fetchall()

            for a in alerts:
                product_hash = a['product_hash']
                target = float(a['target_price'])

                # Find latest known price from price_history (FIX: use history_id instead of id)
                try:
                    cur.execute('SELECT price FROM price_history WHERE product_hash = %s ORDER BY history_id DESC LIMIT 1', (product_hash,))
                    row = cur.fetchone()
                    if row and row.get('price') is not None:
                        current_price = float(row['price'])
                    else:
                        current_price = None
                except Exception:
                    current_price = None

                # Always update current_price in alerts table so users can see the latest price
                if current_price is not None:
                    cur.execute('UPDATE alerts SET current_price = %s WHERE id = %s', (current_price, a['id']))
                
                if current_price is not None and current_price <= target:
                    # mark as notified (within transaction)
                    cur.execute('UPDATE alerts SET notified = 1, notified_at = NOW(), current_price = %s WHERE id = %s', (current_price, a['id'],))

                    # Fetch user email
                    try:
                        cur.execute('SELECT email, full_name FROM users WHERE id = %s', (a['user_id'],))
                        user = cur.fetchone()
                        to_email = user['email'] if user else None
                        user_name = user['full_name'] if user else 'User'
                    except Exception:
                        to_email = None
                        user_name = 'User'

                    # Insert a simple notification log (optional)
                    try:
                        cur.execute('INSERT INTO notifications (user_id, product_hash, message, created_at) VALUES (%s, %s, %s, NOW())',
                                    (a['user_id'], product_hash, f'Price dropped to {current_price} (target {target})'))
                    except Exception:
                        # notifications table may not exist; ignore
                        pass

                    # Send email if possible (FIX: use product_url instead of product_hash)
                    if to_email:
                        product_url = a.get('product_url') or (a.get('product_hash') if (a.get('product_hash', '').startswith('http://') or a.get('product_hash', '').startswith('https://')) else None)
                        link_text = product_url if product_url else 'Product link not available'
                        subject = f"Price Alert: {a.get('product_name', 'Product')} dropped to Rs.{current_price:.2f}"
                        body = f"Hi {user_name},\n\nThe product '{a.get('product_name')}' has reached Rs.{current_price:.2f}, which is at or below your target of Rs.{target:.2f}.\n\nView Product: {link_text}\n\n--\nPriceAI"
                        send_email_notification(to_email, subject, body)
            
            # FIX: Commit transaction after all updates (prevents race conditions)
            conn.commit()
            conn.close()

        except Exception as e:
            print(f"Error in alerts checker loop: {e}")
            if conn:
                try:
                    conn.rollback()
                    conn.close()
                except:
                    pass

        time.sleep(poll_interval)

# Helper function to generate a stable, unique ID for a product
def get_product_hash(product):
    base = (
        str(product.get('url', '')) +
        str(product.get('product_name', '')) +
        str(product.get('brand', '')) +
        str(product.get('source', ''))
    )
    return hashlib.sha256(base.encode()).hexdigest()

# --- API ENDPOINT FOR WISHLIST ADD ---
@app.route('/api/wishlist/add', methods=['POST'])
def add_to_wishlist():
    from flask import session
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Please sign in to access this feature."}), 401
    
    data = request.get_json()
    product = data.get('product') # Full product dictionary from search results

    if not product or 'product_name' not in product or 'brand' not in product:
        return jsonify({"success": False, "message": "Unable to add product: Missing product information. Please try again."}), 400

    user_id = session['user_id']
    product_hash = get_product_hash(product)
    
    # Extract data, converting price from formatted string (e.g., 'Rs.10999.00') to float
    price_str = str(product.get('price', 'Rs.0.00')).replace('Rs.', '').replace('$', '').strip()
    try:
        current_price = float(price_str)
    except ValueError:
        return jsonify({"success": False, "message": "Unable to add product: The product price information is invalid. Please try again."}), 400

    conn = get_db_connection()
    if conn is None: return jsonify({"success": False, "message": "We're experiencing technical difficulties. Please try again in a few moments."}), 500
    
    try:
        cur = conn.cursor()
        
        # Insert or ignore the product into the wishlist 
        sql = """
            INSERT INTO wishlist (user_id, product_hash, product_name, current_price, image_src) 
            VALUES (%s, %s, %s, %s, %s) 
            ON DUPLICATE KEY UPDATE 
                current_price = VALUES(current_price), 
                date_added = date_added 
        """
        cur.execute(
            sql, 
            (
                user_id, 
                product_hash, 
                product.get('product_name'), 
                current_price, 
                product.get('image_src')
            )
        )
        conn.commit()
        
        # Also log the current price to the price_history table (FIX: prevent duplicates)
        # Check if price already exists for this product_hash (within last 5 minutes to prevent spam)
        cur.execute(
            """SELECT history_id FROM price_history 
               WHERE product_hash = %s AND price = %s 
               AND timestamp > DATE_SUB(NOW(), INTERVAL 5 MINUTE)
               ORDER BY history_id DESC LIMIT 1""",
            (product_hash, current_price)
        )
        existing_price = cur.fetchone()
        if not existing_price:
            cur.execute(
                """INSERT INTO price_history (product_hash, price, price_source) VALUES (%s, %s, %s)""",
                (product_hash, current_price, product.get('source', 'Unknown'))
            )
            conn.commit()

        return jsonify({"success": True, "message": "Product added to wishlist."})
        
    except Exception as e:
        print(f"Wishlist/Tracking error: {e}")
        return jsonify({"success": False, "message": "We encountered an issue while adding the product to your wishlist. Please try again."}), 500
    finally:
        if conn: conn.close()

@app.route('/api/alerts/add', methods=['POST'])
def add_alert():
    from flask import session
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Please sign in to create price alerts."}), 401

    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Please provide the required information to create a price alert."}), 400

    product = data.get('product')
    target_price = data.get('target_price')

    if not product or target_price is None:
        missing = "product information" if not product else "target price"
        return jsonify({"success": False, "message": f"Please provide the {missing} to create a price alert."}), 400

    user_id = session['user_id']
    product_hash = get_product_hash(product)

    try:
        target_price_val = float(target_price)
        # FIX: Validate target price - must be positive
        if target_price_val <= 0:
            return jsonify({"success": False, "message": "Target price must be greater than Rs. 0. Please enter a valid amount."}), 400
    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "Please enter a valid price amount (numbers only, e.g., 299.99)."}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "message": "We're experiencing technical difficulties. Please try again in a few moments."}), 500

    try:
        cur = conn.cursor()
        # FIX: Check for duplicate alerts (prevent multiple alerts for same product)
        cur.execute(
            "SELECT id FROM alerts WHERE user_id = %s AND product_hash = %s AND notified = 0",
            (user_id, product_hash)
        )
        existing_alert = cur.fetchone()
        if existing_alert:
            return jsonify({"success": False, "message": "You already have an active price alert for this product. You can edit or delete the existing alert from your alerts page."}), 409
        
        # Get product URL - try from product.url first, then from listings
        product_url = product.get('url', '')
        if not product_url and product.get('listings'):
            # Try to get URL from first listing
            for listing in product.get('listings', []):
                if listing.get('url'):
                    product_url = listing.get('url')
                    break
        
        # Get current price from product if available
        current_price = None
        price_str = str(product.get('price', '')).replace('Rs.', '').replace('$', '').replace(',', '').strip()
        try:
            current_price = float(price_str) if price_str else None
        except (ValueError, TypeError):
            current_price = None
        
        # If no price from product, try from listings
        if current_price is None and product.get('listings'):
            for listing in product.get('listings', []):
                listing_price = listing.get('price')
                if listing_price:
                    try:
                        if isinstance(listing_price, (int, float)):
                            current_price = float(listing_price)
                        else:
                            price_clean = str(listing_price).replace('Rs.', '').replace('$', '').replace(',', '').strip()
                            current_price = float(price_clean) if price_clean else None
                        if current_price:
                            break
                    except (ValueError, TypeError):
                        continue
        
        cur.execute(
            "INSERT INTO alerts (user_id, product_hash, product_name, product_url, target_price, current_price) VALUES (%s, %s, %s, %s, %s, %s)",
            (user_id, product_hash, product.get('product_name'), product_url, target_price_val, current_price)
        )
        conn.commit()
        return jsonify({"success": True, "message": "Price alert created successfully. You'll be notified when the price drops."}), 201
    except mysql.connector.Error as e:
        print(f"Database error creating alert: {e}")
        return jsonify({"success": False, "message": "We encountered an issue while creating your price alert. Please try again."}), 500
    except Exception as e:
        print(f"Error creating alert: {e}")
        return jsonify({"success": False, "message": "An unexpected error occurred while creating your alert. Please try again or contact support if the problem continues."}), 500
    finally:
        if conn: conn.close()

# --- API ENDPOINT TO VIEW USER ALERTS ---
@app.route('/api/alerts/view', methods=['GET'])
def view_alerts():
    from flask import session
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Please sign in to access this feature."}), 401
    
    user_id = session['user_id']
    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "message": "We're experiencing technical difficulties. Please try again in a few moments."}), 500
    
    try:
        cur = conn.cursor(dictionary=True)
        
        # Get all alerts for the user with image from wishlist, ordered by creation date
        cur.execute("""
            SELECT a.id, a.product_name, a.product_hash, a.product_url, a.target_price, a.current_price, 
                   a.created_at, a.notified, a.notified_at,
                   (SELECT price FROM price_history WHERE product_hash = a.product_hash ORDER BY history_id DESC LIMIT 1) as latest_price,
                   (SELECT image_src FROM wishlist WHERE product_hash = a.product_hash AND user_id = a.user_id LIMIT 1) as image_src
            FROM alerts a
            WHERE a.user_id = %s
            ORDER BY a.created_at DESC
        """, (user_id,))
        
        alerts = cur.fetchall()
        
        # Format the alerts
        formatted_alerts = []
        for alert in alerts:
            latest_price = alert['latest_price'] if alert['latest_price'] else alert['current_price']
            product_hash = alert['product_hash']
            price_dropped = latest_price and latest_price <= float(alert['target_price'])
            
            # Use product_url if available, otherwise fallback to product_hash (in case it's a URL)
            product_url = alert.get('product_url') or (product_hash if (product_hash.startswith('http://') or product_hash.startswith('https://')) else None)
            
            formatted_alerts.append({
                "id": alert['id'],
                "product_name": alert['product_name'],
                "product_url": product_url,
                "image_src": alert['image_src'] if alert['image_src'] else None,
                "target_price": float(alert['target_price']),
                "current_price": float(latest_price) if latest_price else None,
                "created_at": alert['created_at'].strftime('%Y-%m-%d %H:%M') if alert['created_at'] else '',
                "notified": bool(alert['notified']),
                "notified_at": alert['notified_at'].strftime('%Y-%m-%d %H:%M') if alert['notified_at'] else None,
                "status": "Triggered" if alert['notified'] else "Active",
                "price_dropped": price_dropped,
                "product_hash": product_hash  # For price history API
            })
        
        return jsonify({
            "success": True,
            "alerts": formatted_alerts
        }), 200
        
    except Exception as e:
        print(f"Error fetching alerts: {e}")
        return jsonify({"success": False, "message": "We encountered an issue while loading your alerts. Please try again."}), 500
    finally:
        if conn: conn.close()

# --- API ENDPOINT TO DELETE ALERT ---
@app.route('/api/alerts/delete', methods=['POST'])
def delete_alert():
    from flask import session
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Please sign in to access this feature."}), 401
    
    data = request.get_json()
    alert_id = data.get('alert_id')
    
    if not alert_id:
        return jsonify({"success": False, "message": "Please select an alert to delete."}), 400
    
    user_id = session['user_id']
    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "message": "We're experiencing technical difficulties. Please try again in a few moments."}), 500
    
    try:
        cur = conn.cursor()
        # Verify the alert belongs to the user before deleting
        cur.execute("SELECT id FROM alerts WHERE id = %s AND user_id = %s", (alert_id, user_id))
        if not cur.fetchone():
            return jsonify({"success": False, "message": "The alert you're trying to delete doesn't exist or you don't have permission to delete it."}), 404
        
        cur.execute("DELETE FROM alerts WHERE id = %s AND user_id = %s", (alert_id, user_id))
        conn.commit()
        
        if cur.rowcount > 0:
            return jsonify({"success": True, "message": "Price alert deleted successfully."}), 200
        else:
            return jsonify({"success": False, "message": "Unable to delete alert. The alert may have already been removed."}), 404
            
    except Exception as e:
        print(f"Error deleting alert: {e}")
        return jsonify({"success": False, "message": "We encountered an issue while deleting your alert. Please try again."}), 500
    finally:
        if conn: conn.close()

# --- API ENDPOINT TO EDIT ALERT ---
@app.route('/api/alerts/edit', methods=['POST'])
def edit_alert():
    from flask import session
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Please sign in to access this feature."}), 401
    
    data = request.get_json()
    alert_id = data.get('alert_id')
    target_price = data.get('target_price')
    
    if not alert_id or target_price is None:
        return jsonify({"success": False, "message": "Please provide both the alert and the new target price to update."}), 400
    
    try:
        target_price_val = float(target_price)
        if target_price_val <= 0:
            return jsonify({"success": False, "message": "Target price must be greater than 0."}), 400
    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "Invalid target price. Please enter a valid number."}), 400
    
    user_id = session['user_id']
    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "message": "Database connection error. Please try again."}), 500
    
    try:
        cur = conn.cursor()
        # Verify the alert belongs to the user before updating
        cur.execute("SELECT id FROM alerts WHERE id = %s AND user_id = %s", (alert_id, user_id))
        if not cur.fetchone():
            return jsonify({"success": False, "message": "Alert not found or access denied."}), 404
        
        cur.execute(
            "UPDATE alerts SET target_price = %s WHERE id = %s AND user_id = %s",
            (target_price_val, alert_id, user_id)
        )
        conn.commit()
        
        if cur.rowcount > 0:
            return jsonify({"success": True, "message": "Price alert updated successfully."}), 200
        else:
            return jsonify({"success": False, "message": "Unable to update the alert. Please try again."}), 500
            
    except Exception as e:
        print(f"Error updating alert: {e}")
        return jsonify({"success": False, "message": "We encountered an issue while updating your alert. Please try again."}), 500
    finally:
        if conn: conn.close()

# --- API ENDPOINT FOR BULK DELETE ALERTS ---
@app.route('/api/alerts/bulk-delete', methods=['POST'])
def bulk_delete_alerts():
    from flask import session
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Please sign in to access this feature."}), 401
    
    data = request.get_json()
    alert_ids = data.get('alert_ids', [])
    
    if not alert_ids or not isinstance(alert_ids, list):
        return jsonify({"success": False, "message": "Please select at least one alert to delete."}), 400
    
    if len(alert_ids) == 0:
        return jsonify({"success": False, "message": "Please select one or more alerts to delete."}), 400
    
    user_id = session['user_id']
    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "message": "Database connection error."}), 500
    
    try:
        cur = conn.cursor()
        # Convert to tuple and delete only alerts belonging to the user
        placeholders = ','.join(['%s'] * len(alert_ids))
        cur.execute(
            f"DELETE FROM alerts WHERE id IN ({placeholders}) AND user_id = %s",
            tuple(alert_ids) + (user_id,)
        )
        conn.commit()
        deleted_count = cur.rowcount
        
        return jsonify({
            "success": True, 
            "message": f"Successfully deleted {deleted_count} alert(s)."
        }), 200
            
    except Exception as e:
        print(f"Error bulk deleting alerts: {e}")
        return jsonify({"success": False, "message": "We encountered an issue while deleting alerts. Please try again."}), 500
    finally:
        if conn: conn.close()

# --- API ENDPOINT FOR BULK DELETE WISHLIST ---
@app.route('/api/wishlist/bulk-remove', methods=['POST'])
def bulk_remove_wishlist():
    from flask import session
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Please sign in to access this feature."}), 401
    
    data = request.get_json()
    product_hashes = data.get('product_hashes', [])
    
    if not product_hashes or not isinstance(product_hashes, list):
        return jsonify({"success": False, "message": "Please select at least one product to remove."}), 400
    
    if len(product_hashes) == 0:
        return jsonify({"success": False, "message": "Please select one or more products to remove from your wishlist."}), 400
    
    user_id = session['user_id']
    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "message": "Database connection error."}), 500
    
    try:
        cur = conn.cursor()
        # Delete alerts first
        placeholders = ','.join(['%s'] * len(product_hashes))
        cur.execute(
            f"DELETE FROM alerts WHERE product_hash IN ({placeholders}) AND user_id = %s",
            tuple(product_hashes) + (user_id,)
        )
        # Then delete from wishlist
        cur.execute(
            f"DELETE FROM wishlist WHERE product_hash IN ({placeholders}) AND user_id = %s",
            tuple(product_hashes) + (user_id,)
        )
        conn.commit()
        deleted_count = cur.rowcount
        
        return jsonify({
            "success": True, 
            "message": f"Successfully removed {deleted_count} product(s) and associated alerts."
        }), 200
            
    except Exception as e:
        print(f"Error bulk removing from wishlist: {e}")
        return jsonify({"success": False, "message": "We encountered an issue while removing products. Please try again."}), 500
    finally:
        if conn: conn.close()

# --- API ENDPOINT TO CHECK TRACKED STATUS ---
@app.route('/api/wishlist/check', methods=['POST'])
def check_tracked_status():
    from flask import session
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Please sign in to access this feature."}), 401
    
    data = request.get_json()
    product_hashes = data.get('product_hashes', [])
    
    if not product_hashes or not isinstance(product_hashes, list):
        return jsonify({"success": False, "message": "Please provide product information to check status."}), 400
    
    user_id = session['user_id']
    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "message": "Database connection error."}), 500
    
    try:
        cur = conn.cursor()
        placeholders = ','.join(['%s'] * len(product_hashes))
        cur.execute(
            f"SELECT product_hash FROM wishlist WHERE product_hash IN ({placeholders}) AND user_id = %s",
            tuple(product_hashes) + (user_id,)
        )
        tracked_hashes = {row[0] for row in cur.fetchall()}
        
        # Return a mapping of product_hash -> is_tracked
        status_map = {hash_val: hash_val in tracked_hashes for hash_val in product_hashes}
        
        return jsonify({
            "success": True,
            "tracked_status": status_map
        }), 200
            
    except Exception as e:
        print(f"Error checking tracked status: {e}")
        return jsonify({"success": False, "message": "We encountered an issue while checking product status. Please try again."}), 500
    finally:
        if conn: conn.close()

# --- API ENDPOINT TO REFRESH/UPDATE PRICES ---
@app.route('/api/prices/refresh', methods=['POST'])
def refresh_prices():
    from flask import session
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Please sign in to access this feature."}), 401
    
    data = request.get_json()
    product_hashes = data.get('product_hashes', [])
    
    user_id = session['user_id']
    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "message": "Database connection error."}), 500
    
    try:
        cur = conn.cursor(dictionary=True)
        updated_count = 0
        
        if product_hashes and len(product_hashes) > 0:
            # Update specific products
            placeholders = ','.join(['%s'] * len(product_hashes))
            cur.execute(
                f"SELECT product_hash, current_price FROM wishlist WHERE product_hash IN ({placeholders}) AND user_id = %s",
                tuple(product_hashes) + (user_id,)
            )
            products = cur.fetchall()
        else:
            # Update all user's products
            cur.execute(
                "SELECT product_hash, current_price FROM wishlist WHERE user_id = %s",
                (user_id,)
            )
            products = cur.fetchall()
        
        for product in products:
            product_hash = product['product_hash']
            # Get latest price from price_history
            cur.execute(
                'SELECT price FROM price_history WHERE product_hash = %s ORDER BY history_id DESC LIMIT 1',
                (product_hash,)
            )
            latest_price_row = cur.fetchone()
            if latest_price_row and latest_price_row.get('price'):
                latest_price = float(latest_price_row['price'])
                # Update wishlist current_price if different
                if product['current_price'] != latest_price:
                    cur.execute(
                        'UPDATE wishlist SET current_price = %s WHERE product_hash = %s AND user_id = %s',
                        (latest_price, product_hash, user_id)
                    )
                    updated_count += 1
        
        conn.commit()
        return jsonify({
            "success": True,
            "message": f"Prices refreshed. {updated_count} product(s) updated.",
            "updated_count": updated_count
        }), 200
            
    except Exception as e:
        print(f"Error refreshing prices: {e}")
        return jsonify({"success": False, "message": "We encountered an issue while refreshing prices. Please try again."}), 500
    finally:
        if conn: conn.close()

@app.route('/api/alerts/send-email', methods=['POST', 'GET'])
def send_alerts_email():
    from flask import session
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Please sign in to access this feature."}), 401
    
    user_id = session['user_id']
    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "message": "We're experiencing technical difficulties. Please try again in a few moments."}), 500
    
    try:
        cur = conn.cursor(dictionary=True)
        
        # Get user email
        cur.execute("SELECT email, full_name FROM users WHERE id = %s", (user_id,))
        user = cur.fetchone()
        if not user:
            return jsonify({"success": False, "message": "User not found."}), 404
        
        to_email = user['email']
        user_name = user['full_name'] or 'User'
        
        # Get all alerts for the user (FIX: include product_url)
        cur.execute("""
            SELECT a.id, a.product_name, a.product_hash, a.product_url, a.target_price, a.current_price, 
                   a.created_at, a.notified, a.notified_at,
                   (SELECT price FROM price_history WHERE product_hash = a.product_hash ORDER BY history_id DESC LIMIT 1) as latest_price
            FROM alerts a
            WHERE a.user_id = %s
            ORDER BY a.created_at DESC
        """, (user_id,))
        
        alerts = cur.fetchall()
        
        if not alerts:
            return jsonify({"success": True, "message": "No alerts to send."}), 200
        
        # Build email body
        email_body = f"Hi {user_name},\n\n"
        email_body += "Here are all your active price alerts:\n\n"
        email_body += "=" * 60 + "\n\n"
        
        for alert in alerts:
            latest_price = alert['latest_price'] if alert['latest_price'] else alert['current_price']
            status = "TRIGGERED" if alert['notified'] else "ACTIVE"
            price_status = ""
            if latest_price:
                if latest_price <= float(alert['target_price']):
                    price_status = f"✓ Price reached! Current: Rs.{latest_price:.2f}"
                else:
                    price_status = f"Current: Rs.{latest_price:.2f} (Target: Rs.{alert['target_price']:.2f})"
            else:
                price_status = "Price not available"
            
            email_body += f"Product: {alert['product_name']}\n"
            email_body += f"Status: {status}\n"
            email_body += f"Target Price: Rs.{alert['target_price']:.2f}\n"
            email_body += f"{price_status}\n"
            email_body += f"Created: {alert['created_at'].strftime('%Y-%m-%d %H:%M') if alert['created_at'] else 'N/A'}\n"
            if alert['notified_at']:
                email_body += f"Notified: {alert['notified_at'].strftime('%Y-%m-%d %H:%M')}\n"
            # FIX: Use product_url instead of product_hash
            product_url = alert.get('product_url') or (alert.get('product_hash') if (alert.get('product_hash', '').startswith('http://') or alert.get('product_hash', '').startswith('https://')) else None)
            link_text = product_url if product_url else 'Product link not available'
            email_body += f"Product Link: {link_text}\n"
            email_body += "\n" + "-" * 60 + "\n\n"
        
        email_body += "\nThank you for using PriceAI!\n"
        email_body += "You can view and manage your alerts in the dashboard.\n"
        
        subject = f"Your Price Alerts Summary - {len(alerts)} Alert(s)"
        
        # Send email
        email_sent = send_email_notification(to_email, subject, email_body)
        
        if email_sent:
            return jsonify({"success": True, "message": "Alert details email sent successfully."}), 200
        else:
            return jsonify({"success": False, "message": "Failed to send email. SMTP may not be configured."}), 500
        
    except Exception as e:
        print(f"Error sending alerts email: {e}")
        return jsonify({"success": False, "message": "We encountered an issue while sending the email. Please try again."}), 500
    finally:
        if conn: conn.close()

# --- API ENDPOINT TO VIEW WISHLIST ---
@app.route('/api/wishlist/view', methods=['GET'])
def view_wishlist():
    from flask import session
    
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Please sign in to access this feature."}), 401
    
    user_id = session['user_id']
    conn = get_db_connection()
    if conn is None: return jsonify({"success": False, "message": "DB error."}), 500
    
    try:
        # Fetch results as dictionaries
        cur = conn.cursor(dictionary=True) 
        
        # Select all relevant columns from the wishlist table
        sql = """
            SELECT product_hash, product_name, current_price, image_src, date_added
            FROM wishlist 
            WHERE user_id = %s
            ORDER BY date_added DESC
        """
        cur.execute(sql, (user_id,))
        products = cur.fetchall()
        
        # Format the products
        formatted_products = []
        for product in products:
            formatted_products.append({
                "product_hash": product['product_hash'],
                "name": product['product_name'],
                "price": f"Rs.{product['current_price']:.2f}",
                "image": product['image_src'],
                "date_added": product['date_added'].strftime('%Y-%m-%d')
            })

        return jsonify({
            "success": True, 
            "message": f"Fetched {len(products)} items.",
            "products": formatted_products
        }), 200
        
    except Exception as e:
        print(f"Error fetching wishlist: {e}")
        return jsonify({"success": False, "message": "We encountered an issue while loading your wishlist. Please try again."}), 500
        
    finally:
        if conn: conn.close()


# --- ADMIN ROUTES ---

# --- ADMIN LOGIN ROUTE (Plain-Text Comparison) ---
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET':
        return render_template('admin_login.html')
    
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "Database connection failed"}), 500
    
    try:
        # We fetch results as a dictionary to easily check the username
        cur = conn.cursor(dictionary=True)
        
        # This query checks both username and plain-text password at once
        query = "SELECT * FROM admins WHERE username = %s AND password = %s"
        cur.execute(query, (username, password))
        admin = cur.fetchone()
        
        if admin:
            # Successful login: set the admin session
            session['admin_logged_in'] = True
            session['admin_user'] = admin['username']
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "message": "Invalid credentials"}), 401
            
    except Exception as e:
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500
    finally:
        conn.close()

# --- ADMIN DASHBOARD PROTECTION ---
@app.route('/admin')
def admin_dashboard():
    # Only allow access if the admin_logged_in flag is set in the session
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    return render_template('admin_dashboard.html')

# --- ADMIN LOGOUT ---
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_user', None)
    return redirect('/')

    
# --- API ENDPOINT TO REMOVE FROM WISHLIST ---
@app.route('/api/wishlist/remove', methods=['POST'])
def remove_from_wishlist():
    from flask import session
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Please sign in to access this feature."}), 401
    
    data = request.get_json()
    product_hash = data.get('product_hash')
    
    if not product_hash:
        return jsonify({"success": False, "message": "Please select a product to remove from your wishlist."}), 400
    
    user_id = session['user_id']
    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "message": "We're experiencing technical difficulties. Please try again in a few moments."}), 500
    
    try:
        cur = conn.cursor()
        # FIX: Also delete associated alerts when removing from wishlist (prevent orphaned alerts)
        cur.execute(
            "DELETE FROM alerts WHERE user_id = %s AND product_hash = %s",
            (user_id, product_hash)
        )
        # Delete from wishlist
        cur.execute(
            "DELETE FROM wishlist WHERE user_id = %s AND product_hash = %s",
            (user_id, product_hash)
        )
        conn.commit()
        
        if cur.rowcount > 0:
            return jsonify({"success": True, "message": "Product removed from your wishlist successfully."}), 200
        else:
            return jsonify({"success": False, "message": "This product is not in your wishlist."}), 404
            
    except Exception as e:
        print(f"Error removing from wishlist: {e}")
        return jsonify({"success": False, "message": "We encountered an issue while removing the product. Please try again."}), 500
    finally:
        if conn: conn.close()

# --- API ENDPOINT FOR USER STATUS (Dashboard counts) ---
@app.route('/api/user/status', methods=['GET'])
def get_user_status():
    from flask import session
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Please sign in to access this feature."}), 401
    
    user_id = session['user_id']
    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "message": "We're experiencing technical difficulties. Please try again in a few moments."}), 500
    
    try:
        cur = conn.cursor(dictionary=True)
        
        # Get wishlist count
        cur.execute("SELECT COUNT(*) as count FROM wishlist WHERE user_id = %s", (user_id,))
        wishlist_result = cur.fetchone()
        tracking_count = wishlist_result['count'] if wishlist_result else 0
        
        # Get active alerts count (not notified yet)
        cur.execute("SELECT COUNT(*) as count FROM alerts WHERE user_id = %s AND notified = 0", (user_id,))
        alerts_result = cur.fetchone()
        active_alerts = alerts_result['count'] if alerts_result else 0
        
        # Get notified/dropped alerts count
        cur.execute("SELECT COUNT(*) as count FROM alerts WHERE user_id = %s AND notified = 1", (user_id,))
        notified_result = cur.fetchone()
        dropped_alerts = notified_result['count'] if notified_result else 0
        
        return jsonify({
            "success": True,
            "status": {
                "tracking_count": tracking_count,
                "active_alerts": active_alerts,
                "dropped_alerts": dropped_alerts,  # Count of price drops
                "savings": "0.00"  # Placeholder for future implementation
            }
        }), 200
        
    except Exception as e:
        print(f"Error getting user status: {e}")
        return jsonify({"success": False, "message": "We encountered an issue while loading your dashboard status. Please try again."}), 500
    finally:
        if conn: conn.close()


@app.route('/api/submit_query', methods=['POST'])
def submit_query():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    message = data.get('message')

    # Basic validation
    if not name or not email or not message:
        return jsonify({"success": False, "message": "All fields are required."}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "Database connection failed."}), 500

    try:
        cur = conn.cursor(dictionary=True)
        
        # --- 1. RESTRICTION: Check if email exists in users table ---
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        user_exists = cur.fetchone()
        
        if not user_exists:
            # Block the request if the email is not a registered user
            return jsonify({
                "success": False, 
                "message": "Access Denied: Only registered users can submit queries. Please sign up first."
            }), 403

        # --- 2. PROCEED: Insert the query if user is found ---
        query = "INSERT INTO queries (name, email, message) VALUES (%s, %s, %s)"
        cur.execute(query, (name, email, message))
        conn.commit()
        
        return jsonify({"success": True, "message": "Query submitted successfully!"}), 200

    except Exception as e:
        print(f"Server Error in submit_query: {e}") # This prints to your terminal for debugging
        return jsonify({"success": False, "message": f"Server Error: {str(e)}"}), 500
    finally:
        conn.close()

@app.route('/api/admin/queries', methods=['GET'])
def admin_list_queries():
    if not session.get('admin_logged_in'):
        return jsonify({"success": False, "message": "Admin not logged in."}), 401

    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "message": "We're experiencing technical difficulties. Please try again in a few moments."}), 500

    try:
        cur = conn.cursor(dictionary=True)
        cur.execute('SELECT id, name, email, message, status, admin_reply, replied_at, created_at FROM queries ORDER BY created_at DESC')
        rows = cur.fetchall()
        return jsonify({"success": True, "queries": rows}), 200
    except Exception as e:
        print(f"Error fetching queries: {e}")
        return jsonify({"success": False, "message": "Server error."}), 500
    finally:
        if conn: conn.close()


@app.route('/api/admin/queries/<int:qid>/reply', methods=['POST'])
def admin_reply_query(qid):
    if not session.get('admin_logged_in'):
        return jsonify({"success": False, "message": "Admin not logged in."}), 401

    data = request.get_json() or {}
    reply = data.get('reply')
    if not reply:
        return jsonify({"success": False, "message": "Reply text required."}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "message": "We're experiencing technical difficulties. Please try again in a few moments."}), 500

    try:
        cur = conn.cursor()
        cur.execute('UPDATE queries SET admin_reply = %s, status = %s, replied_at = NOW() WHERE id = %s', (reply, 'replied', qid))
        conn.commit()
        return jsonify({"success": True, "message": "Replied."}), 200
    except Exception as e:
        print(f"Error replying to query: {e}")
        return jsonify({"success": False, "message": "Server error."}), 500
    finally:
        if conn: conn.close()


@app.route('/api/admin/users', methods=['GET'])
def admin_list_users():
    if not session.get('admin_logged_in'):
        return jsonify({"success": False, "message": "Admin not logged in."}), 401

    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "message": "We're experiencing technical difficulties. Please try again in a few moments."}), 500

    try:
        cur = conn.cursor(dictionary=True)
        cur.execute('SELECT id, full_name, email, registration_date FROM users ORDER BY registration_date DESC')
        rows = cur.fetchall()
        return jsonify({"success": True, "users": rows}), 200
    except Exception as e:
        print(f"Error fetching users: {e}")
        return jsonify({"success": False, "message": "Server error."}), 500
    finally:
        if conn: conn.close()


@app.route('/api/admin/users/<int:uid>/delete', methods=['POST'])
def admin_delete_user(uid):
    if not session.get('admin_logged_in'):
        return jsonify({"success": False, "message": "Admin not logged in."}), 401

    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "message": "We're experiencing technical difficulties. Please try again in a few moments."}), 500

    try:
        cur = conn.cursor()
        cur.execute('DELETE FROM users WHERE id = %s', (uid,))
        conn.commit()
        if cur.rowcount == 0:
            return jsonify({"success": False, "message": "User not found."}), 404
        return jsonify({"success": True, "message": "User deleted."}), 200
    except Exception as e:
        print(f"Error deleting user: {e}")
        return jsonify({"success": False, "message": "Server error."}), 500
    finally:
        if conn: conn.close()


@app.route('/api/user/details', methods=['GET'])
def get_user_details():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Please sign in to access this feature."}), 401

    user_id = session['user_id']
    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "message": "We're experiencing technical difficulties. Please try again in a few moments."}), 500

    try:
        cur = conn.cursor(dictionary=True)
        cur.execute('SELECT id, full_name, email, registration_date FROM users WHERE id = %s', (user_id,))
        user = cur.fetchone()
        if not user:
            return jsonify({"success": False, "message": "User not found."}), 404
        return jsonify({"success": True, "user": user}), 200
    except Exception as e:
        print(f"Error fetching user details: {e}")
        return jsonify({"success": False, "message": "Server error."}), 500
    finally:
        if conn: conn.close()


@app.route('/api/user/queries', methods=['GET'])
def get_user_queries():
    if 'email' not in session:
        return jsonify({"success": False, "message": "Please sign in to access this feature."}), 401

    email = session['email']
    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "message": "We're experiencing technical difficulties. Please try again in a few moments."}), 500

    try:
        cur = conn.cursor(dictionary=True)
        cur.execute('SELECT id, name, email, message, status, admin_reply, replied_at, created_at FROM queries WHERE email = %s ORDER BY created_at DESC', (email,))
        rows = cur.fetchall()
        return jsonify({"success": True, "queries": rows}), 200
    except Exception as e:
        print(f"Error fetching user queries: {e}")
        return jsonify({"success": False, "message": "Server error."}), 500
    finally:
        if conn: conn.close()

@app.route('/api/price-history', methods=['GET'])
def get_price_history():
    """Get price history for a product by product_hash or URL"""
    product_hash = request.args.get('product_hash')
    
    if not product_hash:
        return jsonify({"success": False, "message": "product_hash parameter required."}), 400
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "message": "We're experiencing technical difficulties. Please try again in a few moments."}), 500
    
    try:
        cur = conn.cursor(dictionary=True)
        
        # Try to find by exact match first (could be URL or hash)
        cur.execute("""
            SELECT price, price_source, timestamp 
            FROM price_history 
            WHERE product_hash = %s 
            ORDER BY timestamp ASC
        """, (product_hash,))
        
        history = cur.fetchall()
        
        # If no results and it looks like a URL, try generating hash and searching
        if not history and (product_hash.startswith('http://') or product_hash.startswith('https://')):
            # Try to find by URL pattern (partial match)
            cur.execute("""
                SELECT price, price_source, timestamp 
                FROM price_history 
                WHERE product_hash LIKE %s 
                ORDER BY timestamp ASC
            """, (f'%{product_hash[:100]}%',))
            history = cur.fetchall()
        
        # Format the data for Chart.js
        formatted_history = []
        for record in history:
            formatted_history.append({
                "price": float(record['price']),
                "source": record['price_source'] or 'Unknown',
                "timestamp": record['timestamp'].strftime('%Y-%m-%d %H:%M') if record['timestamp'] else '',
                "date": record['timestamp'].strftime('%Y-%m-%d') if record['timestamp'] else '',
                "time": record['timestamp'].strftime('%H:%M') if record['timestamp'] else ''
            })
        
        return jsonify({
            "success": True,
            "history": formatted_history
        }), 200
        
    except Exception as e:
        print(f"Error fetching price history: {e}")
        return jsonify({"success": False, "message": "Server error fetching price history."}), 500
    finally:
        if conn: conn.close()

# --- NEW ROUTE: SERVE WISHLIST.HTML ---
@app.route('/wishlist')
def serve_wishlist_page():
    """Serves the dedicated wishlist HTML page."""
    # This route will require the user to be logged in, 
    # but the frontend JS will handle the actual data fetching and login check.
    return render_template('wishlist.html')

# --- NEW ROUTE: SERVE INDEX.HTML (Remains the same) ---
@app.route('/')
def serve_index():
    return render_template('index.html')

@app.route('/dashboard-view')
def serve_dashboard_view():
    return render_template('index.html')
if __name__ == '__main__':
    # Load model and data once when the app starts
    load_ai_model_and_data()
    # Ensure alerts table exists
    try:
        ensure_alerts_table()
    except Exception as e:
        print(f"Could not ensure alerts table: {e}")
    # Ensure queries table exists
    try:
        ensure_queries_table()
    except Exception as e:
        print(f"Could not ensure queries table: {e}")
    # Start background thread to monitor alerts
    try:
        t = threading.Thread(target=check_alerts_loop, kwargs={'poll_interval': 60}, daemon=True)
        t.start()
    except Exception as e:
        print(f"Could not start alerts checker thread: {e}")
    
    # Run Flask
    app.run(debug=True)
