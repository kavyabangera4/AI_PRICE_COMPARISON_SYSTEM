# Functional & Workflow Flaws Analysis

## 🔴 CRITICAL FUNCTIONAL ISSUES

### 1. **No Duplicate Alert Prevention**
**Issue:** Users can create unlimited alerts for the same product
```python
# Line 989: No check for existing alerts
cur.execute("INSERT INTO alerts ...")
```
**Problem:**
- User can create 10 alerts for the same product with different target prices
- Clutters database and UI
- Wastes resources in background checker
- Confusing user experience

**Fix:** Check for existing alert before inserting:
```python
# Check if alert already exists
cur.execute("SELECT id FROM alerts WHERE user_id = %s AND product_hash = %s AND notified = 0", 
            (user_id, product_hash))
if cur.fetchone():
    return jsonify({"success": False, "message": "Alert already exists for this product. Update existing alert instead."}), 409
```

### 2. **Orphaned Alerts When Wishlist Removed**
**Issue:** Removing product from wishlist doesn't check/remove alerts
**Problem:**
- User removes product from wishlist
- Alert still exists and continues checking
- Price history may stop updating (if only tracked via wishlist)
- Alert becomes "zombie" - checking for product no longer tracked

**Fix:** Add cascade logic or warning:
```python
# When removing from wishlist, check for alerts
cur.execute("SELECT COUNT(*) FROM alerts WHERE user_id = %s AND product_hash = %s AND notified = 0", 
            (user_id, product_hash))
alert_count = cur.fetchone()[0]
if alert_count > 0:
    # Option 1: Delete alerts too
    # Option 2: Warn user about active alerts
```

### 3. **No Target Price Validation**
**Issue:** No validation that target price is reasonable
**Problem:**
- User can set target price = 0 or negative
- User can set target price higher than current price (defeats purpose)
- No warning for unrealistic prices

**Fix:** Add validation:
```python
if target_price_val <= 0:
    return jsonify({"success": False, "message": "Target price must be greater than 0."}), 400
if current_price and target_price_val > current_price:
    # Warn but allow (maybe user expects price to go up then down)
    pass
```

### 4. **Price History Duplicates**
**Issue:** Every wishlist add creates new price_history entry, even if price unchanged
**Problem:**
- Same price logged multiple times
- Unnecessary database bloat
- Price graphs show flat lines with duplicate points

**Fix:** Check last price before inserting:
```python
cur.execute("SELECT price FROM price_history WHERE product_hash = %s ORDER BY history_id DESC LIMIT 1", 
            (product_hash,))
last_price = cur.fetchone()
if not last_price or float(last_price['price']) != current_price:
    # Only insert if price changed
    cur.execute("INSERT INTO price_history ...")
```

### 5. **Frontend State Not Synced with Backend**
**Issue:** Heart icon state (tracked/untracked) not loaded from server
**Problem:**
- User adds product to wishlist
- Refreshes page or navigates away
- Heart icon shows as untracked (gray) even though product is in wishlist
- User doesn't know which products are already tracked

**Fix:** Load tracked products on page load:
```javascript
async function loadTrackedProducts() {
    const response = await fetch('/api/wishlist/view');
    const data = await response.json();
    if (data.success) {
        const trackedHashes = new Set(data.products.map(p => p.product_hash));
        // Mark all tracked products' heart icons as tracked
        document.querySelectorAll('.wishlist-btn').forEach(btn => {
            const productIndex = btn.getAttribute('data-product-index');
            const product = window.productDataStore[productIndex];
            if (product && trackedHashes.has(generateHash(product))) {
                btn.classList.add('tracked');
            }
        });
    }
}
```

### 6. **Alert Checker Uses Wrong Column**
**Issue:** Line 791 uses `ORDER BY id DESC` but should use `history_id`
```python
cur.execute('SELECT price FROM price_history WHERE product_hash = %s ORDER BY id DESC LIMIT 1', (product_hash,))
```
**Problem:**
- `price_history` table uses `history_id` as primary key, not `id`
- Query might fail or return wrong results
- Should be `ORDER BY history_id DESC`

**Fix:**
```python
cur.execute('SELECT price FROM price_history WHERE product_hash = %s ORDER BY history_id DESC LIMIT 1', (product_hash,))
```

### 7. **No Price Update Mechanism**
**Issue:** Prices only updated when user adds to wishlist
**Problem:**
- If user creates alert without adding to wishlist, price never updates
- Alert checker relies on price_history, but nothing populates it
- Current price stays at initial value forever

**Fix:** Add periodic price scraping or manual refresh:
```python
# Option 1: When checking alerts, try to fetch current price from source
# Option 2: Add "Refresh Price" button for each alert
# Option 3: Require wishlist addition before alert creation
```

### 8. **Race Condition in Alert Checker**
**Issue:** Multiple database operations without transaction
**Problem:**
- Line 804: Updates current_price
- Line 814: Marks as notified
- If error occurs between, data can be inconsistent
- Multiple threads could process same alert

**Fix:** Use transactions and add unique constraint:
```python
try:
    conn.start_transaction()
    # All operations here
    conn.commit()
except:
    conn.rollback()
```

### 9. **No Alert Update/Edit Functionality**
**Issue:** Can't modify existing alert target price
**Problem:**
- User sets wrong target price
- Must delete and recreate alert
- Loses creation date and history

**Fix:** Add update endpoint:
```python
@app.route('/api/alerts/update', methods=['POST'])
def update_alert():
    # Update target_price for existing alert
```

