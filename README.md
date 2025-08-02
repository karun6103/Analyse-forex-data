# Claude AI Assistant

A modern, feature-rich web application powered by Claude 4 Sonnet LLM. This application provides an intuitive chat interface for interacting with Claude AI, complete with conversation memory, custom system prompts, and a beautiful responsive UI.

## 🌟 Features

- **Claude 4 Sonnet Integration**: Powered by the latest Claude 4 Sonnet model for advanced reasoning capabilities
- **Modern Web Interface**: Beautiful, responsive UI with dark theme and smooth animations
- **Conversation Memory**: Maintains context across multiple messages with configurable history limits
- **Custom System Prompts**: Customize Claude's behavior and personality through the settings panel
- **Message Formatting**: Supports markdown rendering with syntax highlighting for code blocks
- **Export Functionality**: Export conversation history as JSON files for backup or analysis
- **Real-time Chat**: Instant messaging with typing indicators and error handling
- **Keyboard Shortcuts**: Efficient navigation with helpful keyboard shortcuts
- **Mobile Responsive**: Optimized for desktop, tablet, and mobile devices
- **Health Monitoring**: Built-in health check and error reporting

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Claude API key from Anthropic
- pip (Python package installer)

### Installation

1. **Clone or download the project**:
   ```bash
   git clone <repository-url>
   cd claude-ai-assistant
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env and add your Claude API key
   nano .env
   ```

4. **Configure your environment**:
   Edit `.env` file and set your Claude API key:
   ```env
   CLAUDE_API_KEY=your_claude_api_key_here
   SECRET_KEY=your_secret_key_here
   ```

5. **Run the application**:
   ```bash
   python app.py
   ```

6. **Open your browser**:
   Navigate to `http://localhost:5000` to start chatting with Claude!

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `CLAUDE_API_KEY` | Your Claude API key from Anthropic | - | Yes |
| `SECRET_KEY` | Flask secret key for sessions | auto-generated | No |
| `FLASK_DEBUG` | Enable debug mode | False | No |
| `HOST` | Server host address | 0.0.0.0 | No |
| `PORT` | Server port number | 5000 | No |
| `MAX_TOKENS` | Maximum tokens per response | 4000 | No |
| `TEMPERATURE` | Response creativity (0.0-1.0) | 0.7 | No |
| `CONVERSATION_HISTORY_LIMIT` | Max messages to remember | 20 | No |

### Getting a Claude API Key

1. Visit [Anthropic's website](https://www.anthropic.com/)
2. Sign up for an account
3. Navigate to the API section
4. Generate a new API key
5. Copy the key to your `.env` file

## 🎮 Usage

### Basic Chat

1. Type your message in the input area at the bottom
2. Press **Ctrl+Enter** or click the send button
3. Claude will respond with helpful, contextual answers
4. Continue the conversation - Claude remembers previous messages

### Keyboard Shortcuts

- **Ctrl+Enter**: Send message
- **Ctrl+K**: Focus message input
- **Ctrl+L**: Clear conversation
- **Escape**: Close modals

### Settings Panel

Access the settings by clicking the "Settings" button in the header:

- **System Prompt**: Customize Claude's behavior and personality
- **View History**: See complete conversation history in a new window
- **Export History**: Download conversation as JSON file

### Features Overview

- **Clear Conversation**: Remove all messages and start fresh
- **Export**: Download current conversation as JSON
- **Responsive Design**: Works on all devices and screen sizes
- **Error Handling**: Graceful error messages and recovery

## 🏗️ Architecture

### Backend Components

- **`app.py`**: Main Flask application with API endpoints
- **`claude_ai.py`**: Core AI class handling Claude API integration
- **`config.py`**: Configuration management and validation

### Frontend Components

- **`templates/index.html`**: Main HTML template
- **`static/css/style.css`**: Modern CSS with responsive design
- **`static/js/app.js`**: JavaScript application logic

### API Endpoints

- `POST /api/chat` - Send message to Claude
- `POST /api/conversation/clear` - Clear conversation history
- `GET /api/conversation/history` - Get conversation history
- `GET /api/conversation/export` - Export conversation as JSON
- `GET/POST /api/system-prompt` - Get/update system prompt
- `GET /api/health` - Health check endpoint

## 🛠️ Development

### Running in Development Mode

```bash
# Enable debug mode
export FLASK_DEBUG=True
python app.py
```

### Project Structure

```
claude-ai-assistant/
├── app.py                 # Main Flask application
├── claude_ai.py          # Core AI functionality
├── config.py             # Configuration management
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variables template
├── README.md             # This file
├── templates/
│   └── index.html        # HTML template
└── static/
    ├── css/
    │   └── style.css     # Stylesheet
    └── js/
        └── app.js        # Frontend JavaScript
```

### Adding Features

1. **Backend**: Add new endpoints in `app.py`
2. **AI Logic**: Extend `claude_ai.py` for new AI features
3. **Frontend**: Update `app.js` and `style.css` for UI changes
4. **Configuration**: Add new settings in `config.py`

## 🚀 Deployment

### Production Setup

1. **Install Gunicorn**:
   ```bash
   pip install gunicorn
   ```

2. **Run with Gunicorn**:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

3. **Environment Configuration**:
   - Set `FLASK_DEBUG=False`
   - Use a strong, random `SECRET_KEY`
   - Configure proper logging

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

Build and run:
```bash
docker build -t claude-ai-assistant .
docker run -p 5000:5000 --env-file .env claude-ai-assistant
```

## 🔒 Security

- API keys are stored in environment variables
- Input sanitization prevents XSS attacks
- CORS protection included
- Session management with secure keys
- Error messages don't expose sensitive information

## 🐛 Troubleshooting

### Common Issues

1. **"Authentication failed"**:
   - Check your Claude API key in `.env`
   - Ensure the key is valid and active

2. **"Module not found"**:
   - Run `pip install -r requirements.txt`
   - Check Python version compatibility

3. **"Port already in use"**:
   - Change the PORT in `.env`
   - Kill existing processes using the port

4. **UI not loading**:
   - Check console for JavaScript errors
   - Ensure static files are accessible
   - Verify Flask is serving static content

### Health Check

Visit `/api/health` to verify the service status:
```json
{
  "status": "healthy",
  "model": "claude-3-5-sonnet-20241022",
  "timestamp": "2024-01-15T10:30:00"
}
```

## 📄 License

This project is open source. Feel free to modify and distribute according to your needs.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues and questions:
- Check the troubleshooting section
- Review the health check endpoint
- Ensure your Claude API key is valid
- Check the browser console for errors

## 🔮 Future Enhancements

- Real-time streaming responses
- File upload and analysis
- Multiple conversation threads
- Voice input/output
- Integration with other AI models
- Advanced conversation analytics
- Team collaboration features

---

**Built with ❤️ using Claude 4 Sonnet, Flask, and modern web technologies.**