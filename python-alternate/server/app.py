"""
Main Flask Application for Python-Only BINGO Tracker
Combines web interface with API functionality
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import yaml
import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import Database, init_db
from utils.discord_webhook import WebhookManager
from utils.wom_api import WiseOldManAPI
from utils.config import Config
import models
import api

# Initialize Flask app
app = Flask(__name__)

# Load configuration
config = Config('config.yaml')
app.config['SECRET_KEY'] = config.get('server.secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = config.get_database_uri()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
CORS(app)
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[config.get('security.rate_limit.default', '100 per hour')]
)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize services
db = Database(app)
webhook_manager = WebhookManager(config.get('discord.webhooks', {}))
wom_api = WiseOldManAPI(config.get('wiseoldman.group_id'))

# Register API blueprint
app.register_blueprint(api.api_bp, url_prefix='/api')

@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(int(user_id))


# ===== Web Routes =====

@app.route('/')
def index():
    """Home page"""
    boards = models.Board.query.order_by(models.Board.created_at.desc()).limit(10).all()
    recent_drops = models.Drop.query.order_by(models.Drop.timestamp.desc()).limit(5).all()
    
    stats = {
        'total_boards': models.Board.query.count(),
        'total_teams': models.Team.query.count(),
        'total_drops': models.Drop.query.count(),
        'active_players': db.session.query(models.Drop.player_name).distinct().count()
    }
    
    return render_template('index.html', 
                          boards=boards, 
                          recent_drops=recent_drops,
                          stats=stats)


@app.route('/dashboard')
def dashboard():
    """Main dashboard with statistics and updates"""
    # Get recent activity
    recent_drops = models.Drop.query.order_by(
        models.Drop.timestamp.desc()
    ).limit(20).all()
    
    # Get active boards
    boards = models.Board.query.all()
    
    # Calculate statistics
    stats = {
        'total_drops': models.Drop.query.count(),
        'unique_players': db.session.query(models.Drop.player_name).distinct().count(),
        'active_boards': len([b for b in boards if b.is_active]),
        'total_points': sum([team.total_points for board in boards for team in board.teams])
    }
    
    return render_template('dashboard.html',
                          recent_drops=recent_drops,
                          boards=boards,
                          stats=stats)


@app.route('/board/<board_name>')
def view_board(board_name):
    """View a specific bingo board"""
    board = models.Board.query.filter_by(name=board_name).first_or_404()
    
    # Check if user has access
    if board.requires_password and not session.get(f'board_auth_{board.id}'):
        return redirect(url_for('board_login', board_name=board_name))
    
    # Calculate team standings
    leaderboard = []
    for team in board.teams:
        completed = len([t for t in team.tiles if t.checked])
        leaderboard.append({
            'name': team.name,
            'color': team.color,
            'points': team.total_points,
            'completed': completed,
            'total': len(team.tiles)
        })
    
    leaderboard.sort(key=lambda x: x['points'], reverse=True)
    
    return render_template('board.html', 
                          board=board, 
                          leaderboard=leaderboard,
                          can_edit=session.get(f'board_auth_{board.id}') == 'admin')


@app.route('/board/<board_name>/login', methods=['GET', 'POST'])
def board_login(board_name):
    """Login to access a board"""
    board = models.Board.query.filter_by(name=board_name).first_or_404()
    
    if request.method == 'POST':
        password = request.form.get('password')
        
        if board.check_password(password, 'admin'):
            session[f'board_auth_{board.id}'] = 'admin'
            flash('Logged in as admin', 'success')
            return redirect(url_for('view_board', board_name=board_name))
        elif board.check_password(password, 'general'):
            session[f'board_auth_{board.id}'] = 'general'
            flash('Logged in successfully', 'success')
            return redirect(url_for('view_board', board_name=board_name))
        else:
            flash('Invalid password', 'error')
    
    return render_template('board_login.html', board=board)


@app.route('/create', methods=['GET', 'POST'])
def create_board():
    """Create a new bingo board"""
    if request.method == 'POST':
        data = request.form.to_dict()
        
        # Parse teams
        teams_count = int(data.get('teams_count', 2))
        teams = []
        for i in range(teams_count):
            teams.append({
                'name': data.get(f'team_{i}_name'),
                'color': data.get(f'team_{i}_color', '#000000')
            })
        
        # Parse tiles (simplified - in production, use a form builder)
        rows = int(data.get('rows', 5))
        cols = int(data.get('cols', 5))
        tiles = []
        for i in range(rows):
            row = []
            for j in range(cols):
                tile_key = f'tile_{i}_{j}'
                row.append({
                    'title': data.get(f'{tile_key}_title', ''),
                    'description': data.get(f'{tile_key}_desc', ''),
                    'points': int(data.get(f'{tile_key}_points', 10)),
                    'type': data.get(f'{tile_key}_type', 'item')
                })
            tiles.append(row)
        
        # Create board
        board = models.Board(
            name=data['board_name'],
            admin_password=data['admin_password'],
            general_password=data['general_password']
        )
        board.set_tiles(tiles)
        db.session.add(board)
        
        # Create teams
        for team_data in teams:
            team = models.Team(
                name=team_data['name'],
                color=team_data['color'],
                board=board
            )
            db.session.add(team)
        
        db.session.commit()
        
        # Send Discord notification
        webhook = webhook_manager.get_webhook('bingo')
        if webhook:
            webhook.send_message(
                content=f"🎮 New Bingo Board Created: **{board.name}**\n"
                       f"Teams: {', '.join([t.name for t in board.teams])}"
            )
        
        flash(f'Board "{board.name}" created successfully!', 'success')
        return redirect(url_for('view_board', board_name=board.name))
    
    return render_template('create_board.html')


@app.route('/leaderboard')
def leaderboard():
    """Global leaderboard across all boards"""
    boards = models.Board.query.filter_by(is_active=True).all()
    
    all_teams = []
    for board in boards:
        for team in board.teams:
            completed = len([t for t in team.tiles if t.checked])
            all_teams.append({
                'name': team.name,
                'board': board.name,
                'color': team.color,
                'points': team.total_points,
                'completed': completed
            })
    
    all_teams.sort(key=lambda x: x['points'], reverse=True)
    
    return render_template('leaderboard.html', teams=all_teams)


@app.route('/drops')
def drops():
    """View all drops"""
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    drops_query = models.Drop.query.order_by(models.Drop.timestamp.desc())
    drops_page = drops_query.paginate(page=page, per_page=per_page)
    
    return render_template('drops.html', drops=drops_page)


@app.route('/report', methods=['GET', 'POST'])
def report_drop():
    """Manual drop reporting form"""
    if not config.get('features.manual_drop_entry', True):
        flash('Manual drop entry is disabled', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        drop = models.Drop(
            player_name=request.form['player_name'],
            item_name=request.form['item_name'],
            quantity=int(request.form.get('quantity', 1)),
            rarity=request.form.get('rarity'),
            value=int(request.form.get('value', 0)) if request.form.get('value') else None,
            team_name=request.form.get('team_name'),
            screenshot_url=request.form.get('screenshot')
        )
        
        db.session.add(drop)
        db.session.commit()
        
        # Send notifications
        webhook = webhook_manager.get_webhook('drops')
        if webhook:
            webhook.send_drop_notification(
                player_name=drop.player_name,
                item_name=drop.item_name,
                item_quantity=drop.quantity,
                rarity=drop.rarity,
                value=drop.value,
                screenshot_url=drop.screenshot_url,
                team_name=drop.team_name
            )
        
        flash('Drop reported successfully!', 'success')
        return redirect(url_for('drops'))
    
    # Get teams for dropdown
    teams = models.Team.query.all()
    
    return render_template('report_drop.html', teams=teams)


@app.route('/stats')
def stats():
    """Statistics page"""
    # Overall stats
    overall = {
        'total_boards': models.Board.query.count(),
        'active_boards': models.Board.query.filter_by(is_active=True).count(),
        'total_teams': models.Team.query.count(),
        'total_drops': models.Drop.query.count(),
        'unique_players': db.session.query(models.Drop.player_name).distinct().count()
    }
    
    # Top players by drops
    top_players = db.session.query(
        models.Drop.player_name,
        db.func.count(models.Drop.id).label('drop_count')
    ).group_by(models.Drop.player_name).order_by(
        db.desc('drop_count')
    ).limit(10).all()
    
    # Top items
    top_items = db.session.query(
        models.Drop.item_name,
        db.func.count(models.Drop.id).label('count')
    ).group_by(models.Drop.item_name).order_by(
        db.desc('count')
    ).limit(10).all()
    
    return render_template('stats.html',
                          overall=overall,
                          top_players=top_players,
                          top_items=top_items)


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'services': {
            'database': db.engine.url.database,
            'discord': bool(webhook_manager.webhooks),
            'wom': bool(wom_api.group_id)
        }
    })


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


if __name__ == '__main__':
    # Initialize database
    with app.app_context():
        init_db(db)
    
    # Run app
    app.run(
        host=config.get('server.host', '0.0.0.0'),
        port=config.get('server.port', 8000),
        debug=config.get('server.debug', False)
    )
