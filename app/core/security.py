from typing import Optional
from fastapi import Header, HTTPException

def require_operator(x_role: Optional[str] = Header(default=None)):
    if x_role != "operator":
        raise HTTPException(status_code=403, detail="Operator role required")
