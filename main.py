
from fastapi import FastAPI
from database import init_db
from routers import products, category, auth

app = FastAPI(title="Products & Categories ")

@app.on_event("startup")
def startup_event():
    init_db()

# Register routers
app.include_router(auth.router)
app.include_router(category.router)
app.include_router(products.router)
