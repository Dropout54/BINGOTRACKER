# Python-Only BINGO Tracker (Alternate Mode)

This is a **fully Python-based** implementation of the BINGO Tracker system. This alternate mode replaces:
- React frontend → Python Flask web interface (using Jinja2 templates)
- Java RuneLite plugin → Python client script that monitors OSRS
- All JavaScript → Pure Python

## Why Python-Only?

**Benefits:**
- ✅ Single language stack - easier to maintain
- ✅ Simpler deployment - no Node.js or Java required
- ✅ Unified debugging and logging
- ✅ Better integration between components
- ✅ Easier for Python developers to contribute
- ✅ Reduced build complexity
- ✅ Lower resource usage

**Trade-offs:**
- ❌ No in-game RuneLite integration (uses external monitoring)
- ❌ Requires OCR or log parsing for drop detection
- ❌ Less interactive UI compared to React
- ❌ Manual refresh instead of real-time updates (unless using WebSockets)

## Architecture

```
python-alternate/
├── server/                 # Flask backend + web interface
│   ├── app.py             # Main application
│   ├── api.py             # REST API endpoints
│   ├── models.py          # Data models
│   ├── discord_bot.py     # Discord bot (optional alternative to webhooks)
│   ├── osrs_monitor.py    # OSRS client monitoring
│   └── templates/         # Jinja2 HTML templates
│       ├── base.html
│       ├── dashboard.html
│       ├── board.html
│       └── leaderboard.html
│
├── client/                 # Python client for drop detection
│   ├── drop_monitor.py    # Main monitoring script
│   ├── ocr_reader.py      # OCR for reading game screen
│   ├── log_parser.py      # Parse OSRS client logs
│   └── screenshot.py      # Screenshot capture
│
├── utils/                  # Shared utilities
│   ├── database.py        # Database operations
│   ├── discord_webhook.py # Discord integration
│   ├── wom_api.py         # Wise Old Man API
│   └── config.py          # Configuration management
│
├── static/                 # CSS, JS, and images
│   ├── css/
│   ├── js/
│   └── images/
│
├── requirements.txt        # Python dependencies
├── config.yaml            # Configuration file
├── setup.py               # Installation script
└── README.md              # This file
```

## Features

### Implemented
- ✅ Flask web interface with Jinja2 templates
- ✅ REST API for all operations
- ✅ Discord webhook integration
- ✅ Wise Old Man API integration
- ✅ Team-based bingo tracking
- ✅ Leaderboard system
- ✅ Drop recording and statistics
- ✅ Configuration via YAML
- ✅ SQLite database (upgradeable to PostgreSQL)
- ✅ Optional Discord bot for commands

### Monitoring Options

**Option 1: Log File Monitoring (Recommended)**
- Monitors OSRS client chat logs
- Detects drops from chat messages
- No OCR required
- Works with RuneLite and official client

**Option 2: OCR-based Monitoring**
- Uses Tesseract OCR to read game screen
- Can detect drops without log files
- Requires more CPU
- Less reliable than log parsing

**Option 3: Manual Entry**
- Web interface for manual drop reporting
- Useful as backup method
- No automation required

**Option 4: Discord Bot Commands**
- Report drops via Discord commands
- Example: `!drop dwh PlayerName`
- Integrates with existing Discord server

## Installation

### Prerequisites

```bash
# Python 3.8 or higher
python --version

# Install system dependencies (for OCR option)
# Ubuntu/Debian:
sudo apt-get install tesseract-ocr

# macOS:
brew install tesseract

# Windows: Download from https://github.com/tesseract-ocr/tesseract
```

### Setup

1. **Clone or navigate to this directory:**
```bash
cd python-alternate
```

2. **Create virtual environment:**
```bash
python -m venv venv

# Activate on Linux/macOS:
source venv/bin/activate

# Activate on Windows:
venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure the application:**
```bash
cp config.example.yaml config.yaml
# Edit config.yaml with your settings
```

5. **Initialize database:**
```bash
python setup.py init-db
```

6. **Run the server:**
```bash
python server/app.py
```

The server will start on `http://localhost:8000`

## Configuration

Edit `config.yaml`:

