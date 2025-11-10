# Configuration Guide

This guide covers all configuration options for the BINGO Tracker system.

## Backend Configuration

### Environment Variables

Create a `.env` file in the `backend/` directory with the following variables:

#### Discord Webhooks

```env
# Main webhook for general announcements
DISCORD_WEBHOOK_MAIN=https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN

# Webhook for drop notifications
DISCORD_WEBHOOK_DROPS=https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN

# Webhook for bingo-specific events
DISCORD_WEBHOOK_BINGO=https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN
```

**How to create Discord webhooks:**

1. Open your Discord server
2. Go to Server Settings → Integrations
3. Click "Webhooks" → "New Webhook"
4. Give it a name and select the channel
5. Copy the Webhook URL
6. Paste into your `.env` file

#### Wise Old Man

```env
# Your Wise Old Man group ID
WOM_GROUP_ID=12345
```

**How to find your group ID:**

1. Go to [WiseOldMan.net](https://wiseoldman.net)
2. Navigate to your group page
3. The group ID is in the URL: `wiseoldman.net/groups/12345`

#### Google Sheets (Optional)

```env
# For clan events integration
GOOGLE_SHEETS_ID=1YMcXxSL3s1NEzsPVMMkPn7EdGNFKENiwqNyDKkJTO80
GOOGLE_API_KEY=AIzaSyC1234567890abcdefghijklmnop
```

**How to set up Google Sheets API:**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google Sheets API
4. Create credentials (API Key)
5. Make your spreadsheet public
6. Copy the sheet ID from URL

#### Server Settings

```env
# Port to run the server on
PORT=5000

# Enable debug mode (set to False in production)
DEBUG=True
```

#### Database (Optional)

```env
# MongoDB connection string
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB=bingo
```

---

## Frontend Configuration

### Environment Variables

Create a `.env` file in the `frontend/` directory:

```env
# Backend API URL
REACT_APP_API_URL=http://localhost:5000/api
```

For production deployment, change this to your production API URL:

```env
REACT_APP_API_URL=https://your-domain.com/api
```

---

## RuneLite Plugin Configuration

The plugin is configured through the RuneLite settings panel after installation.

### Server Settings

**Server URL:**
- Local: `http://localhost:5000`
- Production: `https://your-domain.com`

**Board Name:**
- Enter the exact name of your bingo board
- Case-sensitive
- Must match the board created in the web interface

**Team Name:**
- Your team's name
- Must match one of the teams in the board

**Board Password:**
- The general password for the board
- Required to update tiles

### Discord Webhooks

**Webhook URL(s):**
- One webhook URL per line
- Can add multiple webhooks
- Each webhook receives the same notifications

**Send Embeds:**
- Enabled: Rich formatted messages
- Disabled: Plain text messages

**Send Screenshots:**
- Enabled: Automatically captures and sends screenshots
- Disabled: No screenshots attached

**Send to Server:**
- Enabled: Sends drops to backend server
- Disabled: Only sends to Discord webhooks

### Bingo Settings

**Auto-Check Tiles:**
- Enabled: Automatically marks tiles complete when conditions met
- Disabled: Manual tile checking only

**Notify on Completion:**
- Enabled: Sends Discord notification when you complete a tile
- Disabled: Silent tile completion

### Drop Filters

**Min Rarity (1/x):**
- Default: 64 (items with 1/64 or rarer drop rate)
- Lower number = more common items included
- Higher number = only rarer items

**Min Value (GP):**
- Default: 10000
- Items worth less than this value are ignored
- Set to 0 to include all items

**Whitelisted Items:**
- One item per line
- Always notified regardless of filters
- Example:
  ```
  Dragon warhammer
  Twisted bow
  Scythe of vitur
  ```

**Blacklisted Items:**
- One item per line
- Never notified regardless of filters
- Example:
  ```
  Coins
  Pure essence
  Grimy herbs
  ```

**Always Send Uniques:**
- Enabled: Always notify for unique items (sigils, uniques, etc.)
- Disabled: Apply normal filters to all items

---

## Board Configuration

### Creating a Board

Boards are created through the web interface or API. A board configuration includes:

**Board Details:**
```json
{
  "boardName": "Fall 2025 Bingo",
  "adminPassword": "admin-secret-123",
  "generalPassword": "player-pass-456"
}
```

**Teams:**
```json
{
  "teams": [
    {
      "name": "Team Red",
      "color": "#ff0000",
      "members": ["Player1", "Player2"]
    },
    {
      "name": "Team Blue",
      "color": "#0000ff",
      "members": ["Player3", "Player4"]
    }
  ]
}
```

**Tiles:**

Each tile should have:

```json
{
  "title": "Get 99 Attack",
  "description": "Reach level 99 in Attack",
  "points": 50,
  "type": "skill",
  "requirement": {
    "skill": "attack",
    "level": 99
  },
  "image": "https://example.com/attack-icon.png"
}
```

**Tile Types:**

1. **Item Drops:**
```json
{
  "type": "item",
  "requirement": {
    "item": "Dragon warhammer",
    "quantity": 1
  }
}
```

2. **Skill Levels:**
```json
{
  "type": "skill",
  "requirement": {
    "skill": "attack",
    "level": 99
  }
}
```

3. **Boss Kills:**
```json
{
  "type": "boss",
  "requirement": {
    "boss": "zulrah",
    "kc": 100
  }
}
```

4. **Experience Gains:**
```json
{
  "type": "experience",
  "requirement": {
    "skill": "mining",
    "xp": 1000000
  }
}
```

5. **Achievements:**
```json
{
  "type": "achievement",
  "requirement": {
    "achievement": "Combat Achievements - Hard"
  }
}
```

---

## Advanced Configuration

### Custom Integrations

You can extend the system with custom integrations:

1. **Custom Discord Bot:**
   - Use the Discord API directly
   - Implement custom commands
   - Add reaction-based interactions

2. **Database Integration:**
   - Add MongoDB for persistence
   - Configure connection in `.env`
   - Automatic data migration

3. **Multiple Boards:**
   - Run multiple competitions simultaneously
   - Separate webhooks per board
   - Independent team tracking

### Scheduled Tasks

Set up cron jobs or scheduled tasks for:

**Player Updates (every hour):**
```bash
0 * * * * curl -X POST http://localhost:5000/api/players/Player1/update
```

**Leaderboard Snapshots (daily):**
```bash
0 0 * * * curl http://localhost:5000/api/leaderboard/MyBoard > /path/to/backup.json
```

**Auto-checking Tiles (every 15 minutes):**
```bash
*/15 * * * * curl -X POST http://localhost:5000/api/tiles/check -d @players.json
```

---

## Security Best Practices

1. **Use Strong Passwords:**
   - Admin password should be complex
   - Different from general password
   - Don't share admin password

2. **Secure Webhooks:**
   - Keep webhook URLs private
   - Regenerate if leaked
   - Use separate webhooks for different purposes

3. **Environment Variables:**
   - Never commit `.env` files
   - Use different values for dev/prod
   - Rotate API keys periodically

4. **API Access:**
   - Implement rate limiting in production
   - Use HTTPS for production
   - Consider adding authentication

---

## Troubleshooting Configuration

### Backend not starting

- Check all required environment variables are set
- Verify Discord webhook URLs are valid
- Test MongoDB connection (if using)
- Check port is not already in use

### Frontend can't connect to backend

- Verify `REACT_APP_API_URL` is correct
- Check backend is running
- Test with curl: `curl http://localhost:5000/api/health`
- Check CORS settings

### Plugin not sending data

- Verify server URL is accessible from your network
- Check firewall settings
- Test webhook URLs separately
- Enable plugin debug logging

### Discord notifications not working

- Test webhook with: `curl -X POST <webhook-url> -H "Content-Type: application/json" -d '{"content":"test"}'`
- Check webhook URL format
- Verify webhook permissions in Discord
- Check rate limits

---

## Performance Tuning

### Backend

```env
# Increase worker processes for production
WORKERS=4

# Enable caching
CACHE_TYPE=redis
CACHE_REDIS_URL=redis://localhost:6379

# Database connection pooling
MONGODB_MAX_POOL_SIZE=100
```

### Frontend

```bash
# Production build optimization
npm run build -- --production

# Enable service worker for caching
# Edit src/index.js to register service worker
```

### Plugin

- Reduce screenshot quality for faster uploads
- Batch API calls when possible
- Cache item prices locally
- Implement exponential backoff for retries

---

## Examples

See the `examples/` directory for sample configurations:

- `example-board.json` - Complete board configuration
- `example-tiles.json` - Various tile types
- `example-teams.json` - Team setup
- `.env.example` - Environment template
