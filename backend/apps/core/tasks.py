"""
Celery tasks for the core app.
"""
from celery import shared_task
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_domain_event(self, event_id: str):
    from backend.apps.core.models import Event
    
    try:
        event = Event.objects.get(id=event_id)
        
        if event.status == 'processed':
            logger.info(f"Event {event_id} already processed")
            return {'status': 'already_processed', 'event_id': event_id}
        
        event.status = 'processing'
        event.save(update_fields=['status'])
        
        event.status = 'processed'
        event.processed_at = timezone.now()
        event.save(update_fields=['status', 'processed_at'])
        
        logger.info(f"Successfully processed event {event_id}")
        return {'status': 'success', 'event_id': event_id}
        
    except Event.DoesNotExist:
        logger.error(f"Event {event_id} not found")
        return {'status': 'error', 'message': 'Event not found'}
    except Exception as exc:
        logger.error(f"Error processing event {event_id}: {exc}")
        event.retry_count += 1
        event.status = 'failed'
        event.save(update_fields=['retry_count', 'status'])
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task
def cleanup_old_events(days: int = 30):
    from backend.apps.core.models import Event
    from datetime import timedelta
    
    cutoff = timezone.now() - timedelta(days=days)
    deleted_count, _ = Event.objects.filter(
        status='processed',
        processed_at__lt=cutoff
    ).delete()
    
    logger.info(f"Cleaned up {deleted_count} old events")
    return {'deleted_count': deleted_count}


@shared_task
def sync_user_roles_cache():
    from backend.apps.core.models import User
    from backend.apps.core.cache import set_cached, make_cache_key, CACHE_TIMEOUTS
    
    users = User.objects.all()
    updated = 0
    
    for user in users:
        cache_key = make_cache_key('user_roles', str(user.id))
        set_cached(cache_key, user.roles, CACHE_TIMEOUTS['user_roles'])
        updated += 1
    
    logger.info(f"Synced roles cache for {updated} users")
    return {'users_updated': updated}


@shared_task
def generate_audit_report(start_date: str, end_date: str):
    from backend.apps.core.models import AuditLog
    from datetime import datetime
    
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)
    
    logs = AuditLog.objects.filter(
        timestamp__gte=start,
        timestamp__lte=end
    )
    
    summary = {
        'total_actions': logs.count(),
        'by_action': {},
        'by_entity_type': {},
    }
    
    for log in logs:
        summary['by_action'][log.action] = summary['by_action'].get(log.action, 0) + 1
        summary['by_entity_type'][log.entity_type] = summary['by_entity_type'].get(log.entity_type, 0) + 1
    
    return summary
