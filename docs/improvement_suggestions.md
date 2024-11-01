# SEO Data Extraction Tool Improvement Suggestions

## 1. Security Improvements

### Critical
- Remove hardcoded credentials from config.py
- Implement secure credential management
- Add input validation for URLs and API parameters
- Add request/response sanitization

### Configuration Changes
```python
# config.py - Suggested changes
DATAFORSEO_LOGIN = os.getenv('DATAFORSEO_LOGIN')
DATAFORSEO_PASSWORD = os.getenv('DATAFORSEO_PASSWORD')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GOOGLE_CSE_ID = os.getenv('GOOGLE_CSE_ID')

if not all([DATAFORSEO_LOGIN, DATAFORSEO_PASSWORD, GOOGLE_API_KEY, GOOGLE_CSE_ID]):
    raise ValueError("Missing required environment variables")
```

## 2. Code Organization

### Remove Duplication
```python
# src/clients/base.py
class BaseAPIClient:
    def __init__(self, auth: aiohttp.BasicAuth, timeout: int = 30):
        self.auth = auth
        self.timeout = timeout
        self.session = None

    async def __aenter__(self):
        self.session = self._create_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def _create_session(self) -> aiohttp.ClientSession:
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        connector = aiohttp.TCPConnector(
            limit=10,
            enable_cleanup_closed=True,
            force_close=True
        )
        return aiohttp.ClientSession(
            auth=self.auth,
            timeout=timeout,
            connector=connector,
            raise_for_status=True
        )

# src/clients/dataforseo.py
class DataForSEOClient(BaseAPIClient):
    def __init__(self, auth: aiohttp.BasicAuth):
        super().__init__(auth)
        self.rate_limiter = RateLimiter(2)  # 2 requests per second

# src/clients/google.py
class GoogleSearchClient(BaseAPIClient):
    def __init__(self, api_key: str, cse_id: str):
        super().__init__(None)  # No auth needed, using API key
        self.api_key = api_key
        self.cse_id = cse_id
```

## 3. Resource Management

### Connection Pooling
```python
# src/core/http.py
class ConnectionPool:
    def __init__(self, pool_size: int = 10):
        self.semaphore = asyncio.Semaphore(pool_size)
        self.connections: Dict[str, aiohttp.ClientSession] = {}

    async def get_connection(self, key: str) -> aiohttp.ClientSession:
        async with self.semaphore:
            if key not in self.connections:
                self.connections[key] = self._create_session()
            return self.connections[key]

    def _create_session(self) -> aiohttp.ClientSession:
        return aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(force_close=True),
            timeout=aiohttp.ClientTimeout(total=30)
        )
```

### Session Management
```python
# src/core/session.py
class SessionManager:
    def __init__(self):
        self.pool = ConnectionPool()
        self._sessions: Dict[str, aiohttp.ClientSession] = {}

    async def get_session(self, key: str) -> aiohttp.ClientSession:
        if key not in self._sessions:
            self._sessions[key] = await self.pool.get_connection(key)
        return self._sessions[key]

    async def cleanup(self):
        for session in self._sessions.values():
            await session.close()
        self._sessions.clear()
```

## 4. XML Processing Improvements

### Streaming XML Parser
```python
# src/core/xml_parser.py
from xml.etree.ElementTree import iterparse
from typing import AsyncGenerator

class XMLStreamParser:
    def __init__(self, chunk_size: int = 8192):
        self.chunk_size = chunk_size

    async def parse_stream(self, response: aiohttp.ClientResponse) -> AsyncGenerator[str, None]:
        buffer = ""
        async for chunk in response.content.iter_chunked(self.chunk_size):
            buffer += chunk.decode('utf-8')
            while '<loc>' in buffer and '</loc>' in buffer:
                start = buffer.index('<loc>') + 5
                end = buffer.index('</loc>')
                url = buffer[start:end].strip()
                yield url
                buffer = buffer[end + 6:]
```

### Sitemap Processing
```python
# src/services/sitemap.py
class SitemapProcessor:
    def __init__(self, session_manager: SessionManager, xml_parser: XMLStreamParser):
        self.session_manager = session_manager
        self.xml_parser = xml_parser
        self.url_cache = TTLCache(maxsize=100, ttl=3600)

    async def process_sitemap(self, url: str) -> Set[str]:
        if url in self.url_cache:
            return self.url_cache[url]

        session = await self.session_manager.get_session('sitemap')
        urls = set()

        try:
            async with session.get(url) as response:
                if response.headers.get('Content-Type') == 'application/x-gzip':
                    content = await response.read()
                    content = gzip.decompress(content)
                    response = MockResponse(content)

                async for url in self.xml_parser.parse_stream(response):
                    urls.add(url)
                    if len(urls) >= MAX_URLS_PER_SITEMAP:
                        break

            self.url_cache[url] = urls
            return urls
        except Exception as e:
            logger.error(f"Error processing sitemap {url}: {str(e)}")
            return set()
```

## 5. Error Handling and Recovery

### Enhanced Error Handling
```python
# src/core/errors.py
class HTTPClientError(Exception):
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
        super().__init__(f"HTTP {status}: {message}")

class RetryableError(Exception):
    pass

# src/core/retry.py
class RetryStrategy:
    def __init__(self, max_retries: int = 3, initial_delay: float = 1.0):
        self.max_retries = max_retries
        self.initial_delay = initial_delay

    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        last_exception = None
        delay = self.initial_delay

        for attempt in range(self.max_retries):
            try:
                return await func(*args, **kwargs)
            except RetryableError as e:
                last_exception = e
                await asyncio.sleep(delay)
                delay *= 2
            except Exception as e:
                if not self._is_retryable(e):
                    raise
                last_exception = e
                await asyncio.sleep(delay)
                delay *= 2

        raise last_exception

    def _is_retryable(self, exception: Exception) -> bool:
        if isinstance(exception, aiohttp.ClientError):
            return True
        if isinstance(exception, asyncio.TimeoutError):
            return True
        return False
```

## 6. Performance Monitoring

### Request Tracking
```python
# src/core/metrics.py
class RequestTracker:
    def __init__(self):
        self.requests: Dict[str, List[float]] = defaultdict(list)
        self.errors: Dict[str, int] = defaultdict(int)

    def record_request(self, endpoint: str, duration: float):
        self.requests[endpoint].append(duration)

    def record_error(self, endpoint: str):
        self.errors[endpoint] += 1

    @property
    def statistics(self) -> Dict[str, Any]:
        stats = {}
        for endpoint, durations in self.requests.items():
            stats[endpoint] = {
                'count': len(durations),
                'avg_duration': sum(durations) / len(durations),
                'error_rate': self.errors[endpoint] / len(durations)
            }
        return stats
```

## Implementation Priority

1. Code Organization (High Priority)
   - Remove code duplication
   - Implement proper client structure
   - Add base classes and interfaces

2. Resource Management (High Priority)
   - Implement connection pooling
   - Add proper session management
   - Configure timeouts

3. XML Processing (High Priority)
   - Implement streaming parser
   - Add caching
   - Optimize memory usage

4. Error Handling (Medium Priority)
   - Implement retry strategy
   - Add error classification
   - Improve recovery mechanisms

5. Performance Monitoring (Medium Priority)
   - Add request tracking
   - Implement metrics collection
   - Add performance logging

6. Security (Medium Priority)
   - Remove hardcoded credentials
   - Add input validation
   - Implement proper auth handling

7. Testing (Low Priority)
   - Add unit tests
   - Implement integration tests
   - Add performance tests

8. Documentation (Low Priority)
   - Update API documentation
   - Add code examples
   - Document best practices
