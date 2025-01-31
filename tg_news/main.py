"""Application for sending news from RSS feed to Telegram Channel."""

import asyncio
import json
import time
from datetime import datetime, timedelta
import os

import feedparser
import telegram


TG_TOKEN = os.getenv("TG_BOT_TOKEN")
CHECK_PERIOD_SECONDS = 30 * 60
NUM_WORKERS = 4
TASK_TIMEOUT_SECONDS = 10


async def handler(event, context):
    feeds = read_feed_config("feeds.json")
    await process_feeds(feeds)


def read_feed_config(path: str) -> list[dict]:
    """Read the feed json config file and return a list of feeds."""
    with open(path) as f:
        return json.load(f)


async def process_feeds(feeds: list[dict]) -> None:
    """Process all feeds."""
    queue = asyncio.Queue()
    for feed in feeds:
        queue.put_nowait(feed)
    tasks = []
    for i in range(NUM_WORKERS):
        task = asyncio.create_task(worker(queue))
        tasks.append(task)
    await queue.join()
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)


async def worker(queue):
    """Asincio worker function."""
    while True:
        feed = await queue.get()
        try:
            await asyncio.wait_for(
                process_feed(feed["url"], feed["chat_id"]),
                timeout=TASK_TIMEOUT_SECONDS
            )
        except asyncio.TimeoutError:
            pass
        finally:
            queue.task_done()


async def process_feed(feed_url: str, chat_id: str) -> None:
    """Read data from feed. Check if new articles available. Send new to Telegram."""
    feed = feedparser.parse(feed_url)
    if not feed.entries:
        return
    bot = telegram.Bot(token=TG_TOKEN)
    start_dt = datetime.now() - timedelta(seconds=CHECK_PERIOD_SECONDS)
    num_messages = 0
    for entry in feed.entries:
        if datetime.fromtimestamp(time.mktime(entry.published_parsed)) > start_dt:
            message = f"{entry.title}\n\n{entry.link}"
            await bot.sendMessage(chat_id=chat_id, text=message)
            num_messages += 1
        else:
            return


if __name__ == "__main__":
    feeds = read_feed_config("feeds.json")
    asyncio.run(process_feeds(feeds))
