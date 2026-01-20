import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://neondb_owner:npg_Oslv6SAEJex7@ep-snowy-glitter-a17b3nee-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"
)

RAG_TOP_K = 5
CONTEXT_TIME_WINDOWS = [7, 14, 30]

ENABLE_CONTEXT_CACHE = True
CONTEXT_CACHE_TTL_SECONDS = 3600

DEFAULT_FORECAST_DAYS = 14