```yaml
# Server Configuration
server:
  host: "0.0.0.0"
  port: 8000
  debug: false
  secret_key: "change-this-to-random-string"

# Database
database:
  type: "sqlite"  # or "postgresql"
  path: "data/bingo.db"  # for SQLite
  # url: "postgresql://user:pass@localhost/bingo"  # for PostgreSQL

# Discord Integration
discord:
  webhooks:
    main: "https://discord.com/api/webhooks/..."
    drops: "https://discord.com/api/webhooks/..."
    bingo: "https://discord.com/api/webhooks/..."
  
  # Optional: Discord Bot (alternative to webhooks)
  bot:
    enabled: false
    token: "your-bot-token"
    command_prefix: "!"

# Wise Old Man
wiseoldman:
  group_id: 12345
  api_url: "https://api.wiseoldman.net/v2"

# Google Sheets (optional)
google_sheets:
  enabled: false
  sheet_id: "your-sheet-id"
  api_key: "your-api-key"

# Drop Monitoring
monitoring:
  method: "logfile"  # "logfile", "ocr", "manual", or "discord"
  
  # For logfile method
  logfile:
    path: "~/.runelite/chatlogs"  # RuneLite chat logs
    scan_interval: 5  # seconds
  
  # For OCR method
  ocr:
    region: [100, 100, 400, 300]  # [x, y, width, height]
    scan_interval: 10  # seconds
    tesseract_path: "/usr/bin/tesseract"
  
  # Drop filters
  filters:
    min_rarity: 64  # 1/64
    min_value: 10000  # GP
    whitelist:
      - "Dragon warhammer"
      - "Twisted bow"
    blacklist:
      - "Coins"
      - "Pure essence"
    always_unique: true

# Security
security:
  password_hash_rounds: 12
  session_timeout: 3600  # seconds
  max_login_attempts: 5
```

## Usage

### Starting the Server

**Development mode:**
```bash
python server/app.py
```

**Production mode:**
```bash
# Using gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 server.app:app

# Or using waitress
waitress-serve --host=0.0.0.0 --port=8000 server.app:app
```

### Starting the Drop Monitor

**Log file monitoring (recommended):**
```bash
python client/drop_monitor.py --method logfile
```

**OCR monitoring:**
```bash
python client/drop_monitor.py --method ocr
```

**Run as background service:**
```bash
# Linux/macOS
nohup python client/drop_monitor.py &

# Or use systemd service (see setup.py)
python setup.py install-service
```

### Using the Web Interface

1. **Access the dashboard:**
   - Navigate to `http://localhost:8000`

2. **Create a bingo board:**
   - Go to "Create Board"
   - Fill in board details, teams, and tiles
   - Set passwords for admin and general access

3. **Track progress:**
   - Select your board
   - Click tiles to mark as complete
   - Upload proof images
   - View team standings

4. **View statistics:**
   - Dashboard shows recent drops
   - Leaderboard displays team rankings
   - Statistics page shows detailed metrics

### Using the API

**Create a board:**
```bash
curl -X POST http://localhost:8000/api/boards \
  -H "Content-Type: application/json" \
  -d '{
    "boardName": "Test Board",
    "adminPassword": "admin123",
    "generalPassword": "player123",
    "teams": [{"name": "Team A", "color": "#ff0000"}],
    "boardData": [[{"title": "Test Tile", "points": 10}]]
  }'
```

**Record a drop:**
```bash
curl -X POST http://localhost:8000/api/drops \
  -H "Content-Type: application/json" \
  -d '{
    "playerName": "TestPlayer",
    "itemName": "Dragon warhammer",
    "quantity": 1,
    "teamName": "Team A"
  }'
```

**Get leaderboard:**
```bash
curl http://localhost:8000/api/leaderboard/TestBoard
```

### Using Discord Bot (Optional)

If you enable the Discord bot, you can use commands:

```
!drop <item> [player] - Report a drop
!board <name> - View board status
!leaderboard - Show team rankings
!tile <row> <col> - Mark tile complete
!stats - View statistics
```

## Monitoring OSRS

### Method 1: Log File Monitoring (Recommended)

RuneLite saves chat logs to `~/.runelite/chatlogs/`. The monitor watches these files for drop messages:

```bash
# Start monitoring
python client/drop_monitor.py --method logfile --path ~/.runelite/chatlogs
```

**Configuration:**
```yaml
monitoring:
  method: "logfile"
  logfile:
    path: "~/.runelite/chatlogs"
    scan_interval: 5
    patterns:
      - "Valuable drop:"
      - "Untradeable drop:"
      - "You have a funny feeling"
```

### Method 2: OCR Monitoring

Uses Tesseract OCR to read the game window:

```bash
# Start OCR monitoring
python client/drop_monitor.py --method ocr
```

