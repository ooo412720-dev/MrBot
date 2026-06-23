# app/api/metrics.py

from fastapi import Response

from prometheus_client import (
    generate_latest
)


async def metrics():

    data = generate_latest()

    return Response(

        content=data,

        media_type="text/plain"
    )