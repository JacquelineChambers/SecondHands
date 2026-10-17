"""Start the local dashboard service."""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "secondhands.api.app:app", host="127.0.0.1", port=8765, ws_max_size=8192, ws_max_queue=1
    )
