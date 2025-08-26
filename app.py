from fastapi import FastAPI

# Import all the routers
from src.api import documents_router, items_router, associations_router, ai_suggestions_router

app = FastAPI(
    title="FMEA-CP-OI Analysis Platform API",
    description="API for uploading, editing, and analyzing FMEA and CP documents.",
    version="1.0.0"
)

@app.get("/", tags=["Root"])
def read_root():
    """
    A simple health check endpoint to confirm the server is running.
    """
    return {"status": "ok", "message": "Welcome to the FMEA-CP-OI Analysis Platform API"}

# Include all routers with a common prefix
api_prefix = "/api/v1"
app.include_router(documents_router.router, prefix=api_prefix)
app.include_router(items_router.router, prefix=api_prefix)
app.include_router(associations_router.router, prefix=api_prefix)
app.include_router(ai_suggestions_router.router, prefix=api_prefix)

# To run this application:
# 1. Ensure your .env file is correctly configured with database and DIFY credentials.
# 2. Install all dependencies: pip install -r requirements.txt
# 3. Run the database schema script (database_schema.sql) in your 'db_A060' MySQL database.
# 4. Run the server using uvicorn: uvicorn app:app --reload

# After running, you can access the interactive API documentation at:
# http://127.0.0.1:8000/docs
