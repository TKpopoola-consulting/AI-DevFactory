import pytest
from unittest.mock import MagicMock
from utils.cache import JobCache

def test_cache_operations():
    redis_mock = MagicMock()
    cache = JobCache()
    cache.redis = redis_mock
    
    # Test set
    cache.set_job("job123", {"status": "processing"})
    redis_mock.setex.assert_called_with(
        "job:job123", 300, '{"status": "processing"}'
    )
    
    # Test get
    redis_mock.get.return_value = b'{"status": "completed"}'
    assert cache.get_job("job123") == {"status": "completed"}
    
    # Test error handling
    redis_mock.get.side_effect = Exception("Connection failed")
    assert cache.get_job("job123") is None