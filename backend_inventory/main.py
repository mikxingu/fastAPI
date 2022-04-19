from itertools import product
from typing import Optional

from fastapi import FastAPI
import fastapi
from fastapi.middleware.cors import CORSMiddleware

from redis_om import get_redis_connection, HashModel

app = FastAPI()


#Libera consumo para o frontend comunicar com nossa aplicação
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_methods=['*'],
    allow_headers=['*'],
    
)

redis = get_redis_connection(
    host="redis-13847.c56.east-us.azure.cloud.redislabs.com",
    port=13847,
    password="ltV5q4LNdbfM5KC0susNntvcm2oNnr3I",
    decode_responses=True
)

class Product(HashModel):
    name: str
    price: float
    quantity: int
    
    class Meta:
        database = redis


@app.get("/")
def read_root():
    return {"Fast API Crash Course"}


@app.get('/products')
def all():
    return [format(pk) for pk in Product.all_pks()]

def format(pk: str):
    product = Product.get(pk)
    
    return {
        'id': product.pk,
        'name': product.name,
        'price': product.price,
        'quantity': product.quantity
    }
@app.get('/products/{pk}')
def get(pk: str):
    return Product.get(pk)

@app.delete('/products/{pk}')
def delete(pk: str):
    return Product.delete(pk)

@app.post('/products')
def create(product: Product):
    return product.save()
