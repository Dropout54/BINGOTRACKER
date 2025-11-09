# BINGO Tracker API Documentation

## Base URL

```
http://localhost:5000/api
```

## Authentication

Currently, board operations require a password that is validated on each request. Future versions may implement JWT or OAuth2.

## Endpoints

### Health Check

#### GET /health

Check server health and service availability.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-09T04:00:00.000Z",
  "services": {
    "discord": true,
    "wom": true,
    "google_sheets": false
  }
}
```

---

### Boards

#### POST /boards

Create a new bingo board.

**Request Body:**
```json
{
  "boardName": "Fall 2025 Bingo",
  "adminPassword": "admin123",
  "generalPassword": "player123",
  "teams": [
    {"name": "Team Red", "color": "#ff0000"},
    {"name": "Team Blue", "color": "#0000ff"}
  ],
  "boardData": [
    [
      {
        "title": "Get Dragon Warhammer",
        "description": "Obtain a Dragon Warhammer drop",
        "points": 100,
        "type": "item",
        "image": "https://example.com/dwh.png"
      }
    ]
  ]
}
```

**Response:**
```json
{
  "message": "Board created successfully",
  "boardName": "Fall 2025 Bingo"
}
```

#### GET /boards/:boardName

Get board data.

**Response:**
```json
{
  "boardName": "Fall 2025 Bingo",
  "boardData": [...],
  "teams": [...],
  "teamData": {
    "Team Red": [...],
    "Team Blue": [...]
  },
  "createdAt": "2025-11-09T04:00:00.000Z",
  "lastUpdated": "2025-11-09T05:00:00.000Z"
}
```

#### PUT /boards/:boardName/tiles/:row/:col

Update a tile's completion status.

**Request Body:**
```json
{
  "teamName": "Team Red",
  "password": "player123",
  "checked": true,
  "proof": "https://i.imgur.com/example.png",
  "currPoints": 100,
  "completedBy": "PlayerName",
  "notifyDiscord": true
}
```

**Response:**
```json
{
  "message": "Tile updated",
  "tile": {
    "checked": true,
    "proof": "https://i.imgur.com/example.png",
    "currPoints": 100,
    "completedBy": "PlayerName",
    "completedAt": "2025-11-09T05:00:00.000Z"
  }
}
```

---

### Drops

#### POST /drops

Record a player's item drop.

**Request Body:**
```json
{
  "playerName": "PlayerName",
  "itemName": "Dragon Warhammer",
  "quantity": 1,
  "rarity": "1/5000",
  "value": 50000000,
  "screenshot": "https://i.imgur.com/example.png",
  "teamName": "Team Red"
}
```

**Response:**
```json
{
  "message": "Drop recorded",
  "drop": {
    "playerName": "PlayerName",
    "itemName": "Dragon Warhammer",
    "quantity": 1,
    "rarity": "1/5000",
    "value": 50000000,
    "screenshot": "https://i.imgur.com/example.png",
    "teamName": "Team Red",
    "timestamp": "2025-11-09T05:00:00.000Z"
  }
}
```

#### GET /stats/drops

Get drop statistics.

**Response:**
```json
{
  "total_drops": 150,
  "unique_players": 25,
  "recent_drops": [
    {
      "playerName": "PlayerName",
      "itemName": "Dragon Warhammer",
      "quantity": 1,
      "rarity": "1/5000",
      "value": 50000000,
      "screenshot": "https://i.imgur.com/example.png",
      "teamName": "Team Red",
      "timestamp": "2025-11-09T05:00:00.000Z"
    }
  ]
}
```

---

### Players (Wise Old Man Integration)

#### GET /players/:username/stats

Get player statistics from Wise Old Man.

**Response:**
```json
{
  "username": "PlayerName",
  "displayName": "PlayerName",
  "type": "regular",
  "latestSnapshot": {
    "data": {
      "attack": {
        "rank": 12345,
        "level": 99,
        "experience": 13034431
      },
      "overall": {
        "rank": 5000,
        "level": 2277,
        "experience": 500000000
      }
    }
  }
}
```

#### GET /players/:username/gains

Get player gains for a period.

**Query Parameters:**
- `period` (optional): day, week, month, year (default: week)

**Response:**
```json
{
  "data": {
    "attack": {
      "experience": {
        "gained": 150000
      }
    }
  }
}
```

#### POST /players/:username/update

Update player stats from OSRS highscores.

**Response:**
```json
{
  "message": "Player updated successfully"
}
```

---

### Tiles Tracking

#### POST /tiles/check

Check which tiles players have completed based on Wise Old Man data.

**Request Body:**
```json
{
  "players": ["Player1", "Player2"],
  "tiles": [
    {
      "type": "skill",
      "skill": "attack",
      "level": 99
    },
    {
      "type": "boss",
      "boss": "zulrah",
      "kc": 100
    }
  ]
}
```

**Response:**
```json
{
  "Player1": [
    {
      "type": "skill",
      "skill": "attack",
      "level": 99
    }
  ],
  "Player2": []
}
```

---

### Leaderboard

#### GET /leaderboard/:boardName

Get team leaderboard for a board.

**Response:**
```json
[
  {
    "team": "Team Red",
    "points": 450,
    "completed": 15,
    "color": "#ff0000"
  },
  {
    "team": "Team Blue",
    "points": 380,
    "completed": 12,
    "color": "#0000ff"
  }
]
```

---

### Webhooks

#### POST /webhook/test

Test a Discord webhook.

**Request Body:**
```json
{
  "webhook": "main"
}
```

**Response:**
```json
{
  "message": "Webhook test successful"
}
```

---

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "message": "Error description"
}
```

Common HTTP status codes:
- `200` - Success
- `400` - Bad Request (invalid parameters)
- `404` - Not Found
- `500` - Internal Server Error

---

## Rate Limiting

Currently no rate limiting is implemented. Future versions may include rate limits per IP or API key.

---

## Webhooks (Discord)

The server can send notifications to Discord via webhooks. Configure webhook URLs in the `.env` file:

```
DISCORD_WEBHOOK_MAIN=https://discord.com/api/webhooks/...
DISCORD_WEBHOOK_DROPS=https://discord.com/api/webhooks/...
DISCORD_WEBHOOK_BINGO=https://discord.com/api/webhooks/...
```

### Webhook Events

1. **Drop Notifications** - Sent to `drops` webhook
2. **Tile Completions** - Sent to `bingo` webhook
3. **Bingo Achievements** - Sent to `bingo` webhook
4. **Board Creation** - Sent to `main` webhook

---

## Integration with RuneLite Plugin

The RuneLite plugin communicates with the backend via the `/api/drops` endpoint. When a player receives a drop in-game:

1. Plugin detects the drop
2. Captures screenshot (if enabled)
3. Sends POST request to `/api/drops`
4. Backend records drop and sends Discord notification

---

## Wise Old Man Integration

The backend automatically:
- Fetches player stats on request
- Checks tile completion based on WOM data
- Updates players periodically (can be scheduled)
- Tracks competitions and achievements

---

## Future Enhancements

- [ ] JWT authentication
- [ ] API keys for external integrations
- [ ] WebSocket support for real-time updates
- [ ] Batch operations for tile updates
- [ ] Export/import board configurations
- [ ] Advanced filtering and search
