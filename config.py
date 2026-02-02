import os

MAX_REQUEST_TIMEOUT = int(os.getenv("MAX_REQUEST_TIMEOUT", "600"))

AIPING_BASE_URL = os.getenv("AIPING_BASE_URL", "https://aiping.cn/api/v1")
