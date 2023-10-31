import asyncio
import json
import logging
import uuid

import aio_pika

from src.settings import RABBIT_HOST, REPORT_QUEUE

# Setup basic logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class TaskSender:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.callback_queue = None
        self.response = None
        self.corr_id = None

    async def initialize(self):
        logging.info("Initializing TaskSender...")

        self.connection = await aio_pika.connect_robust(f"amqp://{RABBIT_HOST}")
        self.channel = await self.connection.channel()

        # Declare a unique queue for replies
        self.callback_queue = await self.channel.declare_queue(
            "", exclusive=True)

        # Consume messages from the reply queue
        await self.callback_queue.consume(self.on_response)

        logging.info("TaskSender initialized.")

    async def on_response(self, message: aio_pika.IncomingMessage):
        logging.info("Received response from queue: %s", message.body)
        async with message.process():
            if self.corr_id == message.correlation_id:
                self.response = message.body
                logging.info("Received response matching correlation ID.")

    async def call(self, task_data):
        self.response = None
        self.corr_id = task_data.pop("correlation_id", uuid.uuid4().hex)
        logging.info(f"Sending task with correlation ID: {self.corr_id}. Task data: {task_data}")

        # Send task data with 'reply_to' set to the callback queue
        # and a unique correlation ID
        await self.channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(task_data).encode(),
                correlation_id=self.corr_id,
                reply_to=self.callback_queue,
            ),
            routing_key=REPORT_QUEUE,
        )

        # Wait for a reply in the callback queue
        while self.response is None:
            await asyncio.sleep(0.1)  # This acts as a simple non-blocking wait loop.
        return self.response


async def main():
    task_sender = TaskSender()
    await task_sender.initialize()

    # Create a list of sample tasks
    sample_tasks = [
        {"correlation_id": uuid.uuid4().hex, "phones": [1, 2, 3, 4, 5]},
        {"correlation_id": uuid.uuid4().hex, "phones": [6, 7, 8, 9, 10]},
        {"correlation_id": uuid.uuid4().hex, "phones": [11, 12, 13, 14, 15]},
        {"correlation_id": uuid.uuid4().hex, "phones": [16, 17, 18, 19, 20]},
    ]

    # Send tasks concurrently
    responses = await asyncio.gather(
        *(task_sender.call(task) for task in sample_tasks))

    for raw_response in responses:
        response = json.loads(raw_response.decode())  # Deserialize the response
        print("Received reply:", response)  # Display the result

    logging.info("Tasks completed.")


if __name__ == "__main__":
    asyncio.run(main())
