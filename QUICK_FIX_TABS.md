# Quick Fix: Tab Loading Issues

## Problem
Non-dashboard tabs (Maintenance, Coaching, etc.) hang in loading state because API endpoints timeout.

## Root Cause
1. Dashboard APIs (`/api/dashboard/overview`, `/api/vehicles/`) work fine
2. Other APIs (`/api/maintenance/*`, `/api/coaching/*`) timeout (>30 seconds)
3. Frontend `fetch()` has no timeout, so components show loading spinner forever

## Quick Solution (5 minutes)

Add fetch timeout wrapper to `frontend/src/hooks/useGeotab.ts`:

```typescript
// Add this helper at the top of the file
const fetchWithTimeout = async (url: string, timeout = 10000) => {
  const controller = new AbortController()
  const id = setTimeout(() => controller.abort(), timeout)
  
  try {
    const response = await fetch(url, { signal: controller.signal })
    clearTimeout(id)
    return response
  } catch (error: any) {
    clearTimeout(id)
    if (error.name === 'AbortError') {
      throw new Error('Request timeout')
    }
    throw error
  }
}

// Replace all fetch() calls with fetchWithTimeout()
// Example in useFetch:
const fetchData = useCallback(async () => {
  try {
    const res = await fetchWithTimeout(url, 10000) // 10 second timeout
    if (!res.ok) throw new Error(`${res.status}`)
    setData(await res.json())
    setError(null)
  } catch (e: any) {
    setError(e.message)
    setData(null) // Important: clear data on error
  } finally {
    setLoading(false)
  }
}, [url])
```

## Alternative: Mock Data Fallback (10 minutes)

Add mock data for tabs that timeout:

1. **Maintenance Tab:** Return static predictions
2. **Coaching Tab:** Return sample driver profiles
3. **Other tabs:** Return minimal/cached data

This ensures demo video shows all features working.

## Backend Fix (Proper Solution - 30 minutes)

Add timeout handling to all Geotab API calls in backend routers:

```python
# In each router file, wrap Geotab calls with timeout
import asyncio
from fastapi import HTTPException

async def get_geotab_data_with_timeout(func, timeout=5):
    try:
        return await asyncio.wait_for(asyncio.to_thread(func), timeout=timeout)
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Geotab API timeout")
```

## Recommended for Competition

**Use frontend timeout + error messages:**
- Fast to implement (5 min)
- Shows professional error handling
- Tabs won't hang forever
- User sees "Data unavailable" instead of infinite spinner

**Command to rebuild frontend:**
```bash
cd /home/ethan/FleetPulse/frontend
npm run build
```

Then push to trigger deployment:
```bash
git add -A
git commit -m "fix: add fetch timeout to prevent infinite loading"
git push origin main
```

Deployment will auto-trigger (5-7 min build time).

---

**Status:** Issue identified. Ready to apply fix.
