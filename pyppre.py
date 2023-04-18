import asyncio
from pyppeteer import launch
from datetime import datetime


async def main(link: str):
    browser = await launch({
        'headless': False,
        'executablePath': '/usr/bin/microsoft-edge-stable'
    })

    page = await browser.newPage()
    await page.goto(link, {'timeout': 1000000})

    elements = await page.querySelectorAll('._1it5ivp')
    for element in elements:
        print(await page.evaluate('(element) => element.textContent', element))

    await browser.close()


if __name__ == '__main__':
    now = datetime.now()
    asyncio.run(main('https://2gis.ru/ufa/search/%D0%B2%D0%BA%D1%83%D1%81%D0%BD%D0%BE%20%D0%B8%20%D1%82%D0%BE%D1%87'
                     '%D0%BA%D0%B0/firm/70000001006794970/55.992084%2C54.746492/tab/reviews?m=55.980191%2C54.739852'
                     '%2F15.2'))
    print(datetime.now() - now)
