import ee
from app.config import GEE_PROJECT_ID

_initialised = False

def init_gee() -> bool:
    global _initialised
    if _initialised:
        return True
    try:
        ee.Initialize(project=GEE_PROJECT_ID)
        print("✅ GEE initialized with OAuth")
        _initialised = True
        return True
    except Exception as exc:
        print(f"❌ GEE init failed: {exc}")
        print("   Run: earthengine authenticate")
        return False