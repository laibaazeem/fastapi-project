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

        
        cur.execute("SELECT * FROM products WHERE id = ?", (payload.product_id,))
        product = cur.fetchone()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        
        cur.execute(
            "INSERT INTO orders (user_id, product_id) VALUES (?, ?)",
            (payload.user_id, payload.product_id)
        )

        
        cur.execute("""
            SELECT o.id, o.user_id, o.product_id, o.timestamp,
                   u.email AS user_email,
                   p.name AS product_name,
                   p.price AS product_price
            FROM orders o
            JOIN users u ON o.user_id = u.id
            JOIN products p ON o.product_id = p.id
            WHERE o.id = last_insert_rowid()
        """)
        order = cur.fetchone()
        return order


@router.get("/", response_model=list[schemas.OrderOut])
def list_orders():
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT o.id, o.user_id, o.product_id, o.timestamp,
                   u.email AS user_email,
                   p.name AS product_name,
                   p.price AS product_price
            FROM orders o
            JOIN users u ON o.user_id = u.id
            JOIN products p ON o.product_id = p.id
            ORDER BY o.timestamp DESC
        """)
        return cur.fetchall()
