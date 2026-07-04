# Webhook parser - Support for Imou camera formats
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Map Imou event codes to readable event types
# Supports both local device codes (1-10) and PaaS cloud codes (100+)
IMOU_EVENT_CODE_MAP = {
    # Local device event codes
    "0": "unknown",
    "1": "motion",              # Motion detection
    "2": "person_detection",    # Person detection
    "3": "alarm",               # Alarm
    "4": "face_detection",      # Face detection
    "5": "vehicle_detection",   # Vehicle detection
    "6": "sound_detection",     # Abnormal sound
    "7": "tampering",           # Tampering detection
    "8": "line_crossing",       # Line crossing
    "9": "intrusion",           # Intrusion detection
    "10": "parking",            # Parking detection
    
    # PaaS/Cloud event codes
    "120": "person_detection",   # Human detection/alarm
    "10039": "person_detection", # Smart detection human (NVR)
}

# Map PaaS labelType/msgType to event types
IMOU_PAAS_TYPE_MAP = {
    "humanAlarm": "person_detection",
    "human": "person_detection",
    "smdHuman": "person_detection",
    "motionAlarm": "motion",
    "motion": "motion",
    "mdAlarm": "motion",
    "vehicleAlarm": "vehicle_detection",
    "vehicle": "vehicle_detection",
    "faceAlarm": "face_detection",
    "face": "face_detection",
    "soundAlarm": "sound_detection",
    "sound": "sound_detection",
}

def parse_webhook(data):
    """
    Parse webhook data and extract event information
    Supports multiple Imou camera webhook formats
    
    Format 1 (Real Imou):
    {
        "channel": 0,
        "event_type": "1",
        "description": "",
        "timestamp": "2026-07-04 14:31:18"
    }
    
    Format 2 (Test/Custom):
    {
        "channel": 1,
        "type": "motion",
        "description": "Motion detected",
        "device_id": "IMOU-001"
    }
    """
    try:
        if not isinstance(data, dict):
            logger.warning(f"Invalid webhook data format: {type(data)}")
            return None
        
        # Extract channel - handle both formats
        # PaaS format uses 'cid', local format uses 'channel'
        channel = data.get('channel') or data.get('chn') or data.get('cid') or 0
        try:
            channel = int(channel) if channel else 0
        except (ValueError, TypeError):
            channel = 0
        
        # Map channel 0 to channel 1 for better usability
        if channel == 0:
            channel = 1
        
        # Extract event type - handle both formats
        event_type_raw = data.get('type') or data.get('event_type') or 'unknown'
        
        # Check if it's an Imou event code (numeric string or int like 1, 2, 120, etc.)
        if isinstance(event_type_raw, (int, str)):
            event_type_code = str(event_type_raw)
            # First check if it's a numeric code in our map
            if event_type_code.isdigit() and event_type_code in IMOU_EVENT_CODE_MAP:
                event_type = IMOU_EVENT_CODE_MAP[event_type_code]
                logger.debug(f"Mapped Imou event code '{event_type_code}' to '{event_type}'")
            else:
                # Try PaaS labelType/msgType mapping
                label_type = data.get('labelType', '').lower()
                msg_type = data.get('msgType', '').lower()
                
                # Check labelType first, then msgType
                if label_type and label_type in IMOU_PAAS_TYPE_MAP:
                    event_type = IMOU_PAAS_TYPE_MAP[label_type]
                    logger.debug(f"Mapped PaaS labelType '{label_type}' to '{event_type}'")
                elif msg_type and msg_type in IMOU_PAAS_TYPE_MAP:
                    event_type = IMOU_PAAS_TYPE_MAP[msg_type]
                    logger.debug(f"Mapped PaaS msgType '{msg_type}' to '{event_type}'")
                else:
                    # Normalize standard event type
                    event_type = normalize_event_type(event_type_raw)
        else:
            # Normalize standard event type
            event_type = normalize_event_type(event_type_raw)
        
        # Extract description - prefer cname (channel name) from PaaS format
        description = data.get('description') or data.get('msg') or ''
        
        # For PaaS format, build description from available fields
        if not description and 'cname' in data:
            cname = data.get('cname', '').strip()
            label_type = data.get('labelType', '').strip()
            if cname and label_type:
                description = f"{label_type} on {cname}"
            elif cname:
                description = f"{cname} - {event_type.replace('_', ' ').title()}"
            else:
                description = f"{event_type.replace('_', ' ').title()}"
        
        # If description is still empty, generate from event type
        if not description:
            description = f"{event_type.replace('_', ' ').title()}"
        
        # Extract timestamp - handle multiple formats
        timestamp = data.get('timestamp') or data.get('time')
        if not timestamp:
            timestamp = datetime.now().isoformat()
        else:
            # Try to parse and normalize timestamp
            timestamp = normalize_timestamp(timestamp)
        
        event = {
            'channel': channel,
            'type': event_type,
            'description': description,
            'timestamp': timestamp,
            'device_id': data.get('device_id') or data.get('deviceId') or data.get('did') or 'unknown',
            'device_name': data.get('device_name') or data.get('deviceName') or data.get('dname') or '',
        }
        
        # Add optional fields if present
        if 'confidence' in data:
            event['confidence'] = data['confidence']
        
        if 'alarm_type' in data:
            event['alarm_type'] = data['alarm_type']
        
        if 'image_url' in data:
            event['image_url'] = data['image_url']
        
        if 'snapshot' in data:
            event['snapshot'] = data['snapshot']
        
        logger.info(f"Parsed event: type={event['type']}, channel={event['channel']}, device={event['device_id']}")
        logger.debug(f"Full event: {event}")
        return event
    
    except Exception as e:
        logger.error(f"Error parsing webhook: {e}")
        logger.debug(f"Problematic data: {data}")
        return None


