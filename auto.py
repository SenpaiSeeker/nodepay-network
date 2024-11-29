import asyncio

import aiohttp
from loguru import logger


async def fetch_proxies(api_url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status == 200:
                    proxies = (await response.text()).strip().splitlines()
                    logger.info(f"Fetched {len(proxies)} proxies from API.")
                    return proxies
                else:
                    logger.warning(f"Failed to fetch proxies. Status code: {response.status}")
                    return []
    except Exception as e:
        logger.error(f"Error fetching proxies: {e}")
        return []


def save_proxies(proxy_file, proxies):
    try:
        with open(proxy_file, "w") as file:
            file.writelines([proxy + "\n" for proxy in proxies])
        logger.info(f"Saved {len(proxies)} proxies to {proxy_file}.")
    except Exception as e:
        logger.error(f"Error saving proxies: {e}")


async def main():
    proxy_api_url = (
        "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=text"
    )
    proxies = await fetch_proxies(proxy_api_url)
    save_proxies("proxies.txt", proxies)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Program terminated by user.")
