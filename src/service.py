import asyncio
import json
import logging
import time
from collections import defaultdict
from datetime import datetime
from typing import List

import aio_pika

from src.report_generator import generate_report_fast
from src.settings import RABBIT_HOST, REPORT_QUEUE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def generate_report_callback(message: aio_pika.IncomingMessage):
    async with message.process():
        logger.info(
            "Received new task with correlation ID: %s", message.correlation_id
        )

        task_received = datetime.now()
        start_time = time.time()

        data = json.loads(message.body)

        phone_numbers: List[int] = data["phones"]

        logger.info(f"Received phone numbers: {phone_numbers}")
        logger.info("Generating report...")
        stats: defaultdict[int, dict] = await generate_report_fast(
            phone_numbers=phone_numbers
        )
        result = {
            'correlation_id': message.correlation_id,
            'status': 'Complete',
            'task_received': task_received.strftime("%Y-%m-%d %H:%M:%S"),
            'from': 'report_service',
            'to': 'client',
            'data': [],
            'total_duration': time.time() - start_time
        }

        for phone_number, phone_stats in stats.items():
            result_stats = phone_stats.copy()
            result_stats['phone'] = phone_number
            result['data'].append(result_stats)

        logger.info("Report generated!")

        # Publish the message directly to the routing key (queue)
        # mentioned in the 'reply_to' attribute.
        await message.channel.basic_publish(
            exchange='',  # Use an empty string for the default exchange
            routing_key=message.reply_to,
            body=json.dumps(result).encode()
        )
        logger.info(
            "Sent response to queue: %s with correlation ID: %s",
            message.reply_to,
            message.correlation_id
        )


async def main():
    logger.info("Initializing report generation service...")

    connection = await aio_pika.connect_robust(f"amqp://{RABBIT_HOST}")

    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue(REPORT_QUEUE)

        await queue.consume(generate_report_callback)

        logger.info(
            "Report generation service started. Awaiting tasks..."
        )
        await asyncio.Event().wait()  # Keep the coroutine running indefinitely.


if __name__ == "__main__":
    asyncio.run(main())
