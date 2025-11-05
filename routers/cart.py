from fastapi import APIRouter, HTTPException
from database import get_db
import schemas

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.post("/", response_model=schemas.CartOut)
def add_to_cart(payload: schemas.CartCreate):
    with get_db() as conn:
        cur = conn.cursor()

        
        cur.execute("SELECT * FROM users WHERE id = ?", (payload.user_id,))
        user = cur.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        
        cur.execute("INSERT INTO carts (user_id) VALUES (?)", (payload.user_id,))
        cart_id = cur.lastrowid

        
        for pid in payload.product_ids:
            cur.execute("SELECT id FROM products WHERE id = ?", (pid,))
            if not cur.fetchone():
                raise HTTPException(status_code=400, detail=f"Product {pid} not found")
            cur.execute("INSERT INTO cart_items (cart_id, product_id) VALUES (?, ?)", (cart_id, pid))

        
        cur.execute("""
            SELECT p.id, p.name, p.price
            FROM cart_items ci
            JOIN products p ON ci.product_id = p.id
            WHERE ci.cart_id = ?
        """, (cart_id,))
        products = cur.fetchall()

        cur.execute("SELECT * FROM carts WHERE id = ?", (cart_id,))
        cart = cur.fetchone()
        return {
            "id": cart["id"],
            "user_id": cart["user_id"],
            "created_at": cart["created_at"],
            "products": products
        }



@router.post("/checkout/{cart_id}", response_model=schemas.CheckoutOut)
def checkout_cart(cart_id: int):
    with get_db() as conn:
        cur = conn.cursor()

        
        cur.execute("SELECT * FROM carts WHERE id = ?", (cart_id,))
        cart = cur.fetchone()
        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found")

        if cart["is_checked_out"]:
            raise HTTPException(status_code=400, detail="Cart already checked out")

        
        cur.execute("""
            SELECT SUM(p.price) AS total
            FROM cart_items ci
            JOIN products p ON ci.product_id = p.id
            WHERE ci.cart_id = ?
        """, (cart_id,))
        total_result = cur.fetchone()
        total = total_result["total"] if total_result["total"] is not None else 0

        
        cur.execute("""
            INSERT INTO orders (user_id, cart_id, total_amount, order_status)
            VALUES (?, ?, ?,?)
        """, (cart["user_id"], cart_id, total, 'confirmed'))
        order_id = cur.lastrowid

        
        cur.execute("UPDATE carts SET is_checked_out = 1 WHERE id = ?", (cart_id,))

        
        cur.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        order = cur.fetchone()

        return {
            "order_id": order["id"],
            "user_id": order["user_id"],
            "cart_id": order["cart_id"],
            "total_amount": order["total_amount"],
            "order_status": order["order_status"],
            "order_time": order["order_time"]
        }


#✅ NEW ENDPOINT: Get all cart details by user_id
@router.get("/user/{user_id}", response_model=list[schemas.CartOut])
def get_cart_details(user_id: int):
    with get_db() as conn:
        cur = conn.cursor()

        # Check if user exists
        cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="User not found")

        # Get all carts of user
        cur.execute("SELECT * FROM carts WHERE user_id = ?", (user_id,))
        carts = cur.fetchall()
        if not carts:
            raise HTTPException(status_code=404, detail="No carts found for this user")

        user_carts = []
        for cart in carts:
            # Get products in each cart
            cur.execute("""
                SELECT p.id, p.name, p.price
                FROM cart_items ci
                JOIN products p ON ci.product_id = p.id
                WHERE ci.cart_id = ?
            """, (cart["id"],))
            products = cur.fetchall()

            user_carts.append({
                "id": cart["id"],
                "user_id": cart["user_id"],
                "created_at": cart["created_at"],
                "products": products
            })

        return user_carts
    

# @router.get("/user/{user_id}", response_model=list[schemas.CartOut])
# def get_user_carts(user_id: int):
#     with get_db() as conn:
#         cur = conn.cursor()

        
#         cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
#         user = cur.fetchone()
#         if not user:
#             raise HTTPException(status_code=404, detail="User not found")

        
#         cur.execute("SELECT * FROM carts WHERE user_id = ?", (user_id,))
#         carts = cur.fetchall()
#         if not carts:
#             raise HTTPException(status_code=404, detail="No carts found for this user")

#         results = []
#         for cart in carts:
            
#             cur.execute("""
#                 SELECT p.id, p.name, p.price
#                 FROM cart_items ci
#                 JOIN products p ON ci.product_id = p.id
#                 WHERE ci.cart_id = ?
#             """, (cart["id"],))
#             products = cur.fetchall()

#             results.append({
#                 "id": cart["id"],
#                 "user_id": cart["user_id"],
#                 "created_at": cart["created_at"],
#                 "products": products
#             })

#         return results

    