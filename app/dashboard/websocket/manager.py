class ConnectionManager:

    def __init__(self):

        self.active_connections = []

    async def connect(
        self,
        websocket
    ):

        await websocket.accept()

        self.active_connections.append(
            websocket
        )

    def disconnect(
        self,
        websocket
    ):

        if websocket in self.active_connections:

            self.active_connections.remove(
                websocket
            )

    async def broadcast(
        self,
        payload
    ):

        disconnected = []

        for connection in self.active_connections:

            try:

                await connection.send_json(
                    payload
                )

            except Exception:

                disconnected.append(
                    connection
                )

        for connection in disconnected:

            self.disconnect(
                connection
            )