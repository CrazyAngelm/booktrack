from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routers import users_router, catalog_router, favourites_router, reading_list_router
from exceptions import *
from core import engine, Base


load_dotenv()  # Load environmental variables

# Create the backend application
app = FastAPI()

# Allow all origins
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create the database tables
Base.metadata.create_all(bind=engine)
print("Tables created!")

# Include the routers
app.include_router(users_router)
app.include_router(catalog_router)
app.include_router(favourites_router)
app.include_router(reading_list_router)

# Add the exceptions handlers


# Define the root source
@app.get("/", tags=["Root"], status_code=200)
async def root():
    return {"message": "The BookTrack services are up!"}
