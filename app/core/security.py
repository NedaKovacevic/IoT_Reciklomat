from typing import Optional
from fastapi import Header, HTTPException



def require_operator(x_role: str = Header(default="")):
    if x_role.lower() != "operator":
        raise HTTPException(status_code=403, detail="Operator role required")
    return True