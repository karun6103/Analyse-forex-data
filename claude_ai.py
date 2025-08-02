import anthropic
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClaudeAI:
    """
    Core AI class for interacting with Claude 4 Sonnet LLM.
    Handles conversation memory, context management, and API interactions.
    """
    
    def __init__(self):
        """Initialize the Claude AI client and conversation memory."""
        Config.validate_config()
        self.client = anthropic.Anthropic(api_key=Config.CLAUDE_API_KEY)
        self.conversation_history: List[Dict] = []
        self.system_prompt = self._get_default_system_prompt()
        
    def _get_default_system_prompt(self) -> str:
        """Get the default system prompt for Claude."""
        return """You are Claude, a helpful, harmless, and honest AI assistant created by Anthropic. 
        You are powered by Claude 4 Sonnet, which gives you advanced reasoning capabilities.
        
        Key traits:
        - Be helpful and provide accurate information
        - Ask clarifying questions when needed
        - Explain complex topics clearly
        - Admit when you're uncertain about something
        - Be conversational and engaging
        - Format responses nicely with markdown when appropriate
        
        You can help with a wide variety of tasks including:
        - Answering questions and providing information
        - Writing and editing text
        - Code review and programming help
        - Analysis and reasoning
        - Creative tasks
        - Problem-solving
        
        Always strive to be useful while being safe and ethical."""
    
    def set_system_prompt(self, system_prompt: str) -> None:
        """Set a custom system prompt."""
        self.system_prompt = system_prompt
        logger.info("System prompt updated")
    
    def add_to_conversation(self, role: str, content: str) -> None:
        """Add a message to the conversation history."""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        self.conversation_history.append(message)
        
        # Trim conversation history if it exceeds limit
        if len(self.conversation_history) > Config.CONVERSATION_HISTORY_LIMIT:
            # Keep the most recent messages
            self.conversation_history = self.conversation_history[-Config.CONVERSATION_HISTORY_LIMIT:]
    
    def get_conversation_history(self) -> List[Dict]:
        """Get the current conversation history."""
        return self.conversation_history.copy()
    
    def clear_conversation(self) -> None:
        """Clear the conversation history."""
        self.conversation_history = []
        logger.info("Conversation history cleared")
    
    def _prepare_messages(self, user_message: str) -> List[Dict]:
        """Prepare messages for the Claude API call."""
        messages = []
        
        # Add conversation history (excluding system messages)
        for msg in self.conversation_history:
            if msg["role"] in ["user", "assistant"]:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        # Add the current user message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        return messages
    
    async def generate_response(self, user_message: str, stream: bool = False) -> str:
        """
        Generate a response from Claude 4 Sonnet.
        
        Args:
            user_message: The user's input message
            stream: Whether to stream the response (for future implementation)
            
        Returns:
            Claude's response as a string
        """
        try:
            # Add user message to conversation history
            self.add_to_conversation("user", user_message)
            
            # Prepare messages for API call
            messages = self._prepare_messages(user_message)
            
            # Make API call to Claude
            response = self.client.messages.create(
                model=Config.CLAUDE_MODEL,
                max_tokens=Config.MAX_TOKENS,
                temperature=Config.TEMPERATURE,
                system=self.system_prompt,
                messages=messages
            )
            
            # Extract the response content
            assistant_response = response.content[0].text
            
            # Add assistant response to conversation history
            self.add_to_conversation("assistant", assistant_response)
            
            logger.info(f"Generated response with {len(assistant_response)} characters")
            return assistant_response
            
        except anthropic.AuthenticationError:
            error_msg = "Authentication failed. Please check your Claude API key."
            logger.error(error_msg)
            raise Exception(error_msg)
        except anthropic.RateLimitError:
            error_msg = "Rate limit exceeded. Please wait a moment before trying again."
            logger.error(error_msg)
            raise Exception(error_msg)
        except anthropic.APIError as e:
            error_msg = f"Claude API error: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def generate_response_sync(self, user_message: str) -> str:
        """
        Synchronous version of generate_response for compatibility.
        
        Args:
            user_message: The user's input message
            
        Returns:
            Claude's response as a string
        """
        try:
            # Add user message to conversation history
            self.add_to_conversation("user", user_message)
            
            # Prepare messages for API call (remove the last message since we'll add it in the API call)
            messages = []
            for msg in self.conversation_history[:-1]:  # Exclude the just-added user message
                if msg["role"] in ["user", "assistant"]:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            # Add the current user message
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            # Make API call to Claude
            response = self.client.messages.create(
                model=Config.CLAUDE_MODEL,
                max_tokens=Config.MAX_TOKENS,
                temperature=Config.TEMPERATURE,
                system=self.system_prompt,
                messages=messages
            )
            
            # Extract the response content
            assistant_response = response.content[0].text
            
            # Add assistant response to conversation history
            self.add_to_conversation("assistant", assistant_response)
            
            logger.info(f"Generated response with {len(assistant_response)} characters")
            return assistant_response
            
        except anthropic.AuthenticationError:
            error_msg = "Authentication failed. Please check your Claude API key."
            logger.error(error_msg)
            raise Exception(error_msg)
        except anthropic.RateLimitError:
            error_msg = "Rate limit exceeded. Please wait a moment before trying again."
            logger.error(error_msg)
            raise Exception(error_msg)
        except anthropic.APIError as e:
            error_msg = f"Claude API error: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def get_conversation_summary(self) -> str:
        """Get a summary of the current conversation."""
        if not self.conversation_history:
            return "No conversation history yet."
        
        message_count = len(self.conversation_history)
        user_messages = len([msg for msg in self.conversation_history if msg["role"] == "user"])
        assistant_messages = len([msg for msg in self.conversation_history if msg["role"] == "assistant"])
        
        return f"Conversation contains {message_count} messages: {user_messages} from user, {assistant_messages} from assistant."
    
    def export_conversation(self) -> str:
        """Export conversation history as JSON string."""
        return json.dumps(self.conversation_history, indent=2)
    
    def import_conversation(self, conversation_json: str) -> None:
        """Import conversation history from JSON string."""
        try:
            self.conversation_history = json.loads(conversation_json)
            logger.info("Conversation history imported successfully")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to import conversation: {e}")
            raise ValueError("Invalid JSON format for conversation import")