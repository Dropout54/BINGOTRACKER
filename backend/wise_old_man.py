"""
Wise Old Man API Integration
Tracks player experience, achievements, and competitions
"""
import requests
from typing import Dict, List, Optional
from datetime import datetime


class WiseOldManAPI:
    """Interface to Wise Old Man API for player tracking"""
    
    BASE_URL = "https://api.wiseoldman.net/v2"
    
    def __init__(self, group_id: Optional[int] = None):
        """Initialize WOM API client
        
        Args:
            group_id: Optional group ID for tracking clan/group
        """
        self.group_id = group_id
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'BINGOTRACKER/1.0'
        })
    
    def get_player(self, username: str) -> Optional[Dict]:
        """Get player details
        
        Args:
            username: Player's RuneScape username
            
        Returns:
            Player data dict or None if not found
        """
        try:
            response = self.session.get(
                f"{self.BASE_URL}/players/username/{username}"
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error fetching player {username}: {e}")
            return None
    
    def get_player_gains(
        self,
        username: str,
        period: str = "week"
    ) -> Optional[Dict]:
        """Get player's skill gains for a period
        
        Args:
            username: Player's username
            period: Time period (day, week, month, year)
            
        Returns:
            Gains data dict or None
        """
        try:
            response = self.session.get(
                f"{self.BASE_URL}/players/username/{username}/gained",
                params={'period': period}
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error fetching gains for {username}: {e}")
            return None
    
    def get_player_achievements(self, username: str) -> List[Dict]:
        """Get player's recent achievements
        
        Args:
            username: Player's username
            
        Returns:
            List of achievement dicts
        """
        try:
            response = self.session.get(
                f"{self.BASE_URL}/players/username/{username}/achievements"
            )
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            print(f"Error fetching achievements for {username}: {e}")
            return []
    
    def get_group_members(self) -> List[Dict]:
        """Get all members of the configured group
        
        Returns:
            List of member dicts
        """
        if not self.group_id:
            return []
        
        try:
            response = self.session.get(
                f"{self.BASE_URL}/groups/{self.group_id}"
            )
            if response.status_code == 200:
                data = response.json()
                return data.get('memberships', [])
            return []
        except Exception as e:
            print(f"Error fetching group members: {e}")
            return []
    
    def get_competition(self, competition_id: int) -> Optional[Dict]:
        """Get competition details
        
        Args:
            competition_id: Competition ID
            
        Returns:
            Competition data dict or None
        """
        try:
            response = self.session.get(
                f"{self.BASE_URL}/competitions/{competition_id}"
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error fetching competition {competition_id}: {e}")
            return None
    
    def update_player(self, username: str) -> bool:
        """Update player stats from OSRS API
        
        Args:
            username: Player's username
            
        Returns:
            True if update successful
        """
        try:
            response = self.session.post(
                f"{self.BASE_URL}/players/{username}"
            )
            return response.status_code in [200, 201]
        except Exception as e:
            print(f"Error updating player {username}: {e}")
            return False
    
    def check_skill_milestone(
        self,
        username: str,
        skill: str,
        target_level: int = None,
        target_xp: int = None
    ) -> Dict:
        """Check if player has reached a skill milestone
        
        Args:
            username: Player's username
            skill: Skill name (e.g., 'attack', 'mining')
            target_level: Target level to check
            target_xp: Target XP to check
            
        Returns:
            Dict with 'reached' boolean and current stats
        """
        player = self.get_player(username)
        if not player:
            return {'reached': False, 'error': 'Player not found'}
        
        snapshot = player.get('latestSnapshot', {})
        skill_data = snapshot.get('data', {}).get(skill, {})
        
        current_level = skill_data.get('level', 0)
        current_xp = skill_data.get('experience', 0)
        
        result = {
            'reached': False,
            'current_level': current_level,
            'current_xp': current_xp,
            'skill': skill,
            'username': username
        }
        
        if target_level and current_level >= target_level:
            result['reached'] = True
        elif target_xp and current_xp >= target_xp:
            result['reached'] = True
        
        return result
    
    def get_player_boss_kc(self, username: str, boss: str) -> int:
        """Get player's kill count for a specific boss
        
        Args:
            username: Player's username
            boss: Boss name (lowercase, underscores)
            
        Returns:
            Kill count (0 if not found)
        """
        player = self.get_player(username)
        if not player:
            return 0
        
        snapshot = player.get('latestSnapshot', {})
        boss_data = snapshot.get('data', {}).get(boss, {})
        
        return boss_data.get('kills', 0)
    
    def track_players_for_tiles(
        self,
        players: List[str],
        tiles: List[Dict]
    ) -> Dict[str, List[Dict]]:
        """Check which tiles players have completed based on WOM data
        
        Args:
            players: List of player usernames
            tiles: List of tile configs with requirements
            
        Returns:
            Dict mapping usernames to lists of completed tiles
        """
        results = {}
        
        for username in players:
            player_data = self.get_player(username)
            if not player_data:
                continue
            
            completed_tiles = []
            snapshot = player_data.get('latestSnapshot', {})
            data = snapshot.get('data', {})
            
            for tile in tiles:
                tile_type = tile.get('type')
                
                if tile_type == 'skill':
                    skill = tile.get('skill', '').lower()
                    required_level = tile.get('level')
                    required_xp = tile.get('xp')
                    
                    skill_data = data.get(skill, {})
                    level = skill_data.get('level', 0)
                    xp = skill_data.get('experience', 0)
                    
                    if required_level and level >= required_level:
                        completed_tiles.append(tile)
                    elif required_xp and xp >= required_xp:
                        completed_tiles.append(tile)
                
                elif tile_type == 'boss':
                    boss = tile.get('boss', '').lower()
                    required_kc = tile.get('kc', 0)
                    
                    boss_data = data.get(boss, {})
                    kc = boss_data.get('kills', 0)
                    
                    if kc >= required_kc:
                        completed_tiles.append(tile)
            
            results[username] = completed_tiles
        
        return results
