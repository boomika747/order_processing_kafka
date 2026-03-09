import traceback
import sys
try:
    import tests.test_producer
except Exception as e:
    traceback.print_exc()
    sys.exit(1)
sys.exit(0)
