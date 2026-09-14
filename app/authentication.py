"""
Custom JWT Authentication
Supports both HTTP-only cookies and Authorization header
"""

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.exceptions import AuthenticationFailed
import logging

logger = logging.getLogger(__name__)


class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that reads tokens from HTTP-only cookies.
    Falls back to Authorization header if cookie not present.
    """

    def authenticate(self, request):
        # Log the request path and cookies
        logger.info(f"🔍 Auth attempt for: {request.path}")
        logger.info(f"🔍 Cookies present: {list(request.COOKIES.keys())}")
        
        # Priority 1: Try to get token from HTTP-only cookie
        raw_token = request.COOKIES.get('access_token')
        
        if raw_token:
            logger.info(f"✅ Found access_token in cookies (length: {len(raw_token)})")
        else:
            logger.info("❌ No access_token in cookies")

        # Priority 2: If not in cookie, try Authorization header
        if not raw_token:
            header = self.get_header(request)
            if header is None:
                logger.info("❌ No Authorization header")
                return None
            try:
                raw_token = self.get_raw_token(header)
                logger.info("✅ Got token from Authorization header")
            except Exception as e:
                logger.error(f"❌ Failed to extract token from header: {e}")
                return None

        if raw_token is None:
            logger.info("❌ No token available from any source")
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
            user = self.get_user(validated_token)
            logger.info(f"✅ Authentication successful for user: {user.email}")
            return (user, validated_token)
        except InvalidToken as e:
            logger.error(f"❌ Invalid token: {e}")
            return None
        except TokenError as e:
            logger.error(f"❌ Token error: {e}")
            return None
        except AuthenticationFailed as e:
            logger.error(f"❌ Authentication failed: {e}")
            raise