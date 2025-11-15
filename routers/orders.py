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
            SELECT ci.product_id, ci.quantity, p.remaining_units, p.name
            FROM cart_items ci
            JOIN products p ON ci.product_id = p.id
            WHERE ci.cart_id = ?
        """, (payload.cart_id,))
        cart_items = cur.fetchall()

        for item in cart_items:
            if item["remaining_units"] < item["quantity"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Not enough stock for {item['name']}. Only {item['remaining_units']} left."
                )
            cur.execute("""
                UPDATE products
                SET remaining_units = remaining_units - ?
                WHERE id = ?
            """, (item["quantity"], item["product_id"]))

        
        cur.execute("""
            INSERT INTO orders (user_id, cart_id, total_amount, order_status)
            VALUES (?, ?, ?, ?)
        """, (payload.user_id, payload.cart_id, total_amount, "pending"))

        

        
        cur.execute("""
            SELECT o.id, o.user_id, o.cart_id, o.total_amount, o.order_status, o.order_time,
                   u.email AS user_email
            FROM orders o
            JOIN users u ON o.user_id = u.id
            WHERE o.id = last_insert_rowid()
        """)
        order = cur.fetchone()

        if not order:
            raise HTTPException(status_code=500, detail="Order creation failed")

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
            GROUP BY o.cart_id        
            ORDER BY o.order_time DESC
        """)
        return cur.fetchall()



@router.get("/details/{user_id}")
def get_order_details(user_id: int):
    with get_db() as conn:
        cur = conn.cursor()

        
        cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cur.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        
        cur.execute("""
            SELECT o.id AS order_id, o.total_amount, o.order_status, o.order_time,
                   o.cart_id
            FROM orders o
            WHERE o.user_id = ?
            GROUP BY o.cart_id        
            ORDER BY o.order_time DESC
        """, (user_id,))
        orders = cur.fetchall()

        if not orders:
            raise HTTPException(status_code=404, detail="No orders found for this user")

        
        detailed_orders = []
        for order in orders:
            cur.execute("""
                SELECT p.id, p.name, p.price, ci.quantity
                FROM cart_items ci
                JOIN products p ON ci.product_id = p.id
                WHERE ci.cart_id = ?
            """, (order["cart_id"],))
            products = cur.fetchall()

            detailed_orders.append({
                "order_id": order["order_id"],
                "cart_id": order["cart_id"],
                "total_amount": order["total_amount"],
                "order_status": order["order_status"],
                "order_time": order["order_time"],
                "products": products
            })

        return detailed_orders


# @router.get("/user/{user_id}", response_model=list[schemas.OrderOut])
# def get_user_orders(user_id: int):
#     with get_db() as conn:
#         cur = conn.cursor()

        
#         cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
#         user = cur.fetchone()
#         if not user:
#             raise HTTPException(status_code=404, detail="User not found")

        
#         cur.execute("""
#             SELECT o.id, o.user_id, o.cart_id, o.total_amount, o.order_status, o.order_time,
#                    u.email AS user_email
#             FROM orders o
#             JOIN users u ON o.user_id = u.id
#             WHERE o.user_id = ?
#             ORDER BY o.order_time DESC
#         """, (user_id,))
#         orders = cur.fetchall()

#         if not orders:
#             raise HTTPException(status_code=404, detail="No orders found for this user")

#         return orders