"""API for RiskLens Quantitative Terminal.
Exposes app from app.py for backward compatibility.
"""
from app import *

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=False)