### 10. **Session Expiry Not Handled**
**Issue:** No session timeout or refresh mechanism
**Problem:**
- User stays logged in indefinitely
- Session might expire on server but frontend doesn't know
- User gets errors when trying to use features
- No graceful logout on session expiry

**Fix:** Add session validation and auto-refresh:
```python
# Check session expiry before each protected route
# Frontend: Check session status periodically
```

## 🟡 WORKFLOW ISSUES

### 11. **Inconsistent Product Hash Generation**
**Issue:** Hash used for grouping might differ from hash used for storage
**Problem:**
- Search results group products by normalized name
- But alerts/wishlist use hash from URL+name+brand+source
- Same product might have different hashes if URL format differs
- Products won't match between search and wishlist

**Fix:** Use consistent hashing strategy everywhere

### 12. **No Bulk Operations**
**Issue:** Can't delete multiple alerts/wishlist items at once
**Problem:**
- User with 50 tracked items must delete one by one
- Time-consuming and frustrating

**Fix:** Add bulk delete endpoints

### 13. **Alert Email Uses Wrong Link**
**Issue:** Line 842 uses `product_hash` as link, not `product_url`
```python
body = f"...\n\nLink: {a.get('product_hash')}\n\n..."
```
**Problem:**
- Email contains hash string instead of clickable URL
- User can't easily access product

**Fix:** Use `product_url` or construct proper link

### 14. **No Price Change Notifications**
**Issue:** Only notifies when price drops below target
**Problem:**
- User might want to know if price increases significantly
- No way to track price trends via notifications

**Fix:** Add option for price change notifications (up/down)

### 15. **Wishlist "View History" Button Does Nothing**
**Issue:** Line 152-154 in wishlist.html - button has no functionality
```html
<a href="#" class="btn-view-deal">View History</a>
```
**Problem:**
- Button exists but doesn't do anything
- User expects to see price history graph
- Misleading UI

**Fix:** Implement price history modal or redirect

### 16. **No Search Result Persistence**
**Issue:** Search results lost on page refresh
**Problem:**
- User searches, finds product, navigates away
- Must search again to find same product
- Can't bookmark search results

**Fix:** Store search results in sessionStorage or URL params

### 17. **Alert Modal Doesn't Show Current Price**
**Issue:** Alert creation modal doesn't display current price
**Problem:**
- User doesn't know current price when setting target
- Must remember or guess
- Might set unrealistic target

**Fix:** Display current price in alert modal

### 18. **No Confirmation for Alert Deletion**
**Issue:** Alert deletion happens immediately without confirmation
**Problem:**
- Accidental clicks delete alerts
- No way to undo

**Fix:** Add confirmation dialog (already exists in code, but check if working)

### 19. **Dashboard Counts Not Real-Time**
**Issue:** Counts only update on page load or manual refresh
**Problem:**
- User adds item, count doesn't update immediately
- Must refresh page to see new count
- Confusing UX

**Fix:** Update counts after every add/remove operation

### 20. **No Error Recovery**
**Issue:** If background alert checker fails, no retry mechanism
**Problem:**
- One error stops entire loop
- Alerts stop being checked
- Users never get notified

**Fix:** Add retry logic and error recovery

## 🟢 UX/UI ISSUES

### 21. **No Loading States**
**Issue:** No visual feedback during API calls
**Problem:**
- User clicks button, nothing happens
- Doesn't know if request is processing
- Might click multiple times

**Fix:** Add loading spinners and disable buttons during requests

### 22. **Generic Error Messages**
**Issue:** Errors like "Server error" don't help user
**Problem:**
- User doesn't know what went wrong
- Can't take corrective action
- Frustrating experience

**Fix:** Provide specific, actionable error messages

### 23. **No Empty States**
**Issue:** Empty lists show generic messages
**Problem:**
- No guidance on what to do next
- Missing helpful tips or CTAs

**Fix:** Add helpful empty state messages with actions

### 24. **Price Formatting Inconsistency**
**Issue:** Prices displayed in different formats
**Problem:**
- Some show "Rs.600.00", others "600"
- Inconsistent user experience

**Fix:** Standardize price formatting function

## 📊 DATA INTEGRITY ISSUES

### 25. **No Foreign Key Constraints**
**Issue:** Can delete user but alerts/wishlist remain
**Problem:**
- Orphaned records in database
- Data inconsistency
- Potential errors when querying

**Fix:** Add foreign key constraints with CASCADE

### 26. **No Data Validation on Product Hash**
**Issue:** Product hash can be empty or invalid
**Problem:**
- Alerts created with empty hash
- Can't match products later
- Breaks functionality

**Fix:** Validate hash before insertion

### 27. **Price History Has No Unique Constraint**
**Issue:** Same price+hash+timestamp can be inserted multiple times
**Problem:**
- Duplicate entries
- Inflated database size
- Incorrect price trends

**Fix:** Add unique constraint or check before insert

## 🔧 QUICK FIXES (High Impact, Low Effort)

1. **Fix alert duplicate prevention** - 30 minutes
2. **Fix price_history ORDER BY** - 5 minutes  
3. **Add target price validation** - 15 minutes
4. **Fix email link** - 5 minutes
5. **Add wishlist "View History" functionality** - 1 hour
6. **Load tracked products on page load** - 2 hours
7. **Add confirmation for alert deletion** - 10 minutes
8. **Update dashboard counts after operations** - 30 minutes

---

**Priority Order:**
1. Fix alert duplicate prevention (prevents data bloat)
2. Fix price_history query (prevents wrong data)
3. Load tracked state on page load (better UX)
4. Add target price validation (prevents bad data)
5. Fix orphaned alerts issue (data integrity)

