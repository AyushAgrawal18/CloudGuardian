
import logging
import time

import httpx

from agent.config import (
    API_BASE_URL,
    AGENT_EMAIL,
    AGENT_PASSWORD,
)

logger = logging.getLogger("cloudguardian-agent")

MAX_RETRIES = 3
BACKOFF_BASE_SECONDS = 2


class CloudGuardianClient:
    def __init__(self):
        if not AGENT_EMAIL or not AGENT_PASSWORD:
            raise RuntimeError(
                "Agent credentials are missing from environment variables"
            )

        self.client = httpx.Client(
            base_url=API_BASE_URL,
            timeout=10.0,
        )

        self.access_token = None

    def login(self):
        response = self.client.post(
            "/api/v1/auth/login",
            json={
                "email": AGENT_EMAIL,
                "password": AGENT_PASSWORD,
            },
        )

        response.raise_for_status()

        self.access_token = response.json()["access_token"]

        self.client.headers.update({
            "Authorization": f"Bearer {self.access_token}"
        })

        logger.info("Successfully authenticated with CloudGuardian")

    def _send_with_retry(self, payload: dict):
        for attempt in range(MAX_RETRIES + 1):
            try:
                response = self.client.post(
                    "/api/v1/metrics",
                    json=payload,
                )

                # Return 401 so send_metrics() can refresh the JWT.
                if response.status_code == 401:
                    return response

                # Retry only temporary server errors.
                if response.status_code >= 500:
                    response.raise_for_status()

                # Do not retry validation or permission errors.
                response.raise_for_status()

                return response

            except (httpx.TimeoutException, httpx.NetworkError) as error:
                if attempt == MAX_RETRIES:
                    raise

                delay = BACKOFF_BASE_SECONDS * (2 ** attempt)

                logger.warning(
                    "API connection failed: %s. Retrying in %s seconds "
                    "(attempt %s/%s)",
                    error,
                    delay,
                    attempt + 1,
                    MAX_RETRIES,
                )

                time.sleep(delay)

            except httpx.HTTPStatusError as error:
                if error.response.status_code < 500:
                    raise

                if attempt == MAX_RETRIES:
                    raise

                delay = BACKOFF_BASE_SECONDS * (2 ** attempt)

                logger.warning(
                    "Backend returned HTTP %s. Retrying in %s seconds",
                    error.response.status_code,
                    delay,
                )

                time.sleep(delay)

    def send_metrics(self, payload: dict):
        if not self.access_token:
            self.login()

        response = self._send_with_retry(payload)

        # Refresh JWT once if the token has expired.
        if response.status_code == 401:
            logger.warning("Access token expired. Re-authenticating...")

            self.login()

            response = self._send_with_retry(payload)

        return response.json()

    def close(self):
        self.client.close()
