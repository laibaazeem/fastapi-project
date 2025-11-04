from fastapi import APIRouter, HTTPException
from database import get_db
import schemas

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=schemas.OrderOut)
def make_order(payload: schemas.OrderCreate):
    with get_db() as conn:
        cur = conn.cursor()

        
        cur.execute("SELECT * FROM users WHERE id = ?", (payload.user_id,))
        user = cur.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        
        cur.execute("SELECT * FROM carts WHERE id = ?", (payload.cart_id,))
        cart = cur.fetchone()
        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found")

        
        cur.execute("""
            SELECT SUM(p.price * ci.quantity) AS total
            FROM cart_items ci
            JOIN products p ON ci.product_id = p.id
            WHERE ci.cart_id = ?
        """, (payload.cart_id,))
        row = cur.fetchone()
        total_amount = row["total"] if row and row["total"] else 0


        
        cur.execute("""
            INSERT INTO orders (user_id, cart_id, total_amount)
            VALUES (?, ?, ?)
        """, (payload.user_id, payload.cart_id, total_amount))

        conn.commit()

        
        cur.execute("""
            SELECT o.id, o.user_id, o.cart_id, o.total_amount, o.order_status, o.order_time,
                   u.email AS user_email
            FROM orders o
            JOIN users u ON o.user_id = u.id
            WHERE o.id = last_insert_rowid()
        """)
        order = cur.fetchone()
        return order



@router.get("/", response_model=list[schemas.OrderOut])
def list_orders():
    with get_db() as conn:
        cur = conn.cursor()

        cur.execute("""
            SELECT o.id, o.user_id, o.cart_id, o.total_amount, o.order_status, o.order_time,
                   u.email AS user_email
            FROM orders o
            JOIN users u ON o.user_id = u.id
            ORDER BY o.order_time DESC
        """)
        return cur.fetchall()

@router.get("/user/{user_id}", response_model=list[schemas.OrderOut])
def get_user_orders(user_id: int):
    with get_db() as conn:
        cur = conn.cursor()

        
        cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cur.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        
        cur.execute("""
            SELECT o.id, o.user_id, o.cart_id, o.total_amount, o.order_status, o.order_time,
                   u.email AS user_email
            FROM orders o
            JOIN users u ON o.user_id = u.id
            WHERE o.user_id = ?
            ORDER BY o.order_time DESC
        """, (user_id,))
        orders = cur.fetchall()

        if not orders:
            raise HTTPException(status_code=404, detail="No orders found for this user")

        return orders
