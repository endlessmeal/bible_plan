import httpx
from typing import Optional
from const import JUST_BIBLE_API_URL

class BibleAPI:

    def __init__(self, translation: str = 'rst'):
        self.translation = translation

    async def get_chapter(self, book: int, chapter: int) -> Optional[dict]:
        params = {
            'translation': self.translation,
            'book': book,
            'chapter': chapter
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(JUST_BIBLE_API_URL, params=params)
            if response.status_code == 200:
                return response.json()
            return None
