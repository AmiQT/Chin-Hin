"""
Request Middleware untuk logging, tracing, dan timing.
Setiap request dapat unique ID! 🎯
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from uuid import uuid4
import time
import logging

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security headers to all responses.
    These headers help protect against common web vulnerabilities.
    """
    
    async def dispatch(
        self, 
        request: Request, 
        call_next: RequestResponseEndpoint
    ) -> Response:
        response = await call_next(request)
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # Enable XSS filter in browsers
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Strict Transport Security (HTTPS only)
        # Only enable in production with HTTPS
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Prevent referrer leakage
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Content Security Policy (basic)
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        
        # Permissions Policy (previously Feature-Policy)
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        return response


class RequestMiddleware(BaseHTTPMiddleware):
    """
    Middleware untuk:
    1. Generate unique request ID
    2. Log request/response
    3. Track request duration
    """
    
    async def dispatch(
        self, 
        request: Request, 
        call_next: RequestResponseEndpoint
    ) -> Response:
        # Generate unique request ID
        request_id = str(uuid4())[:8]
        
        # Store in request state for access in handlers
        request.state.request_id = request_id
        
        # Start timer
        start_time = time.perf_counter()
        
        # Get request info
        method = request.method
        path = request.url.path
        client_ip = request.client.host if request.client else "unknown"
        
        # Log incoming request
        logger.info(
            f"➡️  {method} {path} | Client: {client_ip} | ReqID: {request_id}"
        )
        
        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            # Calculate duration
            duration_ms = (time.perf_counter() - start_time) * 1000
            
            logger.error(
                f"❌ {method} {path} | Error: {str(e)} | "
                f"Duration: {duration_ms:.2f}ms | ReqID: {request_id}"
            )
            raise
        
        # Calculate duration
        duration_ms = (time.perf_counter() - start_time) * 1000
        
        # Add headers to response
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"
        
        # Choose emoji based on status code
        if response.status_code < 300:
            emoji = "✅"
        elif response.status_code < 400:
            emoji = "↪️"
        elif response.status_code < 500:
            emoji = "⚠️"
        else:
            emoji = "❌"
        
        # Log response
        logger.info(
            f"{emoji} {method} {path} | Status: {response.status_code} | "
            f"Duration: {duration_ms:.2f}ms | ReqID: {request_id}"
        )
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiting.
    TODO: Use Redis for distributed rate limiting.
    """
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests = {}  # IP -> list of timestamps
    
    async def dispatch(
        self, 
        request: Request, 
        call_next: RequestResponseEndpoint
    ) -> Response:
        # Skip rate limiting for health check
        if request.url.path in ["/health", "/", "/docs", "/openapi.json"]:
            return await call_next(request)
        
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # Clean old requests (older than 1 minute)
        if client_ip in self.requests:
            self.requests[client_ip] = [
                t for t in self.requests[client_ip] 
                if current_time - t < 60
            ]
        else:
            self.requests[client_ip] = []
        
        # Check rate limit
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            request_id = getattr(request.state, "request_id", "unknown")
            logger.warning(
                f"🐢 Rate limit exceeded | IP: {client_ip} | ReqID: {request_id}"
            )
            
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error": {
                        "code": "TOO_MANY_REQUESTS",
                        "message": "Slow down bro! Terlalu banyak request! 🐢"
                    }
                },
                headers={"Retry-After": "60"}
            )
        
        # Record this request
        self.requests[client_ip].append(current_time)
        
        return await call_next(request)
