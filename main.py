from fastapi import FastAPI, HTTPException, status
import database
import schemas

app = FastAPI(title="FastAPI")


@app.post("/products", response_model=schemas.ProductResponse)
def create_product(product: schemas.ProductCreate):
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO products (name, description, price, quantity) VALUES (?, ?, ?, ?)",
        (product.name, product.description, product.price, product.quantity),
    )
    conn.commit()
    product_id = cursor.lastrowid
    conn.close()
    return schemas.ProductResponse(id=product_id, **product.dict())



@app.get("/products", response_model=list[schemas.ProductResponse])
def get_products():
    conn = database.get_db_connection()
    rows = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    return [schemas.ProductResponse(**dict(row)) for row in rows]



@app.get("/products/{product_id}", response_model=schemas.ProductResponse)
def get_product(product_id: int):
    conn = database.get_db_connection()
    row = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Product not found")
    return schemas.ProductResponse(**dict(row))



@app.put("/products/{product_id}", response_model=schemas.ProductResponse)
def update_product(product_id: int, product: schemas.ProductCreate):
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE products SET name=?, description=?, price=?, quantity=? WHERE id=?",
        (product.name, product.description, product.price, product.quantity, product_id),
    )
    conn.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    conn.close()
    return schemas.ProductResponse(id=product_id, **product.dict())



@app.patch("/products/{product_id}", response_model=schemas.ProductResponse)
def patch_product(product_id: int, product: schemas.ProductUpdate):
    conn = database.get_db_connection()
    cursor = conn.cursor()
    existing = conn.execute("SELECT * FROM products WHERE id=?", (product_id,)).fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="Product not found")

    data = dict(existing)
    updated = product.dict(exclude_unset=True)
    data.update(updated)

    cursor.execute(
        "UPDATE products SET name=?, description=?, price=?, quantity=? WHERE id=?",
        (data["name"], data["description"], data["price"], data["quantity"], product_id),
    )
    conn.commit()
    conn.close()
    return schemas.ProductResponse(**data)



@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int):
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
    conn.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    conn.close()
    return
