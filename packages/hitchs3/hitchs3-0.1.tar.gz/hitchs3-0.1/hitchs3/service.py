from hitchtest.environment import checks
from hitchserve import Service
import hitchs3
import sys


class MockBucket(object):
    """Mock bucket for use with MockS3Service."""

    def __init__(self, name):
        self._name = name


class MockS3Service(Service):
    """Run a Mock S3 Service."""

    def __init__(self, buckets=None, port=10028, **kwargs):
        """Initialize mock S3 service.

        Args:
            buckets (Optional[MockBucket]): Run service with mock buckets.
        """
        self._port = port
        self._buckets = buckets
        kwargs['log_line_ready_checker'] = lambda line: "Listening on" in line
        kwargs['command'] = [sys.executable, "-u", "-m", "hitchs3.s3server", "--port", str(port)]
        super(MockS3Service, self).__init__(**kwargs)
