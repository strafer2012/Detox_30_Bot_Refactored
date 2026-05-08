import asyncio
from aiohttp import web
from loguru import logger

async def health_check(request):
    return web.json_response({
        "status": "healthy",
        "service": "detox30-bot",
        "timestamp": asyncio.get_event_loop().time()
    })

async def start_health_server(port: int = 8080):
    app = web.Application()
    app.router.add_get("/health", health_check)
    app.router.add_get("/metrics", health_check)  # Placeholder for Prometheus
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    
    logger.info(f"Health check server started on port {port}")
    
    # Keep the server running
    while True:
        await asyncio.sleep(3600)