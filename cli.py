#!/usr/bin/env python3
"""
Claude AI CLI - Command Line Interface for Claude 4 Sonnet
"""

import argparse
import sys
import os
from claude_ai import ClaudeAI
from config import Config
import readline
import json
from datetime import datetime

class ClaudeCLI:
    """Command Line Interface for Claude AI."""
    
    def __init__(self):
        """Initialize the CLI."""
        try:
            self.ai = ClaudeAI()
            self.running = True
            self.setup_readline()
            print("🤖 Claude AI CLI initialized successfully!")
            print(f"Model: {Config.CLAUDE_MODEL}")
            print("Type 'help' for available commands or start chatting!")
            print("-" * 60)
        except Exception as e:
            print(f"❌ Error initializing Claude AI: {e}")
            sys.exit(1)
    
    def setup_readline(self):
        """Setup readline for better input experience."""
        try:
            # Enable history
            history_file = os.path.expanduser("~/.claude_ai_history")
            try:
                readline.read_history_file(history_file)
            except FileNotFoundError:
                pass
            
            # Save history on exit
            import atexit
            atexit.register(readline.write_history_file, history_file)
            
            # Set history length
            readline.set_history_length(1000)
            
        except ImportError:
            # readline not available on all systems
            pass
    
    def print_help(self):
        """Print available commands."""
        help_text = """
Available Commands:
  help                 - Show this help message
  clear               - Clear conversation history
  history             - Show conversation history
  export <filename>   - Export conversation to JSON file
  prompt <text>       - Set custom system prompt
  show-prompt         - Show current system prompt
  stats               - Show conversation statistics
  quit/exit           - Exit the application
  
Chat Commands:
  Just type your message and press Enter to chat with Claude!
  
Tips:
  - Use Ctrl+C to interrupt long responses
  - Use arrow keys to navigate command history
  - Multi-line input: end lines with '\\' to continue
        """
        print(help_text)
    
    def get_multiline_input(self, prompt="You: "):
        """Get potentially multi-line input from user."""
        lines = []
        while True:
            try:
                if not lines:
                    line = input(prompt)
                else:
                    line = input("... ")
                
                if line.endswith('\\'):
                    lines.append(line[:-1])
                    continue
                else:
                    lines.append(line)
                    break
                    
            except (EOFError, KeyboardInterrupt):
                if lines:
                    print("\n[Input cancelled]")
                    return None
                raise
        
        return '\n'.join(lines).strip()
    
    def format_response(self, text, width=80):
        """Format response text for terminal display."""
        import textwrap
        
        # Simple markdown-like formatting for terminal
        lines = text.split('\n')
        formatted_lines = []
        
        for line in lines:
            if line.startswith('# '):
                # Header
                formatted_lines.append(f"\n{'='*width}")
                formatted_lines.append(f"  {line[2:].upper()}")
                formatted_lines.append('='*width)
            elif line.startswith('## '):
                # Subheader
                formatted_lines.append(f"\n{'-'*width}")
                formatted_lines.append(f"  {line[3:]}")
                formatted_lines.append('-'*width)
            elif line.startswith('```'):
                # Code block marker
                formatted_lines.append('┌' + '─'*(width-2) + '┐')
                if len(line) > 3:
                    formatted_lines.append(f"│ {line[3:].ljust(width-4)} │")
            elif line.strip().startswith('- '):
                # List item
                wrapped = textwrap.fill(line, width-2, initial_indent='  • ', subsequent_indent='    ')
                formatted_lines.append(wrapped)
            else:
                # Regular text
                if line.strip():
                    wrapped = textwrap.fill(line, width)
                    formatted_lines.append(wrapped)
                else:
                    formatted_lines.append('')
        
        return '\n'.join(formatted_lines)
    
    def clear_conversation(self):
        """Clear conversation history."""
        self.ai.clear_conversation()
        print("✅ Conversation history cleared.")
    
    def show_history(self):
        """Show conversation history."""
        history = self.ai.get_conversation_history()
        if not history:
            print("No conversation history.")
            return
        
        print(f"\n📋 Conversation History ({len(history)} messages):")
        print("=" * 60)
        
        for i, msg in enumerate(history, 1):
            role = msg['role'].upper()
            timestamp = msg.get('timestamp', 'Unknown time')
            content = msg['content'][:100] + ('...' if len(msg['content']) > 100 else '')
            
            print(f"{i:2d}. [{role}] {timestamp}")
            print(f"    {content}")
            print()
    
    def export_conversation(self, filename=None):
        """Export conversation to JSON file."""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"claude_conversation_{timestamp}.json"
        
        try:
            conversation_json = self.ai.export_conversation()
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(conversation_json)
            print(f"✅ Conversation exported to {filename}")
        except Exception as e:
            print(f"❌ Error exporting conversation: {e}")
    
    def set_system_prompt(self, prompt):
        """Set custom system prompt."""
        if not prompt.strip():
            print("❌ System prompt cannot be empty.")
            return
        
        self.ai.set_system_prompt(prompt)
        print("✅ System prompt updated.")
    
    def show_system_prompt(self):
        """Show current system prompt."""
        print("\n📝 Current System Prompt:")
        print("-" * 40)
        print(self.ai.system_prompt)
        print("-" * 40)
    
    def show_stats(self):
        """Show conversation statistics."""
        summary = self.ai.get_conversation_summary()
        history = self.ai.get_conversation_history()
        
        if not history:
            print("No conversation data available.")
            return
        
        user_messages = len([m for m in history if m['role'] == 'user'])
        assistant_messages = len([m for m in history if m['role'] == 'assistant'])
        total_chars = sum(len(m['content']) for m in history)
        
        print(f"\n📊 Conversation Statistics:")
        print(f"   Total messages: {len(history)}")
        print(f"   User messages: {user_messages}")
        print(f"   Assistant messages: {assistant_messages}")
        print(f"   Total characters: {total_chars:,}")
        print(f"   Average message length: {total_chars // len(history) if history else 0} chars")
        print(f"   Summary: {summary}")
    
    def process_command(self, user_input):
        """Process user commands."""
        parts = user_input.strip().split(maxsplit=1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        if command in ['help', '?']:
            self.print_help()
        elif command == 'clear':
            self.clear_conversation()
        elif command == 'history':
            self.show_history()
        elif command == 'export':
            self.export_conversation(args if args else None)
        elif command == 'prompt':
            if args:
                self.set_system_prompt(args)
            else:
                print("Usage: prompt <your custom prompt>")
        elif command == 'show-prompt':
            self.show_system_prompt()
        elif command == 'stats':
            self.show_stats()
        elif command in ['quit', 'exit']:
            print("👋 Goodbye!")
            self.running = False
        else:
            return False  # Not a command
        
        return True  # Was a command
    
    def chat_loop(self):
        """Main chat loop."""
        while self.running:
            try:
                user_input = self.get_multiline_input("You: ")
                
                if user_input is None:
                    continue
                
                if not user_input:
                    continue
                
                # Check if it's a command
                if user_input.startswith('/') or self.process_command(user_input):
                    continue
                
                # Send to Claude
                print("\nClaude: ", end="", flush=True)
                try:
                    response = self.ai.generate_response_sync(user_input)
                    formatted_response = self.format_response(response)
                    print(formatted_response)
                    print()
                    
                except KeyboardInterrupt:
                    print("\n[Response interrupted]")
                    continue
                except Exception as e:
                    print(f"\n❌ Error: {e}")
                    continue
                    
            except (EOFError, KeyboardInterrupt):
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                continue

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Claude AI CLI - Command Line Interface for Claude 4 Sonnet",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py                    # Start interactive chat
  python cli.py --help            # Show this help
  
Commands within the CLI:
  help                            # Show available commands
  clear                           # Clear conversation
  export myconvo.json             # Export conversation
  prompt "You are a helpful assistant"  # Set system prompt
        """
    )
    
    parser.add_argument(
        '--version', 
        action='version', 
        version='Claude AI CLI 1.0.0'
    )
    
    args = parser.parse_args()
    
    # Check for required environment variables
    try:
        Config.validate_config()
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("Please set your CLAUDE_API_KEY in the .env file or environment variables.")
        sys.exit(1)
    
    try:
        cli = ClaudeCLI()
        cli.chat_loop()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()