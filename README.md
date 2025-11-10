# BINGO Tracker

A comprehensive Old School RuneScape (OSRS) bingo tracking system that integrates:
- 🎯 **Bingo Board Management** - Track team progress on custom bingo tiles
- 📱 **Discord Webhooks** - Real-time notifications for drops and completions
- 📊 **Wise Old Man Integration** - Automatic experience and achievement tracking
- 👥 **Team Competition** - Multi-team leaderboards and statistics
- 🎮 **RuneLite Plugin** - In-game drop detection and tile tracking

## Features

### 🎯 Bingo Board Tracking
- Create custom bingo boards with configurable tiles
- Track tile completion per team
- Support for item drops, experience goals, boss kills, and more
- Proof submission with image URLs
- Real-time board updates

### 📱 Discord Integration
- Automatic drop notifications with rich embeds
- Tile completion announcements
- Team leaderboard updates
- Configurable webhook URLs for different channels

### 📊 Wise Old Man Integration
- Automatic tracking of experience gains
- Boss kill count monitoring
- Achievement detection
- Competition tracking
- Scheduled player updates

### 🎮 RuneLite Plugin
- In-game drop detection
- Automatic screenshot capture
- Configurable drop filters (rarity, value)
- Whitelist/blacklist support
- Direct integration with backend server

### 👥 Team Features
- Multi-team competition support
- Team-specific tracking and leaderboards
- Individual player contributions
- Points system with configurable values

## Project Structure

```
BINGOTRACKER/
├── backend/                    # Python Flask API server
│   ├── enhanced_server.py     # Main server with all integrations
│   ├── discord_webhook.py     # Discord webhook handler
│   ├── wise_old_man.py        # Wise Old Man API client
│   ├── requirements.txt       # Python dependencies
│   └── .env.example          # Environment configuration template
│
├── frontend/                   # React web application
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── Dashboard.js   # Main dashboard with stats
│   │   │   ├── BoardView.js   # Bingo board display
│   │   │   ├── BoardTile.js   # Individual tile component
│   │   │   └── Teams.js       # Team management
│   │   └── routes/
│   │       └── bingo.jsx      # Bingo board route
│   ├── package.json           # Node dependencies
│   └── .env.example          # Frontend configuration
│
├── runelite-plugin/           # RuneLite plugin for OSRS
│   ├── src/main/java/com/bingotracker/
│   │   ├── BingoTrackerPlugin.java    # Main plugin class
│   │   └── BingoTrackerConfig.java    # Plugin configuration
│   ├── build.gradle           # Gradle build file
│   └── runelite-plugin.properties     # Plugin metadata
│
└── docs/                      # Documentation
    ├── SETUP.md              # Setup instructions
    ├── API.md                # API documentation
    └── CONFIGURATION.md      # Configuration guide
```

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 14+
- Java 11+ (for RuneLite plugin)
- MongoDB (optional, for persistent storage)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Copy and configure environment variables:
```bash
cp .env.example .env
# Edit .env with your Discord webhooks, WOM group ID, etc.
```

4. Run the server:
```bash
python enhanced_server.py
```

The server will start on `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install Node dependencies:
```bash
npm install
```

3. Copy and configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API URL
```

4. Start the development server:
```bash
npm start
```

The frontend will open at `http://localhost:3000`

### RuneLite Plugin Setup

1. Navigate to the plugin directory:
```bash
cd runelite-plugin
```

2. Build the plugin:
```bash
./gradlew build
```

3. Install in RuneLite:
   - Open RuneLite
   - Go to Plugin Hub or External Plugins
   - Load the built JAR file from `build/libs/`

4. Configure the plugin:
   - Set your server URL
   - Enter your board name and team name
   - Add Discord webhook URLs (optional)
   - Configure drop filters

## Configuration

### Discord Webhooks

Create Discord webhooks for your channels:

1. Go to Server Settings → Integrations → Webhooks
2. Create New Webhook
3. Copy the webhook URL
4. Add to `.env` file in backend

### Wise Old Man Setup

1. Create a group on [Wise Old Man](https://wiseoldman.net)
2. Add your clan members to the group
3. Copy your group ID from the URL
4. Add to `.env` file: `WOM_GROUP_ID=your_id`

### Google Sheets Integration (Optional)

For clan events functionality:

1. Create a Google Sheets API key
2. Create a public spreadsheet with event data
3. Add credentials to `.env` file

## API Endpoints

### Boards
- `POST /api/boards` - Create a new bingo board
- `GET /api/boards/<name>` - Get board data
- `PUT /api/boards/<name>/tiles/<row>/<col>` - Update tile

### Drops
- `POST /api/drops` - Record a player drop
- `GET /api/stats/drops` - Get drop statistics

### Players
- `GET /api/players/<username>/stats` - Get player stats from WOM
- `GET /api/players/<username>/gains` - Get player gains
- `POST /api/players/<username>/update` - Update player stats

### Leaderboard
- `GET /api/leaderboard/<board_name>` - Get team leaderboard

See [docs/API.md](docs/API.md) for full API documentation.

## Integration Details

### PattyRich/github-pages Integration
- Bingo board UI components
- Tile management system
- Team tracking interface
- React component library

### BossHuso/discord-rare-drop-notificater Integration
- Drop detection logic
- Discord webhook formatting
- Screenshot capture
- Rarity/value filtering

### cmsu224/clan-events Integration
- Event management framework
- Google Sheets connectivity
- Competition tracking
- Member roster management

## Credits

- **PattyRich** - Bingo board UI and tracking system
- **BossHuso** - Discord drop notification framework
- **cmsu224** - Clan events and competition management
- **Wise Old Man** - Player statistics API
- **RuneLite** - OSRS client and plugin framework
