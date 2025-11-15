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

        
        for item in payload.products:
            pid = item.product_id
            quantity = item.quantity

            cur.execute("SELECT id, remaining_units FROM products WHERE id = ?", (pid,))
            product = cur.fetchone()
            if not product:
                raise HTTPException(status_code=400, detail=f"Product {pid} not found")
            if product["remaining_units"] < quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Not enough stock for product {pid}. Only {product['remaining_units']} left."
                )

            cur.execute(
                "INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (?, ?, ?)",
                (cart_id, pid, quantity)
            )

        
        cur.execute("SELECT * FROM carts WHERE id = ?", (cart_id,))
        cart = cur.fetchone()
        if not cart:
            raise HTTPException(status_code=500, detail="Cart not found after creation")

        
        cur.execute("""
            SELECT p.id, p.name, p.price, ci.quantity
            FROM cart_items ci
            JOIN products p ON ci.product_id = p.id
            WHERE ci.cart_id = ?
        """, (cart_id,))
        products = cur.fetchall() or []

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

        # Get cart
        cur.execute("SELECT * FROM carts WHERE id = ?", (cart_id,))
        cart = cur.fetchone()
        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found")

        if cart["is_checked_out"]:
            raise HTTPException(status_code=400, detail="Cart already checked out")

        # Get cart items and check stock
        cur.execute("""
            SELECT ci.product_id, ci.quantity, p.remaining_units, p.price, p.name
            FROM cart_items ci
            JOIN products p ON ci.product_id = p.id
            WHERE ci.cart_id = ?
        """, (cart_id,))
        items = cur.fetchall()
        if not items:
            raise HTTPException(status_code=400, detail="Cart is empty")

        total = 0
        for item in items:
            if item["remaining_units"] < item["quantity"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Not enough stock for {item['name']}. Only {item['remaining_units']} left."
                )
            total += item["price"] * item["quantity"]

        # Reduce stock
        for item in items:
            cur.execute("""
                UPDATE products
                SET remaining_units = remaining_units - ?
                WHERE id = ?
            """, (item["quantity"], item["product_id"]))

        # Create order
        cur.execute("""
            INSERT INTO orders (user_id, cart_id, total_amount, order_status)
            VALUES (?, ?, ?, ?)
        """, (cart["user_id"], cart_id, total, 'confirmed'))
        order_id = cur.lastrowid

        # Update cart status
        cur.execute("UPDATE carts SET is_checked_out = 1 WHERE id = ?", (cart_id,))

        # Fetch order
        cur.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        order = cur.fetchone()
        if not order:
            raise HTTPException(status_code=500, detail="Order not found after creation")

        return {
            "order_id": order["id"],
            "user_id": order["user_id"],
            "cart_id": order["cart_id"],
            "total_amount": order["total_amount"],
            "order_status": order["order_status"],
            "order_time": order["order_time"]
        }


@router.get("/user/{user_id}", response_model=list[schemas.CartOut])
def get_cart_details(user_id: int):
    with get_db() as conn:
        cur = conn.cursor()

        # Check if user exists
        cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="User not found")

        # Get carts
        cur.execute("SELECT * FROM carts WHERE user_id = ?", (user_id,))
        carts = cur.fetchall()
        if not carts:
            raise HTTPException(status_code=404, detail="No carts found for this user")

        user_carts = []
        for cart in carts:
            cur.execute("""
                SELECT p.id, p.name, p.price, ci.quantity
                FROM cart_items ci
                JOIN products p ON ci.product_id = p.id
                WHERE ci.cart_id = ?
            """, (cart["id"],))
            products = cur.fetchall() or []

            user_carts.append({
                "id": cart["id"],
                "user_id": cart["user_id"],
                "created_at": cart["created_at"],
                "products": products
            })

        return user_carts
