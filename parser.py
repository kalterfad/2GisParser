import asyncio
import logging

import aiohttp

from core.prop import DOUBLE_GIS_API_KEY
from database.crud import get_reviews_count, add_reviews_count, update_reviews_count, add_new_review
from database.schemas import ReviewsCountSchema, ReviewsSchema

logging.basicConfig(filename='parser.log', level=logging.INFO, format='%(levelname)s %(asctime)s %(message)s')


class Parser:
    _headers = {
        'authority': 'public-api.reviews.2gis.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'ru,en;q=0.9',
        'origin': 'https://2gis.ru',
        'referer': 'https://2gis.ru/',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102", "Yandex";v="22"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/102.0.5005.134 YaBrowser/22.7.1.806 Yowser/2.5 Safari/537.36',
    }
    # Адреса филиалов Вкусно и точка
    _addresses = ['2393065583018885', '2393066583092767', '2393066583119255']
    _DOUBLE_GIS_URL = 'https://public-api.reviews.2gis.com/2.0/branches/{' \
                     'place_id}/reviews?limit=50&is_advertiser=false&fields=meta.providers,' \
                     'meta.branch_rating,meta.branch_reviews_count,meta.total_count,reviews.hiding_reason,' \
                     'reviews.is_verified&without_my_first_review=false&rated=true&sort_by=date_edited&key={' \
                     'APIKEY}&locale=ru_RU'
    _tasks = []
    __session: aiohttp.ClientSession

    async def main(self):
        logging.info('Start parsing reviews')
        async with aiohttp.ClientSession() as self.__session:
            for i in self._addresses:
                self._tasks.append(asyncio.create_task(self._start(i)))

            await asyncio.gather(*self._tasks)
        logging.info('End of reviews parsing')

    async def _start(self, place_id: str):
        reviews = await self._get(self._DOUBLE_GIS_URL.format(place_id=place_id, APIKEY=DOUBLE_GIS_API_KEY))
        count = await get_reviews_count(place=ReviewsCountSchema(**{
            'place_id': place_id,
            'reviews_count': reviews['meta']['branch_reviews_count']
        }))

        if count.reviews_count == 0:
            logging.info(f'Add review counter to place: {place_id}')
            await add_reviews_count(ReviewsCountSchema(**{
                'place_id': place_id,
                'reviews_count': reviews['meta']['branch_reviews_count']
            }))

            async for collect_result in self._collect_results(reviews):
                await add_new_review(ReviewsSchema(**collect_result))

        elif count.reviews_count != reviews['meta']['branch_reviews_count']:
            logging.info(f'Update review counter to place: {place_id}')
            await update_reviews_count(ReviewsCountSchema(**{
                'place_id': place_id,
                'reviews_count': reviews['meta']['branch_reviews_count']
            }))

            async for collect_result in self._collect_results(reviews):
                await add_new_review(ReviewsSchema(**collect_result))

    async def _get(self, url: str):
        async with self.__session.get(url, headers=self._headers) as response:
            return await response.json()

    async def _collect_results(self, reviews):
        """ Формирует отзывы и отправляет запросы на следующие страницы отзывов"""
        async for formed_response in self._generate_response(reviews['reviews']):
            if formed_response is not None:
                yield formed_response

        async for next_review in self._get_next_reviews(reviews):
            yield next_review

    async def _get_next_reviews(self, response):
        """Отправляет запросы на следующие страницы отзывов"""
        while 'next_link' in response['meta']:
            response = await self._get(response['meta']['next_link'])

            async for formed_response in self._generate_response(response['reviews']):
                if formed_response is not None:
                    yield formed_response

    @staticmethod
    async def _generate_response(response):
        for item in response:
            yield {
                'id': item['id'],
                'user': (item['user']['name']),
                'date_created': item['date_created'],
                'rating': item['rating'],
                'text': item['text'],
            }
