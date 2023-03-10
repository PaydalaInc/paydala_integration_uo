from http.client import HTTPException
# from urllib.request import Request
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from signedcreds import *
import json
import logging
from fastapi import FastAPI, Header, HTTPException
from hashlib import sha256
import hmac

API_SECRET_KEY = "your_api_secret_key_here"

app = FastAPI()

# Initialize a logger object
logger = logging.getLogger("my_logger")

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(content={"error": exc.detail}, status_code=exc.status_code)

@app.get('/')
def hello():
    return {'message': 'Hello, World!'}


@app.post('/getSignedCreds')
async def get_signed_creds(request: Request):
    payload_bytes = await request.body()
    if len(payload_bytes) == 0:
        raise HTTPException(400, "Missing or empty payload")
    payload_str = payload_bytes.decode("utf-8")
    print("payload = ",payload_str) 
    try:
        x = json.loads(payload_str)
    except Exception as e:
        logger.error(f"Error loading JSON: {e}")
        raise HTTPException(400, "Malformed JSON payload")
    creds = SignedCreds(payload_str)
    return {"creds":creds.creds, "signature" : creds.signature }
    # return json.dumps(creds, cls=SignedCredsEncoder)




@app.post("/webhookConfirmation")
async def webhook_confirmation(payload: dict, X_Request_Signature: str = Header(None)):
    if X_Request_Signature is None:
        raise HTTPException(status_code=400, detail="X-Request-Signature header is missing")
    
    # Create the signature using the API_SECRET_KEY and the payload
    signature = hmac.new(API_SECRET_KEY.encode(), str(payload).encode(), sha256).hexdigest()

    # Compare the signature in the X-Request-Signature header with the calculated signature
    if not hmac.compare_digest(signature, X_Request_Signature):
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # If the signature is valid, print the payload
    print(payload)
    
    return {"message": "Webhook confirmed"}




if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)

