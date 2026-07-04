# Webhook parser
import logging

logger = logging.getLogger(__name__)

def parse_webhook(data):
    """Parse webhook data and extract event information"""
    try:
        if not isinstance(data, dict):
            logger.warning("Invalid webhook data format")
            return None
        
        # Extract common event fields
        event = {
            'channel': data.get('channel', 0),
            'type': data.get('type', 'unknown'),
            'description': data.get('description', ''),
            'timestamp': data.get('timestamp')
        }
        
        logger.info(f"Parsed event: {event}")
        return event
    except Exception as e:
        logger.error(f"Error parsing webhook: {e}")
        return None
