from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import logging
import traceback
from datetime import datetime
import os
from claude_ai import ClaudeAI
from config import Config
import markdown
import bleach

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Global AI instance
claude_ai = None

def get_ai_instance():
    """Get or create Claude AI instance."""
    global claude_ai
    if claude_ai is None:
        try:
            claude_ai = ClaudeAI()
            logger.info("Claude AI instance created successfully")
        except Exception as e:
            logger.error(f"Failed to create Claude AI instance: {e}")
            raise
    return claude_ai

def format_message(content: str) -> str:
    """Format message content with markdown and sanitization."""
    try:
        # Convert markdown to HTML
        html = markdown.markdown(content, extensions=['codehilite', 'fenced_code'])
        # Sanitize HTML to prevent XSS
        safe_html = bleach.clean(html, tags=[
            'p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'blockquote', 'code', 'pre', 'a', 'div', 'span'
        ], attributes={
            'a': ['href', 'title'],
            'div': ['class'],
            'span': ['class'],
            'code': ['class'],
            'pre': ['class']
        })
        return safe_html
    except Exception as e:
        logger.error(f"Error formatting message: {e}")
        return content

@app.route('/')
def index():
    """Main page route."""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages."""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400
        
        user_message = data['message'].strip()
        if not user_message:
            return jsonify({'error': 'Empty message'}), 400
        
        # Get AI instance
        ai = get_ai_instance()
        
        # Generate response
        response = ai.generate_response_sync(user_message)
        
        return jsonify({
            'response': response,
            'formatted_response': format_message(response),
            'timestamp': datetime.now().isoformat(),
            'conversation_summary': ai.get_conversation_summary()
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/conversation/clear', methods=['POST'])
def clear_conversation():
    """Clear conversation history."""
    try:
        ai = get_ai_instance()
        ai.clear_conversation()
        return jsonify({'message': 'Conversation cleared successfully'})
    except Exception as e:
        logger.error(f"Error clearing conversation: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/conversation/history', methods=['GET'])
def get_conversation_history():
    """Get conversation history."""
    try:
        ai = get_ai_instance()
        history = ai.get_conversation_history()
        
        # Format messages for display
        formatted_history = []
        for msg in history:
            formatted_msg = {
                'role': msg['role'],
                'content': msg['content'],
                'formatted_content': format_message(msg['content']),
                'timestamp': msg.get('timestamp', '')
            }
            formatted_history.append(formatted_msg)
        
        return jsonify({
            'history': formatted_history,
            'summary': ai.get_conversation_summary()
        })
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/conversation/export', methods=['GET'])
def export_conversation():
    """Export conversation history."""
    try:
        ai = get_ai_instance()
        conversation_json = ai.export_conversation()
        return jsonify({
            'conversation': conversation_json,
            'filename': f"claude_conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        })
    except Exception as e:
        logger.error(f"Error exporting conversation: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/system-prompt', methods=['GET', 'POST'])
def system_prompt():
    """Get or update system prompt."""
    try:
        ai = get_ai_instance()
        
        if request.method == 'GET':
            return jsonify({'system_prompt': ai.system_prompt})
        
        elif request.method == 'POST':
            data = request.get_json()
            if not data or 'system_prompt' not in data:
                return jsonify({'error': 'No system prompt provided'}), 400
            
            new_prompt = data['system_prompt'].strip()
            if not new_prompt:
                return jsonify({'error': 'Empty system prompt'}), 400
            
            ai.set_system_prompt(new_prompt)
            return jsonify({'message': 'System prompt updated successfully'})
            
    except Exception as e:
        logger.error(f"Error handling system prompt: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        # Verify configuration
        Config.validate_config()
        return jsonify({
            'status': 'healthy',
            'model': Config.CLAUDE_MODEL,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    try:
        # Validate configuration before starting
        Config.validate_config()
        logger.info(f"Starting Claude AI application on {Config.HOST}:{Config.PORT}")
        app.run(
            host=Config.HOST,
            port=Config.PORT,
            debug=Config.DEBUG
        )
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise