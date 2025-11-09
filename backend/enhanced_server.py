"""
Enhanced BINGO Tracker Server
Integrates Discord webhooks, Wise Old Man API, and team tracking
"""
from flask import Flask, jsonify, Response, request, abort
from flask_cors import CORS, cross_origin
import json
import datetime
import time
import requests
import os
from typing import Dict, List, Optional

# Import our custom modules
from discord_webhook import DiscordWebhook, WebhookManager
from wise_old_man import WiseOldManAPI

app = Flask(__name__, static_folder='../frontend/build')
CORS(app)

# Configuration
WEBHOOK_CONFIG = {
    'main': os.getenv('DISCORD_WEBHOOK_MAIN', ''),
    'drops': os.getenv('DISCORD_WEBHOOK_DROPS', ''),
    'bingo': os.getenv('DISCORD_WEBHOOK_BINGO', '')
}

WOM_GROUP_ID = os.getenv('WOM_GROUP_ID')
GOOGLE_SHEETS_ID = os.getenv('GOOGLE_SHEETS_ID', '')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')

# Initialize services
webhook_manager = WebhookManager(WEBHOOK_CONFIG)
wom_api = WiseOldManAPI(group_id=int(WOM_GROUP_ID) if WOM_GROUP_ID else None)

# In-memory storage (replace with MongoDB/database in production)
bingo_boards = {}
player_drops = {}
team_stats = {}

# Admin keys for validation
adminTileKeys = ['description', 'image', 'points', 'title', 'rowBingo', 'colBingo', 'type', 'requirement']
generalTileKeys = ['proof', 'checked', 'currPoints', 'completedBy', 'completedAt']
boardCreationKeys = ['adminPassword', 'generalPassword', 'boardName', 'boardData', 'teams']


def bad_request(message):
    response = jsonify({'message': message})
    response.status_code = 400
    return response


def init_empty_team_data(row, col):
    """Initialize empty team data structure"""
    teamData = []
    for i in range(row):
        teamData.append([])
        for j in range(col):
            teamObj = {
                'checked': False,
                'proof': '',
                'currPoints': 0,
                'completedBy': '',
                'completedAt': ''
            }
            teamData[i].append(teamObj)
    return teamData


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.datetime.utcnow().isoformat(),
        'services': {
            'discord': bool(WEBHOOK_CONFIG.get('main')),
            'wom': bool(WOM_GROUP_ID),
            'google_sheets': bool(GOOGLE_SHEETS_ID)
        }
    })


@app.route('/api/boards', methods=['POST'])
def create_board():
    """Create a new bingo board"""
    data = request.json
    
    # Validate required fields
    for key in boardCreationKeys:
        if key not in data:
            return bad_request(f"Missing required field: {key}")
    
    board_name = data['boardName']
    if board_name in bingo_boards:
        return bad_request("Board name already exists")
    
    # Initialize board
    board = {
        'boardName': board_name,
        'adminPassword': data['adminPassword'],
        'generalPassword': data['generalPassword'],
        'boardData': data['boardData'],
        'teams': data['teams'],
        'teamData': {},
        'createdAt': datetime.datetime.utcnow().isoformat(),
        'lastUpdated': datetime.datetime.utcnow().isoformat()
    }
    
    # Initialize team data for each team
    rows = len(data['boardData'])
    cols = len(data['boardData'][0]) if rows > 0 else 0
    
    for team in data['teams']:
        board['teamData'][team['name']] = init_empty_team_data(rows, cols)
    
    bingo_boards[board_name] = board
    
    # Send notification
    webhook = webhook_manager.get_webhook('bingo')
    if webhook:
        webhook.send_message(
            content=f"🎮 New Bingo Board Created: **{board_name}**\n"
                   f"Teams: {', '.join([t['name'] for t in data['teams']])}"
        )
    
    return jsonify({'message': 'Board created successfully', 'boardName': board_name})


@app.route('/api/boards/<board_name>', methods=['GET'])
def get_board(board_name):
    """Get board data"""
    if board_name not in bingo_boards:
        return bad_request("Board not found")
    
    board = bingo_boards[board_name]
    
    # Remove sensitive data
    safe_board = {
        'boardName': board['boardName'],
        'boardData': board['boardData'],
        'teams': board['teams'],
        'teamData': board['teamData'],
        'createdAt': board['createdAt'],
        'lastUpdated': board['lastUpdated']
    }
    
    return jsonify(safe_board)


@app.route('/api/boards/<board_name>/tiles/<int:row>/<int:col>', methods=['PUT'])
def update_tile(board_name, row, col):
    """Update a tile's completion status"""
    if board_name not in bingo_boards:
        return bad_request("Board not found")
    
    data = request.json
    team_name = data.get('teamName')
    password = data.get('password')
    
    if not team_name:
        return bad_request("Team name required")
    
    board = bingo_boards[board_name]
    
    # Validate password
    if password != board['generalPassword'] and password != board['adminPassword']:
        return bad_request("Invalid password")
    
    # Update tile
    if team_name not in board['teamData']:
        return bad_request("Team not found")
    
    team_data = board['teamData'][team_name]
    if row >= len(team_data) or col >= len(team_data[row]):
        return bad_request("Invalid tile coordinates")
    
    tile = team_data[row][col]
    tile['checked'] = data.get('checked', tile['checked'])
    tile['proof'] = data.get('proof', tile['proof'])
    tile['currPoints'] = data.get('currPoints', tile['currPoints'])
    tile['completedBy'] = data.get('completedBy', tile.get('completedBy', ''))
    tile['completedAt'] = datetime.datetime.utcnow().isoformat()
    
    board['lastUpdated'] = datetime.datetime.utcnow().isoformat()
    
    # Send notification if tile was completed
    if tile['checked'] and data.get('notifyDiscord', True):
        tile_data = board['boardData'][row][col]
        webhook = webhook_manager.get_webhook('bingo')
        if webhook:
            webhook.send_tile_completion(
                tile_title=tile_data.get('title', 'Unknown Tile'),
                team_name=team_name,
                player_name=tile['completedBy'],
                points=tile['currPoints'],
                proof_url=tile['proof']
            )
    
    return jsonify({'message': 'Tile updated', 'tile': tile})


@app.route('/api/drops', methods=['POST'])
def record_drop():
    """Record a player's item drop"""
    data = request.json
    
    required = ['playerName', 'itemName']
    for field in required:
        if field not in data:
            return bad_request(f"Missing field: {field}")
    
    player_name = data['playerName']
    item_name = data['itemName']
    
    # Record drop
    drop_record = {
        'playerName': player_name,
        'itemName': item_name,
        'quantity': data.get('quantity', 1),
        'rarity': data.get('rarity'),
        'value': data.get('value'),
        'screenshot': data.get('screenshot'),
        'teamName': data.get('teamName'),
        'timestamp': datetime.datetime.utcnow().isoformat()
    }
    
    if player_name not in player_drops:
        player_drops[player_name] = []
    
    player_drops[player_name].append(drop_record)
    
    # Send Discord notification
    webhook = webhook_manager.get_webhook('drops')
    if webhook:
        webhook.send_drop_notification(
            player_name=player_name,
            item_name=item_name,
            item_quantity=drop_record['quantity'],
            rarity=drop_record['rarity'],
            value=drop_record['value'],
            screenshot_url=drop_record['screenshot'],
            team_name=drop_record['teamName']
        )
    
    return jsonify({'message': 'Drop recorded', 'drop': drop_record})


@app.route('/api/players/<username>/stats', methods=['GET'])
def get_player_stats(username):
    """Get player stats from Wise Old Man"""
    player_data = wom_api.get_player(username)
    
    if not player_data:
        return bad_request("Player not found")
    
    return jsonify(player_data)


@app.route('/api/players/<username>/gains', methods=['GET'])
def get_player_gains(username):
    """Get player gains from Wise Old Man"""
    period = request.args.get('period', 'week')
    gains_data = wom_api.get_player_gains(username, period)
    
    if not gains_data:
        return bad_request("Could not fetch gains")
    
    return jsonify(gains_data)


@app.route('/api/players/<username>/update', methods=['POST'])
def update_player(username):
    """Update player stats from OSRS"""
    success = wom_api.update_player(username)
    
    if success:
        return jsonify({'message': 'Player updated successfully'})
    else:
        return bad_request("Failed to update player")


@app.route('/api/tiles/check', methods=['POST'])
def check_tile_completion():
    """Check if players have completed tiles based on WOM data"""
    data = request.json
    
    players = data.get('players', [])
    tiles = data.get('tiles', [])
    
    if not players or not tiles:
        return bad_request("Players and tiles required")
    
    results = wom_api.track_players_for_tiles(players, tiles)
    
    return jsonify(results)


@app.route('/api/leaderboard/<board_name>', methods=['GET'])
def get_leaderboard(board_name):
    """Get team leaderboard for a board"""
    if board_name not in bingo_boards:
        return bad_request("Board not found")
    
    board = bingo_boards[board_name]
    leaderboard = []
    
    for team in board['teams']:
        team_name = team['name']
        team_data = board['teamData'].get(team_name, [])
        
        total_points = 0
        completed_tiles = 0
        
        for row in team_data:
            for tile in row:
                if tile['checked']:
                    completed_tiles += 1
                    total_points += tile['currPoints']
        
        leaderboard.append({
            'team': team_name,
            'points': total_points,
            'completed': completed_tiles,
            'color': team.get('color', '#000000')
        })
    
    # Sort by points descending
    leaderboard.sort(key=lambda x: x['points'], reverse=True)
    
    return jsonify(leaderboard)


@app.route('/api/stats/drops', methods=['GET'])
def get_drop_stats():
    """Get drop statistics"""
    stats = {
        'total_drops': sum(len(drops) for drops in player_drops.values()),
        'unique_players': len(player_drops),
        'recent_drops': []
    }
    
    # Get 10 most recent drops
    all_drops = []
    for player, drops in player_drops.items():
        all_drops.extend(drops)
    
    all_drops.sort(key=lambda x: x['timestamp'], reverse=True)
    stats['recent_drops'] = all_drops[:10]
    
    return jsonify(stats)


@app.route('/api/webhook/test', methods=['POST'])
def test_webhook():
    """Test Discord webhook"""
    data = request.json
    webhook_name = data.get('webhook', 'main')
    
    webhook = webhook_manager.get_webhook(webhook_name)
    if not webhook:
        return bad_request(f"Webhook '{webhook_name}' not configured")
    
    success = webhook.send_message(
        content="✅ Test message from BINGO Tracker!"
    )
    
    if success:
        return jsonify({'message': 'Webhook test successful'})
    else:
        return bad_request("Webhook test failed")


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug_mode = os.getenv('DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
