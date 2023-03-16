import platform
from datetime import datetime, timedelta
import sys
from pprint import pprint
import aiohttp
import asyncio


def create_url(date):
    """ Створення url запиту в залежності від дати """

    day, month, year = date.strftime('%d %m %Y').split()
    return f'https://api.privatbank.ua/p24api/exchange_rates?json&date={day}.{month}.{year}'



async def main(n=1):
    if n > 10:
        n = 10

    # створення списку url за останні n днів
    urls = [create_url(datetime.now() - timedelta(days=day)) for day in range(n-1, -1, -1)]
    
    curr_list = []

    async with aiohttp.ClientSession() as session:
        for url in urls:
            exchange_rate_for_a_date = {}
            async with session.get(url) as response:
                result = await response.json()
                
                curr = {}
                for record in result['exchangeRate']:
                    
                    if record['currency'] == 'USD':
                        curr['USD'] = {
                            'sale': record['saleRate'], 
                            'purchase': record['purchaseRate']
                        }

                    elif record['currency'] == 'EUR':
                        curr["EUR"] = {
                            'sale': record['saleRate'], 
                            'purchase': record['purchaseRate']
                        }
                   
                    exchange_rate_for_a_date[result['date']] = curr
            curr_list.append(exchange_rate_for_a_date)
        return curr_list


if __name__ == "__main__":
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    try:
        n = int(sys.argv[1])
    except IndexError:
        n = 1
    r = asyncio.run(main(n))
    pprint(r)