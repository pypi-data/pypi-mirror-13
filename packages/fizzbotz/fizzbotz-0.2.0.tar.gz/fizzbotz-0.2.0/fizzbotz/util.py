#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import random
import string

import aiohttp


async def get_markup(url):
    response = await aiohttp.get(url)
    markup = await response.text()
    return markup


class ImageQueue:
    _imgur_url = 'https://i.imgur.com/{}.png'
    _removed_url = 'https://i.imgur.com/removed.png'
    _valid_characters = string.ascii_letters + string.digits
    _id_length = 5

    def __init__(self, queue_size=20):
        self.queue_size = queue_size
        self.queue = asyncio.Queue(maxsize=self.queue_size)

    async def _enqueue_valid_image(self):
        while True:
            image_id = ''.join(random.choice(self._valid_characters) for _ in range(self._id_length))
            image_url = self._imgur_url.format(image_id)

            r = None
            try:
                r = await aiohttp.get(image_url)
            except aiohttp.errors.ClientResponseError:
                continue
            finally:
                if r is not None:
                    r.close()

            if r.url != self._removed_url:
                self.queue.put_nowait(image_url)
                return

    async def populate(self):
        for _ in range(self.queue_size):
            await self._enqueue_valid_image()

    async def get_image(self):
        image = await self.queue.get()
        asyncio.ensure_future(self._enqueue_valid_image())
        return image
