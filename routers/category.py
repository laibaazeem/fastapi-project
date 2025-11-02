# routers/category.py
from fastapi import APIRouter, HTTPException
from database import get_db
import schemas

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.post("/", response_model=schemas.CategoryOut)
def create_category(payload: schemas.CategoryCreate):
    with get_db() as conn:
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO categories (name, description) VALUES (?, ?)",
                        (payload.name, payload.description))
        except Exception as e:
            raise HTTPException(status_code=400, detail="Category already exists")
        cur.execute("SELECT * FROM categories WHERE id = last_insert_rowid()")
        return cur.fetchone()

@router.get("/", response_model=list[schemas.CategoryOut])
def get_categories():
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM categories")
        return cur.fetchall()

@router.get("/{category_id}", response_model=schemas.CategoryOut)
def get_category(category_id: int):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM categories WHERE id = ?", (category_id,))
        cat = cur.fetchone()
        if not cat:
            raise HTTPException(status_code=404, detail="Category not found")
        return cat

@router.put("/{category_id}", response_model=schemas.CategoryOut)
def update_category(category_id: int, payload: schemas.CategoryUpdate):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM categories WHERE id = ?", (category_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Category not found")

        updates, params = [], []
        if payload.name: updates.append("name = ?"); params.append(payload.name)
        if payload.description: updates.append("description = ?"); params.append(payload.description)
        if updates:
            params.append(category_id)
            cur.execute(f"UPDATE categories SET {', '.join(updates)} WHERE id = ?", tuple(params))
        cur.execute("SELECT * FROM categories WHERE id = ?", (category_id,))
        return cur.fetchone()

@router.delete("/{category_id}")
def delete_category(category_id: int):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Category not found")
        return {"message": "Category deleted"}
