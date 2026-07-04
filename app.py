# Imou Gateway v2.0.0
# Main entry with CasaOS/Docker optimizations
import os
import sys
import signal
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from config import config
from mqtt_client import mqtt_manager
from database import db_manager
from parser import parse_webhook

# Setup logging with better formatting
log_level = config.get("gateway.log_level", "INFO")
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/imou-gateway.log', encoding='utf-8') if os.path.exists('logs') or os.makedirs('logs', exist_ok=True) else logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# Graceful shutdown flag
shutdown_event = False

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    global shutdown_event
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    shutdown_event = True
    mqtt_manager.disconnect()
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

@app.route('/', methods=['GET'])
def index():
    """Root endpoint with service info"""
    return jsonify({
        "service": "Imou Gateway v2.0.0",
        "status": "running",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint for Docker/Kubernetes"""
    health_status = {
        "status": "healthy",
        "service": "imou-gateway",
        "mqtt_connected": mqtt_manager.connected,
        "database_available": True,
        "timestamp": datetime.now().isoformat()
    }
    
    # Return 200 if system is healthy, 503 if not
    status_code = 200 if mqtt_manager.connected else 503
    return jsonify(health_status), status_code

@app.route('/stats', methods=['GET'])
def stats():
    """Get system statistics"""
    try:
        db_stats = db_manager.get_stats()
        return jsonify({
            "status": "ok",
            "database": db_stats,
            "mqtt_connected": mqtt_manager.connected,
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/webhook', methods=['POST'])
@app.route('/imou', methods=['POST'])
def webhook():
    """Receive webhook events from Imou cameras
    
    Supports both /webhook and /imou endpoints for compatibility
    """
    try:
        data = request.get_json()
        logger.info(f"Webhook received: {data}")
        
        # Validate data is a dictionary
        if not isinstance(data, dict):
            logger.warning(f"Invalid webhook data format: {type(data)}")
            return jsonify({"error": "Invalid data format. Expected JSON object"}), 400
        
        # Parse and process webhook
        event = parse_webhook(data)
        if event:
            event_id = db_manager.save_event(event)
            mqtt_manager.publish_event(event)
            
            logger.debug(f"Event saved with ID: {event_id}")
            return jsonify({
                "status": "ok",
                "event_id": event_id
            }), 200
        else:
            return jsonify({"error": "Failed to parse event"}), 400
    
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/events', methods=['GET'])
def get_events():
    """Get recent events with optional filtering"""
    try:
        limit = request.args.get('limit', default=50, type=int)
        channel = request.args.get('channel', default=None, type=int)
        event_type = request.args.get('type', default=None, type=str)
        
        # Limit the maximum number of events to return
        limit = min(limit, 500)
        
        events = db_manager.get_events(
            limit=limit,
            channel=channel,
            event_type=event_type
        )
        
        return jsonify({
            "status": "ok",
            "count": len(events),
            "events": events
        }), 200
    except Exception as e:
        logger.error(f"Error getting events: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/events/cleanup', methods=['POST'])
def cleanup_events():
    """Cleanup old events (admin endpoint)"""
    try:
        # Simple auth with API key if needed
        api_key = request.args.get('api_key', default='')
        days = request.args.get('days', default=30, type=int)
        
        # You can add API key validation here
        # if api_key != config.get("api.key"):
        #     return jsonify({"error": "Unauthorized"}), 401
        
        removed = db_manager.cleanup_old_events(days=days)
        
        logger.info(f"Cleaned up {removed} events older than {days} days")
        
        return jsonify({
            "status": "ok",
            "removed": removed,
            "days": days
        }), 200
    except Exception as e:
        logger.error(f"Error cleaning up events: {e}")
        return jsonify({"error": str(e)}), 500

@app.before_request
def before_request():
    """Pre-request checks"""
    if not mqtt_manager.connected:
        try:
            mqtt_manager.connect()
        except Exception as e:
            logger.warning(f"MQTT connection attempt failed: {e}")

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal error: {error}")
    return jsonify({"error": "Internal server error"}), 500

def start_app():
    """Start the Flask application"""
    try:
        logger.info("=" * 60)
        logger.info("Starting Imou Gateway v2.0.0")
        logger.info("=" * 60)
        
        # Log configuration
        logger.info(f"MQTT: {config.get('mqtt.host')}:{config.get('mqtt.port')}")
        logger.info(f"Database: {config.get('database.path')}")
        logger.info(f"Log Level: {log_level}")
        logger.info("=" * 60)
        
        # Connect MQTT
        try:
            mqtt_manager.connect()
            logger.info("MQTT connection initiated")
        except Exception as e:
            logger.warning(f"MQTT connection failed (will retry): {e}")
        
        # Start Flask
        logger.info("Starting Flask application on 0.0.0.0:5000")
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,
            use_reloader=False,
            threaded=True
        )
    
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, shutting down...")
        mqtt_manager.disconnect()
    
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        mqtt_manager.disconnect()
        sys.exit(1)
    
    finally:
        logger.info("Imou Gateway v2.0.0 stopped")

if __name__ == '__main__':
    start_app()

