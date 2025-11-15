from fastapi import FastAPI
from database import init_db
from routers import products, category, auth , orders , cart
from dotenv import load_dotenv
load_dotenv()


app = FastAPI(title="Products & Categories ")

@app.on_event("startup")
def startup_event():
    init_db()

app.include_router(auth.router)
app.include_router(category.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(cart.router)


