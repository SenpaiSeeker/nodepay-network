import asyncio
import random
import uuid

import cloudscraper
from fake_useragent import UserAgent
from loguru import logger

PING_INTERVAL = 1
DOMAIN_API_ENDPOINTS = {
    "SESSION": ["http://api.nodepay.ai/api/auth/session"],
    "PING": ["https://api.nodepay.ai/api/network/ping"],
}


def uuidv4():
    return str(uuid.uuid4())


def valid_resp(resp):
    if not resp or "code" not in resp or resp["code"] < 0:
        raise ValueError("Invalid response")
    return resp


def load_proxies(proxy_file):
    try:
        with open(proxy_file, "r") as file:
            return file.read().splitlines()
    except Exception as e:
        logger.error(f"Failed to load proxies: {e}")
        raise SystemExit("Exiting due to failure in loading proxies")


async def call_api(url, data, proxy, token):
    user_agent = UserAgent().random
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": user_agent,
        "Content-Type": "application/json",
    }
    try:
        scraper = cloudscraper.create_scraper()
        response = scraper.post(url, json=data, headers=headers, proxies={"http": proxy, "https": proxy}, timeout=30)
        response.raise_for_status()
        return valid_resp(response.json())
    except Exception as e:
        logger.error(f"Error during API call: {e}")
        raise ValueError(f"Failed API call to {url}")


async def render_profile_info(proxy, token):
    try:
        response = await call_api(random.choice(DOMAIN_API_ENDPOINTS["SESSION"]), {}, proxy, token)
        valid_resp(response)
        uid = response["data"].get("uid")
        if uid:
            logger.info(f"Session established for proxy {proxy}: UID {uid}")
            await start_ping(proxy, token, uid)
    except Exception as e:
        logger.error(f"Error in render_profile_info for proxy {proxy}: {e}")


async def start_ping(proxy, token, uid):
    try:
        while True:
            await ping(proxy, token, uid)
            await asyncio.sleep(PING_INTERVAL)
    except asyncio.CancelledError:
        logger.info(f"Ping task for proxy {proxy} was cancelled")
    except Exception as e:
        logger.error(f"Error in start_ping for proxy {proxy}: {e}")


async def ping(proxy, token, uid):
    data = {
        "id": uid,
        "timestamp": int(asyncio.get_event_loop().time()),
    }
    try:
        response = await call_api(random.choice(DOMAIN_API_ENDPOINTS["PING"]), data, proxy, token)
        if response["code"] == 0:
            logger.info(f"Ping successful via proxy {proxy}")
        else:
            logger.error(f"Ping failed via proxy {proxy} with response: {response}")
    except Exception as e:
        logger.error(f"Ping failed via proxy {proxy}: {e}")


async def main():
    all_proxies = load_proxies("proxies.txt")

    token = input("Enter Nodepay token: ").strip()
    if not token:
        logger.error("Token cannot be empty. Exiting.")
        return

    while True:
        active_proxies = [proxy for proxy in all_proxies if proxy]
        tasks = [render_profile_info(proxy, token) for proxy in active_proxies]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Program terminated by user.")
