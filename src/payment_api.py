from fastapi import FastAPI

app = FastAPI(title="Retail Payment Source API")

payments = [
    {
        "payment_id": "PAY-001",
        "order_id": "ORD-1001",
        "amount": "200.00",
        "currency": "USD",
        "status": "CAPTURED",
    },
    {
        "payment_id": "PAY-002",
        "order_id": "ORD-1002",
        "amount": "70.00",
        "currency": "USD",
        "status": "CAPTURED",
    },
]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/payments")
def get_payments():
    return {"payments": payments}