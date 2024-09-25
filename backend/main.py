import uvicorn
import asyncio
from app.plugins import AskarStorage, AskarWallet

if __name__ == "__main__":
    # asyncio.run(AskarStorage().provision(recreate=True))
    asyncio.run(AskarWallet().provision(recreate=True))
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        # workers=4,
    )
