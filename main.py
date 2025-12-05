#
# main.py
import logging
#import uvicorn
#from fastapi import FastAPI

#from app.api import router
#from app.logging_conf import setup_logging

#setup_logging()

#app = FastAPI(title="Evacuation Routing Service")
#app.include_router(router)

#if __name__ == "__main__":
 #   uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
# main.py
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api import router
from app.logging_conf import setup_logging

setup_logging()

app = FastAPI(title="Evacuation Routing Service")
app.include_router(router)

# NEW: serve static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

