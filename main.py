from typing import Annotated
from fastapi import FastAPI, Path, Body

# Storage implementation. To replace storage strategies,
# see storage/base_storage
from storage.base_storage import storageInstance as storage

# Maximum length of user settings
MAX_SETTINGS_LENGTH = 100
# Minimum settings length. We won't story empty strings, the delete endpoint exists
# for removing data.
MIN_SETTINGS_LENGTH = 1

# User ids longer than this are considered invalid
MAX_USER_ID_LENGTH = 50
# User ids shorter than this are considered invalid
MIN_USER_ID_LENGTH = 3

app = FastAPI()

# Health check endpoint, useful for testing if app instances are running
# since APIs don't have a homepage or may otherwise require auth
@app.get("/health")
async def health():
    return {"Hello": "World"}

# GET /user_id
@app.get("/{user_id}")
async def get_user_settings(
    user_id: Annotated[
        str,
        Path(title="The user ID to return settings for",
             min_length=MIN_USER_ID_LENGTH,
             max_length=MAX_USER_ID_LENGTH)
    ]
):
    results = await storage.read(user_id)

    if results:
        return {'success': True, 'value': results}
    
    return {'success': False}

# PUT /user_id
@app.put("/{user_id}")
async def update_user_settings(
    user_id: Annotated[
        str,
        Path(title="Update settings for the given user ID",
             min_length=MIN_USER_ID_LENGTH,
             max_length=MAX_USER_ID_LENGTH)
    ],
    settings: Annotated[str, Body(
        min_length=MIN_SETTINGS_LENGTH,
        max_length=MAX_SETTINGS_LENGTH
    )]
):
    results = await storage.write(user_id, settings)
    return { 'success': results }

# DELETE /user_id
@app.delete("/{user_id}")
async def delete_user_settings(
    user_id: Annotated[
        str,
        Path(title="The user ID to delete settings for",
             min_length=MIN_USER_ID_LENGTH,
             max_length=MAX_USER_ID_LENGTH)
    ]
):
    results = await storage.delete(user_id)
    return { 'success': results }