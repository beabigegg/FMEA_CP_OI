from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import dependencies for startup event
from src.database import database, models
from src.security import get_password_hash
from src.database.config import settings

# Import all the routers
from src.api import (
    documents_router,
    items_router,
    fe_router,
    auth_router, # Added auth router
    ai_suggestions_router, # Added AI suggestions router
    export_router, # Added export router
    associations_router, # Added associations router
)

app = FastAPI(
    title="FMEA-CP-OI Analysis Platform API",
    description="API for uploading, editing, and analyzing FMEA and CP documents.",
    version="1.0.0"
)

# --- CORS Middleware ---
# Allow all origins for development purposes. For production, you should
# restrict this to your frontend's actual domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Startup Event ---
@app.on_event("startup")
def on_startup():
    """
    Create the first admin user on startup if no users exist.
    Requires ADMIN_USERNAME and ADMIN_PASSWORD to be set in the .env file.
    """
    db = next(database.get_db())
    try:
        user_count = db.query(models.User).count()
        if user_count == 0:
            print("No users found in the database. Creating initial admin user...")
            admin_user = settings.ADMIN_USERNAME
            admin_pass = settings.ADMIN_PASSWORD
            if not admin_user or not admin_pass:
                print("FATAL: ADMIN_USERNAME and ADMIN_PASSWORD must be set in .env to create the first user.")
                return

            hashed_password = get_password_hash(admin_pass)
            initial_admin = models.User(
                username=admin_user,
                hashed_password=hashed_password,
                role='admin' # The first user is always an admin
            )
            db.add(initial_admin)
            db.commit()
            print(f"Admin user '{admin_user}' created successfully.")
        else:
            print(f"{user_count} user(s) found. Skipping initial user creation.")
    finally:
        db.close()


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
# Register the Failure Effects router to expose FE options endpoints
app.include_router(fe_router.router, prefix=api_prefix)

# Register the new routers
app.include_router(auth_router.router) # Auth router has its own prefix
app.include_router(ai_suggestions_router.router, prefix=api_prefix)
app.include_router(export_router.router, prefix=api_prefix)
app.include_router(associations_router.router, prefix=api_prefix)

# To run this application:
# 1. Ensure your .env file is correctly configured with database and DIFY credentials.
# 2. Install all dependencies: pip install -r requirements.txt
# 3. Run the database schema script (database_schema.sql) in your 'db_A060' MySQL database.
# 4. Run the server using uvicorn: uvicorn app:app --reload

# After running, you can access the interactive API documentation at:
# http://127.0.0.1:8000/docs