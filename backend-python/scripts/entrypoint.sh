#!/bin/sh
# Wait for Postgres and run migrations, then exec uvicorn.
set -e

RETRIES=30
until python -c "
import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import get_settings
async def check():
    try:
        e = create_async_engine(get_settings().database_url)
        async with e.connect() as c:
            await c.run_sync(lambda _: None)
        await e.dispose()
        return True
    except Exception:
        return False
sys.exit(0 if asyncio.run(check()) else 1)
" 2>/dev/null; do
  echo "Waiting for database..."
  RETRIES=$((RETRIES - 1))
  if [ "$RETRIES" -le 0 ]; then
    echo "Database not ready."
    exit 1
  fi
  sleep 2
done
echo "Database ready."
alembic upgrade head
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