def normalize_timestamp(timestamp):
    """
    Normalize various timestamp formats to ISO format
    
    Supports:
    - Unix epoch (seconds): 1783201662
    - Unix epoch (milliseconds): 1783201662000
    - "2026-07-04 14:31:18" (Imou format)
    - "2026-07-04T14:31:18" (ISO format)
    - "2026-07-04T14:31:18Z" (ISO with Z)
    """
    if not timestamp:
        return datetime.now().isoformat()
    
    timestamp_str = str(timestamp).strip()
    
    # Handle Unix epoch (numeric)
    try:
        timestamp_int = int(timestamp_str)
        # If it's a reasonable Unix timestamp (between 2020 and 2050)
        if 1577836800 <= timestamp_int <= 2524608000:
            # Convert to datetime
            dt = datetime.utcfromtimestamp(timestamp_int)
            return dt.isoformat()
    except (ValueError, TypeError):
        pass
    
    # Already ISO format
    if 'T' in timestamp_str:
        return timestamp_str
    
    # Imou format: "2026-07-04 14:31:18"
    try:
        dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        return dt.isoformat()
    except ValueError:
        pass
    
    # Try other common formats
    formats = [
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y/%m/%d %H:%M:%S",
        "%d-%m-%Y %H:%M:%S",
        "%d/%m/%Y %H:%M:%S",
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(timestamp_str, fmt)
            return dt.isoformat()
        except ValueError:
            continue
    
    # If all parsing fails, return as-is
    logger.warning(f"Could not parse timestamp: {timestamp_str}")
    return timestamp_str


def normalize_event_type(event_type):
    """
    Normalize event type to standard format
    Handles various Imou webhook event type formats
    """
    if not event_type:
        return 'unknown'
    
    # Convert to lowercase for comparison
    event_lower = str(event_type).lower().strip()
    
    # Motion detection
    if 'motion' in event_lower or 'md' in event_lower:
        return 'motion'
    
    # Person detection
    if 'person' in event_lower or 'human' in event_lower:
        return 'person_detection'
    
    # Vehicle detection
    if 'vehicle' in event_lower or 'car' in event_lower:
        return 'vehicle_detection'
    
    # Face detection
    if 'face' in event_lower:
        return 'face_detection'
    
    # Alarm
    if 'alarm' in event_lower:
        return 'alarm'
    
    # Abnormal sound
    if 'sound' in event_lower or 'abnormal' in event_lower:
        return 'sound_detection'
    
    # Tampering
    if 'tamper' in event_lower or 'tampering' in event_lower:
        return 'tampering'
    
    # Line crossing
    if 'line' in event_lower or 'crossing' in event_lower:
        return 'line_crossing'
    
    # Intrusion
    if 'intrusion' in event_lower:
        return 'intrusion'
    
    # Parking
    if 'parking' in event_lower:
        return 'parking'
    
    # Other events - return as-is
    return event_lower


