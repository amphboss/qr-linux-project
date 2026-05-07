from fastapi import HTTPException, Header

API_KEY = "mysecretkey"


def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")
