from itertools import product
from typing import Optional
from starlette.requests import Request
from fastapi.background import BackgroundTasks

from fastapi import FastAPI
import fastapi
import requests, time

from fastapi.middleware.cors import CORSMiddleware

from redis_om import get_redis_connection, HashModel

app = FastAPI()


# Libera consumo para o frontend comunicar com nossa aplicação
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_methods=['*'],
    allow_headers=['*'],

)

# Database config
redis = get_redis_connection(
    host="redis-13847.c56.east-us.azure.cloud.redislabs.com",
    port=13847,
    password="ltV5q4LNdbfM5KC0susNntvcm2oNnr3I",
    decode_responses=True
)


class Order(HashModel):
    product_id: str
    price: float
    fee: float
    total: float
    quantity: int
    status: str #PENDING, COMPLETED, REFUNDED.
    
    class Meta:
        database = redis

@app.get('/orders/{pk}')        
def get(pk: str):
    return Order.get(pk)
        
@app.post('/orders')
async def create(request: Request, background_tasks: BackgroundTasks): #id, quantity
    body = await request.json()
    
    req = requests.get('http://localhost:8000/products/%s' % body['id'])
    
    product = req.json()
    
    order = Order(
        product_id = body['id'],
        price=product['price'],
        fee=0.2 * product['price'],
        total=1.2 * product['price'],
        quantity=body['quantity'],
        status='pending'
    )
    
    order.save()
    
    background_tasks.add_task(order_completed, order)
    
    return order

def order_completed(order: Order):
    time.sleep(5)
    order.status = 'completed'
    order.save()