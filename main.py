from fastapi import FastAPI
from furigana_utils import get_furigana

app = FastAPI()

# The home page, its only use is to tell
# if the server is running.
@app.get("/")
def index() -> str:
    return "The server is running!"

# Returns a JSON array of words with their
# corresponding readings.
@app.get("/furigana/{text}")
def furigana(text: str) -> str:
    return get_furigana(text)