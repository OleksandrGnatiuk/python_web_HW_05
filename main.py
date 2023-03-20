import platform
from datetime import datetime, timedelta
import sys
import asyncio
import aiohttp
import json


def create_url(date):
    """ Створення url запиту в залежності від дати """

    day, month, year = date.strftime('%d %m %Y').split()
    return f'https://api.privatbank.ua/p24api/exchange_rates?json&date={day}.{month}.{year}'


async def get_exchange(n=None, lst=None):
    lst_curr = ['USD', 'EUR']
    if lst:
        lst_curr += lst

    if n > 10:
        n = 10

    # створення списку url за останні n днів
    urls = [create_url(datetime.now() - timedelta(days=day)) for day in range(n-1, -1, -1)]
    
    curr_list = []

    async with aiohttp.ClientSession() as session:
        for url in urls:
            exchange_rate_for_a_date = {}
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        result = await response.json()
                        curr = {}
                        for record in result['exchangeRate']:
                            if record['currency'] in lst_curr:
                                curr[record['currency']] = {
                                    'sale': record['saleRate'], 
                                    'purchase': record['purchaseRate']
                                }
                            exchange_rate_for_a_date[result['date']] = curr
                        curr_list.append(exchange_rate_for_a_date)
                    else:
                        print(f'Error status {response.status} for {url}')
            except aiohttp.ClientConnectionError as err:
                print(f'Connection error: {url}', str(err))

        exc = json.dumps(curr_list, ensure_ascii=False, indent=4)
        return exc


if __name__ == "__main__":
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    lst_curr = ['USD', 'EUR']
    try:
        n = int(sys.argv[1])
        if len(sys.argv) > 2:
            # якщо введено додаткові валюти, то добавляємо їх до спистку валют за замовчуванням
            lst_curr += sys.argv[2:]
    except IndexError:
        n = 1
    r = asyncio.run(get_exchange(n, lst_curr))
    print(r)
