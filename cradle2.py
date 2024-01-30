import uvicorn
from fastapi import FastAPI



class CustomServer(uvicorn.Server):
    def __init__(self, port, host="127.0.0.1"):
        self.port = port
        self.host = host
        pass
    
    async def start_server(self):
        app = FastAPI()
        @app.get("/")
        async def read_root():
            return {"Hello": "World"}
        config = uvicorn.Config(app=app, host=self.host, port=self.port, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()

# Given the nature of asynchronous code, it needs to be run under an event loop.
async def main():  
    server = CustomServer(8000)
    await server.start_server()

# Run the server
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())