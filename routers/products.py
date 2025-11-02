# routers/products.py
from fastapi import APIRouter, HTTPException
from database import get_db
import schemas

router = APIRouter(prefix="/products", tags=["Products"])

def get_category_by_id(conn, cat_id: int):
    cur = conn.cursor()
    cur.execute("SELECT * FROM categories WHERE id = ?", (cat_id,))
    return cur.fetchone()

@router.post("/", response_model=schemas.ProductOut)
def create_product(payload: schemas.ProductCreate):
    with get_db() as conn:
        cur = conn.cursor()
        category = get_category_by_id(conn, payload.category_id)
        if not category:
            raise HTTPException(status_code=400, detail="category did not exist")

        cur.execute(
            "INSERT INTO products (name, description, price, category_id) VALUES (?, ?, ?, ?)",
            (payload.name, payload.description, payload.price, payload.category_id)
        )
        cur.execute("SELECT * FROM products WHERE id = last_insert_rowid()")
        product = cur.fetchone()
        return {
            "id": product["id"],
            "name": product["name"],
            "description": product["description"],
            "price": product["price"],
            "category": category
        }

@router.get("/", response_model=list[schemas.ProductOut])
def list_products():
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT p.*, c.id as cat_id, c.name as cat_name, c.description as cat_desc
            FROM products p
            JOIN categories c ON p.category_id = c.id
        """)
        rows = cur.fetchall()
        return [
            {
                "id": r["id"],
                "name": r["name"],
                "description": r["description"],
                "price": r["price"],
                "category": {
                    "id": r["cat_id"],
                    "name": r["cat_name"],
                    "description": r["cat_desc"]
                }
            } for r in rows
        ]
