import uvicorn
import asyncio
from app.plugins import AskarStorage, TractionController

if __name__ == "__main__":
    asyncio.run(AskarStorage().provision())
    # asyncio.run(TractionController().provision_tdw())
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        # workers=4,
    )
