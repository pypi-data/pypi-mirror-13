from django.conf import settings
from django.core.cache import cache
from django.db import IntegrityError
from django.db import DatabaseError
from django.http.response import HttpResponse
from django.middleware.common import CommonMiddleware

from ..models import Heartbeat
from .. import defaults as defs


class HeartbeatMiddleWare(CommonMiddleware):
    """
    Check Django's health.
    """
    def process_request(self, request):
        """
        Determines the health of our Django application, back-ends and environment.
        """
        if request.path == defs.PULSEWARE_DEFAULT_SETTINGS.get('PATH'):
            if defs.PULSEWARE_DEFAULT_SETTINGS.get('DATABASE_READ_HEALTH'):
                try:
                    Heartbeat.objects.filter().exists()
                except IntegrityError:
                    return self.send_response("Integrity Error - Read")
                except DatabaseError:
                    return self.send_response("Database Error - Read")
                except Exception:
                    return self.send_response("Unknown Database Read Error")

            if defs.PULSEWARE_DEFAULT_SETTINGS.get('DATABASE_WRITE_HEALTH'):
                try:
                    obj = Heartbeat.objects.filter().first()
                    obj.save()
                except IntegrityError:
                    return self.send_response("Integrity Error - Write")
                except DatabaseError:
                    return self.send_response("Database Error - Write")
                except Exception:
                        return self.send_response("Unknown Database Write Error")

            if defs.PULSEWARE_DEFAULT_SETTINGS.get('CACHE_HEALTH'):
                try:
                    value = 100
                    cache.set('check-my-cache-health', value)
                    if cache.get('check-my-cache-health') != value:
                        return self.send_response("Cache Error")
                except CacheKeyWarning:
                    return self.send_response("Cache Key Error")
                except ValueError:
                    return self.send_response("Cache Value Error")
                except Exception:
                        return self.send_response("Unknown Cache Error")

            return self.send_response("Healthy I am")

    def send_response(self, message='', status=200):
        """
        Sends response.
        """
        return HttpResponse(message, status=status)
