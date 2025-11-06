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
            raise HTTPException(status_code=400, detail="Category does not exist")

        cur.execute(
            """
            INSERT INTO products (name, description, price, category_id, total_units, remaining_units)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                payload.name,
                payload.description,
                payload.price,
                payload.category_id,
                payload.total_units,
                payload.remaining_units,
            ),
        )
        cur.execute("SELECT * FROM products WHERE id = last_insert_rowid()")
        product = cur.fetchone()
        return {
            "id": product["id"],
            "name": product["name"],
            "description": product["description"],
            "price": product["price"],
            "category": schemas.CategoryOut(
                id=category["id"],
                name=category["name"],
                description=category["description"]
            ),
            "stock_status": "Out of Stock" if product["remaining_units"] == 0 else "Available"
        }


@router.get("/", response_model=list[schemas.ProductOut])
def list_products():
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT p.*, c.id AS cat_id, c.name AS cat_name, c.description AS cat_desc
            FROM products p
            JOIN categories c ON p.category_id = c.id
        """)
        rows = cur.fetchall()

        products = []
        for r in rows:
            products.append({
                "id": r["id"],
                "name": r["name"],
                "description": r["description"],
                "price": r["price"],
                "category": schemas.CategoryOut(
                    id=r["cat_id"],
                    name=r["cat_name"],
                    description=r["cat_desc"]
                ),
                "stock_status": "Out of Stock" if r["remaining_units"] == 0 else "Available"
            })

        return products
