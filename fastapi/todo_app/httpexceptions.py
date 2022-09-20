from fastapi import HTTPException


def error_404():
    return HTTPException(status_code=404, detail="Item not found", headers={"X-Header_error": "Item could not be found"})