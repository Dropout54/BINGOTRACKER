"""
Discord Webhook Integration Module
Sends notifications about bingo tile completions and item drops
"""
import requests
import json
from datetime import datetime
from typing import Dict, List, Optional


class DiscordWebhook:
    """Handle Discord webhook notifications for bingo tracker"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    def send_message(self, content: str = None, embed: Dict = None) -> bool:
        """Send a message to Discord webhook
        
        Args:
            content: Plain text message content
            embed: Rich embed object for formatting
            
        Returns:
            bool: True if message sent successfully
        """
        if not self.webhook_url:
            return False
            
        payload = {}
        if content:
            payload['content'] = content
        if embed:
            payload['embeds'] = [embed]
            
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            return response.status_code in [200, 204]
        except Exception as e:
            print(f"Error sending Discord webhook: {e}")
            return False
    
    def send_drop_notification(
        self,
        player_name: str,
        item_name: str,
        item_quantity: int = 1,
        rarity: str = None,
        value: int = None,
        screenshot_url: str = None,
        team_name: str = None
    ) -> bool:
        """Send notification about item drop
        
        Args:
            player_name: Name of the player
            item_name: Name of the dropped item
            item_quantity: Quantity of items
            rarity: Drop rarity (e.g., "1/128")
            value: Item value in GP
            screenshot_url: URL to screenshot
            team_name: Team the player belongs to
            
        Returns:
            bool: Success status
        """
        embed = {
            'title': f'🎉 {item_name} Drop!',
            'color': 0x00ff00,  # Green
            'timestamp': datetime.utcnow().isoformat(),
            'fields': [
                {
                    'name': 'Player',
                    'value': player_name,
                    'inline': True
                },
                {
                    'name': 'Item',
                    'value': f'{item_name} x{item_quantity}',
                    'inline': True
                }
            ]
        }
        
        if team_name:
            embed['fields'].append({
                'name': 'Team',
                'value': team_name,
                'inline': True
            })
        
        if rarity:
            embed['fields'].append({
                'name': 'Rarity',
                'value': rarity,
                'inline': True
            })
        
        if value:
            embed['fields'].append({
                'name': 'Value',
                'value': f'{value:,} GP',
                'inline': True
            })
        
        if screenshot_url:
            embed['image'] = {'url': screenshot_url}
        
        return self.send_message(embed=embed)
    
    def send_tile_completion(
        self,
        tile_title: str,
        team_name: str,
        player_name: str,
        points: int,
        proof_url: str = None
    ) -> bool:
        """Send notification about bingo tile completion
        
        Args:
            tile_title: Title of the completed tile
            team_name: Team that completed the tile
            player_name: Player who completed it
            points: Points awarded
            proof_url: URL to proof image
            
        Returns:
            bool: Success status
        """
        embed = {
            'title': '✅ Bingo Tile Completed!',
            'description': tile_title,
            'color': 0xffd700,  # Gold
            'timestamp': datetime.utcnow().isoformat(),
            'fields': [
                {
                    'name': 'Team',
                    'value': team_name,
                    'inline': True
                },
                {
                    'name': 'Player',
                    'value': player_name,
                    'inline': True
                },
                {
                    'name': 'Points',
                    'value': str(points),
                    'inline': True
                }
            ]
        }
        
        if proof_url:
            embed['thumbnail'] = {'url': proof_url}
        
        return self.send_message(embed=embed)
    
    def send_bingo_achieved(
        self,
        team_name: str,
        bingo_type: str,
        total_points: int
    ) -> bool:
        """Send notification when team achieves a bingo
        
        Args:
            team_name: Team that got the bingo
            bingo_type: Type of bingo (row/column/diagonal)
            total_points: Total points scored
            
        Returns:
            bool: Success status
        """
        embed = {
            'title': '🎊 BINGO!',
            'description': f'{team_name} achieved a {bingo_type} bingo!',
            'color': 0xff0000,  # Red
            'timestamp': datetime.utcnow().isoformat(),
            'fields': [
                {
                    'name': 'Team',
                    'value': team_name,
                    'inline': True
                },
                {
                    'name': 'Type',
                    'value': bingo_type,
                    'inline': True
                },
                {
                    'name': 'Total Points',
                    'value': str(total_points),
                    'inline': True
                }
            ]
        }
        
        return self.send_message(embed=embed)


class WebhookManager:
    """Manage multiple Discord webhooks for different purposes"""
    
    def __init__(self, webhook_config: Dict[str, str]):
        """Initialize webhook manager
        
        Args:
            webhook_config: Dict mapping webhook names to URLs
        """
        self.webhooks = {
            name: DiscordWebhook(url) 
            for name, url in webhook_config.items()
        }
    
    def get_webhook(self, name: str) -> Optional[DiscordWebhook]:
        """Get a specific webhook by name"""
        return self.webhooks.get(name)
    
    def broadcast(
        self,
        content: str = None,
        embed: Dict = None,
        webhook_names: List[str] = None
    ) -> Dict[str, bool]:
        """Broadcast message to multiple webhooks
        
        Args:
            content: Message content
            embed: Embed object
            webhook_names: List of webhook names to send to (all if None)
            
        Returns:
            Dict mapping webhook names to success status
        """
        if webhook_names is None:
            webhook_names = list(self.webhooks.keys())
        
        results = {}
        for name in webhook_names:
            webhook = self.webhooks.get(name)
            if webhook:
                results[name] = webhook.send_message(content, embed)
        
        return results