**Requirements:**
- Tesseract OCR installed
- OSRS window visible on screen
- Configured screen region

**Configuration:**
```yaml
monitoring:
  method: "ocr"
  ocr:
    region: [100, 100, 400, 300]  # Adjust for your screen
    scan_interval: 10
    confidence: 0.8
```

**Tips:**
- Adjust region to cover chat area
- Use fixed window size for consistency
- Increase confidence for fewer false positives

### Method 3: Manual Entry

Simple web form for manual drop reporting:

1. Go to `http://localhost:8000/report`
2. Fill in player name, item, quantity
3. Upload screenshot (optional)
4. Submit

### Method 4: Discord Bot

Report drops via Discord:

```
!drop Dragon warhammer PlayerName
```

Bot confirms and sends to server automatically.

## Database Management

### SQLite (Default)

**Backup:**
```bash
python setup.py backup-db
```

**Restore:**
```bash
python setup.py restore-db backup.db
```

### PostgreSQL (Production)

**Setup:**
```yaml
database:
  type: "postgresql"
  url: "postgresql://user:password@localhost/bingo"
```

**Migrate:**
```bash
python setup.py migrate-db
```

## Development

### Project Structure

```python
# server/app.py - Main Flask application
# Handles routing, templates, and coordination

# server/api.py - REST API endpoints
# All /api/* routes for programmatic access

# server/models.py - Data models
# Board, Team, Tile, Drop, Player classes

# client/drop_monitor.py - Drop detection
# Monitors game and sends drops to server

# utils/ - Shared utilities
# Reusable components for both server and client
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/

# With coverage
pytest --cov=server --cov=client tests/
```

### Code Style

```bash
# Format code
black server/ client/ utils/

# Lint
flake8 server/ client/ utils/

# Type checking
mypy server/ client/ utils/
```

## Deployment

### Docker

```bash
# Build image
docker build -t bingo-tracker .

# Run container
docker run -d -p 8000:8000 \
  -v $(pwd)/config.yaml:/app/config.yaml \
  -v $(pwd)/data:/app/data \
  bingo-tracker
```

### Docker Compose

```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./config.yaml:/app/config.yaml
      - ./data:/app/data
    environment:
      - FLASK_ENV=production
  
  postgres:
    image: postgres:13
    environment:
      - POSTGRES_DB=bingo
      - POSTGRES_USER=bingo
      - POSTGRES_PASSWORD=secret
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Systemd Service

```bash
# Install as system service
sudo python setup.py install-service

# Start service
sudo systemctl start bingo-tracker

# Enable on boot
sudo systemctl enable bingo-tracker
```

## Troubleshooting

### Server won't start

**Check port availability:**
```bash
netstat -tuln | grep 8000
```

**Check logs:**
```bash
tail -f logs/bingo-tracker.log
```

**Verify configuration:**
```bash
python setup.py verify-config
```

### Drop monitoring not working

**Log file method:**
- Verify log path: `ls ~/.runelite/chatlogs/`
- Check permissions
- Ensure RuneLite chat logging is enabled

**OCR method:**
- Test Tesseract: `tesseract --version`
- Verify screen region
- Check OCR output: `python client/ocr_reader.py --test`

**General:**
- Check server connection: `curl http://localhost:8000/api/health`
- Verify filters in config.yaml
- Check monitor logs: `tail -f logs/monitor.log`

### Discord notifications not sending

**Test webhook:**
```bash
curl -X POST <webhook-url> \
  -H "Content-Type: application/json" \
  -d '{"content":"Test message"}'
```

**Check configuration:**
- Verify webhook URL format
- Test in config: `python setup.py test-discord`
- Check Discord server permissions

### Database errors

**SQLite:**
```bash
# Check database integrity
sqlite3 data/bingo.db "PRAGMA integrity_check;"

# Reset database
python setup.py reset-db
```

**PostgreSQL:**
```bash
# Check connection
psql -h localhost -U bingo -d bingo

# Run migrations
python setup.py migrate-db
```

### Performance issues

**Too many drops:**
- Increase filters (min_rarity, min_value)
- Use blacklist for common items

**Slow web interface:**
- Enable caching
- Use PostgreSQL instead of SQLite
- Add Redis for session storage

**High CPU usage:**
- Reduce OCR scan_interval
- Use logfile method instead of OCR
- Optimize database queries

## Expanding the System

### Adding New Tile Types

Edit `server/models.py`:

