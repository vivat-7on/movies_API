from contextlib import asynccontextmanager

import aio_pika
from fastapi import FastAPI
from notification.broker.settings import RabbitSettings

from .v1.events import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    rabbit_settings = RabbitSettings()

    connection = await aio_pika.connect_robust(rabbit_settings.dsn)
    channel = await connection.channel()

    await channel.declare_queue(
        "notifications",
        durable=True,
    )

    app.state.rabbit_connection = connection
    app.state.rabbit_channel = channel

    yield

    await connection.close()


app = FastAPI(lifespan=lifespan)

app.include_router(router=router, prefix="/api/v1/notification")


@app.get("/notification/health")
async def check_health():
    return {"status": "ok"}
