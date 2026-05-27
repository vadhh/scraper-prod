import requests
from bs4 import BeautifulSoup
import random
import time
import logging

from config import BASE_URL, USER_AGENTS, CAPTCHA_SIGNATURES

log = logging.getLogger(__name__)


class CaptchaDetectedError(Exception):
    pass


class RateLimitError(Exception):
    pass


class ScraperSession:
    def __init__(self, proxy=None, min_delay=1.0, max_delay=3.0):
        self.session = requests.Session()
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.request_count = 0
        self.captcha_count = 0
        self.rate_limit_count = 0

        if proxy:
            self.session.proxies = {"http": proxy, "https": proxy}
            log.info(f"Using proxy: {proxy}")

    def _rotate_headers(self):
        self.session.headers.update({
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": BASE_URL,
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        })

    def _detect_captcha(self, response):
        text = response.text.lower()
        for sig in CAPTCHA_SIGNATURES:
            if sig in text:
                return True
        if response.status_code == 403 and len(response.text) < 5000:
            return True
        return False

    def _throttle(self):
        delay = random.uniform(self.min_delay, self.max_delay)
        if self.request_count > 0 and self.request_count % 50 == 0:
            delay = random.uniform(5.0, 10.0)
            log.info(f"Cooling down for {delay:.1f}s after {self.request_count} requests...")
        time.sleep(delay)

    def get(self, url, max_retries=5):
        self._throttle()
        self._rotate_headers()

        for attempt in range(1, max_retries + 1):
            try:
                response = self.session.get(url, timeout=20)
                self.request_count += 1

                if response.status_code == 429:
                    self.rate_limit_count += 1
                    retry_after = int(response.headers.get("Retry-After", 0))
                    backoff = max(retry_after, (2 ** attempt) + random.uniform(0, 2))
                    log.warning(f"Rate limited (429). Waiting {backoff:.1f}s (attempt {attempt}/{max_retries})")
                    time.sleep(backoff)
                    continue

                if response.status_code == 503:
                    backoff = (2 ** attempt) + random.uniform(0, 2)
                    log.warning(f"Service unavailable (503). Waiting {backoff:.1f}s (attempt {attempt}/{max_retries})")
                    time.sleep(backoff)
                    continue

                if self._detect_captcha(response):
                    self.captcha_count += 1
                    log.warning(f"CAPTCHA detected on {url} (attempt {attempt}/{max_retries})")

                    if attempt < max_retries:
                        backoff = (2 ** attempt) * 5 + random.uniform(0, 5)
                        log.info(f"Rotating identity and waiting {backoff:.1f}s...")
                        self._rotate_headers()
                        time.sleep(backoff)
                        continue
                    else:
                        raise CaptchaDetectedError(
                            f"CAPTCHA persists after {max_retries} attempts on {url}. "
                            "Try using a proxy or solving service."
                        )

                response.raise_for_status()
                return BeautifulSoup(response.text, "lxml")

            except requests.exceptions.ConnectionError:
                backoff = (2 ** attempt) + random.uniform(0, 2)
                log.warning(f"Connection error. Retrying in {backoff:.1f}s (attempt {attempt}/{max_retries})")
                time.sleep(backoff)
            except requests.exceptions.Timeout:
                backoff = (2 ** attempt) + random.uniform(0, 2)
                log.warning(f"Timeout. Retrying in {backoff:.1f}s (attempt {attempt}/{max_retries})")
                time.sleep(backoff)
            except (CaptchaDetectedError, requests.exceptions.HTTPError):
                raise
            except requests.exceptions.RequestException as e:
                if attempt == max_retries:
                    raise
                backoff = (2 ** attempt) + random.uniform(0, 2)
                log.warning(f"Request error: {e}. Retrying in {backoff:.1f}s (attempt {attempt}/{max_retries})")
                time.sleep(backoff)

        raise RateLimitError(f"Failed after {max_retries} retries on {url}")

    def stats(self):
        return {
            "requests": self.request_count,
            "captchas_hit": self.captcha_count,
            "rate_limits_hit": self.rate_limit_count,
        }