```python
class TileType:
    ITEM = "item"
    SKILL = "skill"
    BOSS = "boss"
    QUEST = "quest"  # NEW
    DIARY = "diary"  # NEW
    
    @staticmethod
    def check_completion(tile, player_data):
        if tile.type == TileType.QUEST:
            return check_quest_completion(tile, player_data)
        # ... existing checks
```

### Adding Custom Discord Commands

Edit `server/discord_bot.py`:

```python
@bot.command(name='custom')
async def custom_command(ctx, arg):
    """Your custom command"""
    # Implementation
    await ctx.send(f"Custom command executed: {arg}")
```

### Adding New Monitoring Methods

Create `client/custom_monitor.py`:

```python
from client.base_monitor import BaseMonitor

class CustomMonitor(BaseMonitor):
    def __init__(self, config):
        super().__init__(config)
    
    def detect_drops(self):
        # Your detection logic
        pass
```

Register in `client/drop_monitor.py`:

```python
MONITORS = {
    'logfile': LogFileMonitor,
    'ocr': OCRMonitor,
    'custom': CustomMonitor,  # NEW
}
```

### Adding New API Endpoints

Edit `server/api.py`:

```python
@api_bp.route('/custom-endpoint', methods=['POST'])
def custom_endpoint():
    data = request.json
    # Process data
    return jsonify({'status': 'success'})
```

### Custom Web Templates

Create `server/templates/custom.html`:

```html
{% extends "base.html" %}
{% block content %}
<h1>Custom Page</h1>
<!-- Your content -->
{% endblock %}
```

Add route in `server/app.py`:

```python
@app.route('/custom')
def custom_page():
    return render_template('custom.html')
```

## API Reference

See `API_REFERENCE.md` for complete API documentation.

## Performance Optimization

### Caching

```yaml
cache:
  enabled: true
  type: "redis"
  url: "redis://localhost:6379"
  ttl: 300  # seconds
```

### Database Optimization

```python
# Use connection pooling
database:
  pool_size: 10
  max_overflow: 20
  pool_timeout: 30
```

### Async Processing

```yaml
async:
  enabled: true
  workers: 4
  queue: "redis"
```

## Security Considerations

1. **Change default passwords** in config.yaml
2. **Use HTTPS** in production
3. **Enable rate limiting** for API
4. **Secure Discord webhooks** (keep URLs private)
5. **Hash passwords** (bcrypt with 12 rounds)
6. **Validate all inputs** (sanitize user data)
7. **Use environment variables** for secrets

## Contributing

To contribute to the Python-alternate mode:

1. Fork the repository
2. Create feature branch
3. Make changes in `python-alternate/`
4. Add tests
5. Run linters and tests
6. Submit pull request

## License

Same as main project. See parent LICENSE file.

## Support

For issues specific to Python-alternate mode:
- Check troubleshooting section above
- Review logs in `logs/`
- Test configuration: `python setup.py verify-all`
- Open issue with `[Python-Alternate]` prefix

## Comparison with Main Project

| Feature | Main Project | Python-Alternate |
|---------|-------------|------------------|
| Frontend | React | Flask + Jinja2 |
| Backend | Python Flask | Python Flask |
| Plugin | Java (RuneLite) | Python Client |
| Drop Detection | In-game (RuneLite) | Log/OCR/Manual |
| Real-time Updates | WebSocket | Polling/SSE |
| Database | MongoDB (optional) | SQLite/PostgreSQL |
| Deployment | Multi-service | Single service |
| Learning Curve | Higher (3 languages) | Lower (1 language) |
| Performance | Better UI | Lower overhead |
| Customization | Moderate | High (all Python) |

Choose the main project if:
- You need in-game RuneLite integration
- You prefer modern React UI
- You have React/Java expertise

Choose Python-alternate if:
- You prefer single-language stack
- Simpler deployment is priority
- You're comfortable with Python
- Don't need in-game plugin

## Future Enhancements

- [ ] WebSocket support for real-time updates
- [ ] Mobile-responsive templates
- [ ] Advanced analytics dashboard
- [ ] Export/import board configurations
- [ ] Multi-language support
- [ ] Plugin system for custom integrations
- [ ] RESTful API versioning
- [ ] GraphQL endpoint
- [ ] Automated testing CI/CD
- [ ] Performance monitoring

## Changelog

### v1.0.0 (Initial Release)
- Complete Python rewrite
- Flask web interface
- Log file monitoring
- OCR monitoring option
- Discord integration
- Wise Old Man integration
- Team tracking
- Leaderboards
