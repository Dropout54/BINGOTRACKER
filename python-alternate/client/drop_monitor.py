"""
Drop Monitor Client - Watches for OSRS drops and reports to server
Supports multiple detection methods: logfile, OCR, manual
"""
import os
import sys
import time
import argparse
import logging
from pathlib import Path
from datetime import datetime
import requests
import yaml
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import Config


class LogFileMonitor:
    """Monitor RuneLite chat logs for drop messages"""
    
    def __init__(self, config, server_url):
        self.config = config
        self.server_url = server_url
        self.log_path = Path(config.get('monitoring.logfile.path', '~/.runelite/chatlogs')).expanduser()
        self.patterns = config.get('monitoring.logfile.patterns', [])
        self.last_positions = {}
        self.logger = logging.getLogger('monitor.logfile')
        
    def start(self):
        """Start monitoring log files"""
        self.logger.info(f"Starting log file monitor on {self.log_path}")
        
        if not self.log_path.exists():
            self.logger.error(f"Log path does not exist: {self.log_path}")
            return
        
        # Watch for new log files
        event_handler = LogFileHandler(self)
        observer = Observer()
        observer.schedule(event_handler, str(self.log_path), recursive=False)
        observer.start()
        
        try:
            while True:
                # Check existing log files
                self.scan_logs()
                time.sleep(self.config.get('monitoring.logfile.scan_interval', 5))
        except KeyboardInterrupt:
            observer.stop()
        
        observer.join()
    
    def scan_logs(self):
        """Scan all log files for new messages"""
        for log_file in self.log_path.glob('*.txt'):
            self.process_log_file(log_file)
    
    def process_log_file(self, log_file):
        """Process a single log file"""
        # Get last read position
        last_pos = self.last_positions.get(str(log_file), 0)
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                # Seek to last position
                f.seek(last_pos)
                
                # Read new lines
                for line in f:
                    self.process_line(line.strip())
                
                # Update position
                self.last_positions[str(log_file)] = f.tell()
        
        except Exception as e:
            self.logger.error(f"Error processing {log_file}: {e}")
    
    def process_line(self, line):
        """Process a single chat line"""
        # Check if line matches any pattern
        for pattern in self.patterns:
            if pattern in line:
                self.handle_drop(line)
                break
    
    def handle_drop(self, message):
        """Handle detected drop message"""
        self.logger.info(f"Drop detected: {message}")
        
        # Parse drop information from message
        drop_info = self.parse_drop_message(message)
        
        if drop_info:
            # Send to server
            self.report_drop(drop_info)
    
    def parse_drop_message(self, message):
        """Parse drop message to extract item info"""
        # Example formats:
        # "Valuable drop: Dragon warhammer (58,123,456 coins)"
        # "Untradeable drop: Pet snakeling"
        # "You have a funny feeling like you're being followed."
        
        drop_info = {
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if 'Valuable drop:' in message:
            # Extract item name and value
            parts = message.split('Valuable drop: ')[1].split(' (')
            drop_info['item_name'] = parts[0].strip()
            
            if len(parts) > 1:
                value_str = parts[1].replace(' coins)', '').replace(',', '')
                try:
                    drop_info['value'] = int(value_str)
                except ValueError:
                    pass
        
        elif 'Untradeable drop:' in message:
            drop_info['item_name'] = message.split('Untradeable drop: ')[1].strip()
        
        elif 'funny feeling' in message.lower():
            drop_info['item_name'] = 'Pet drop'
            drop_info['note'] = message
        
        return drop_info if 'item_name' in drop_info else None
    
    def report_drop(self, drop_info):
        """Report drop to server"""
        try:
            # Get player name from config or environment
            player_name = self.config.get('monitoring.player_name', os.getenv('OSRS_USERNAME', 'Unknown'))
            team_name = self.config.get('monitoring.team_name', '')
            
            payload = {
                'playerName': player_name,
                'itemName': drop_info['item_name'],
                'quantity': drop_info.get('quantity', 1),
                'value': drop_info.get('value'),
                'teamName': team_name,
                'timestamp': drop_info['timestamp']
            }
            
            response = requests.post(
                f"{self.server_url}/api/drops",
                json=payload,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                self.logger.info(f"Drop reported successfully: {drop_info['item_name']}")
            else:
                self.logger.error(f"Failed to report drop: {response.status_code}")
        
        except Exception as e:
            self.logger.error(f"Error reporting drop: {e}")


class LogFileHandler(FileSystemEventHandler):
    """Watch for new log files"""
    
    def __init__(self, monitor):
        self.monitor = monitor
    
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.txt'):
            self.monitor.process_log_file(Path(event.src_path))
    
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('.txt'):
            self.monitor.process_log_file(Path(event.src_path))


class OCRMonitor:
    """Monitor OSRS window using OCR (requires Tesseract)"""
    
    def __init__(self, config, server_url):
        self.config = config
        self.server_url = server_url
        self.logger = logging.getLogger('monitor.ocr')
        
        try:
            import pytesseract
            from PIL import ImageGrab
            self.pytesseract = pytesseract
            self.ImageGrab = ImageGrab
        except ImportError:
            self.logger.error("OCR monitoring requires: pip install pytesseract Pillow")
            sys.exit(1)
    
    def start(self):
        """Start OCR monitoring"""
        self.logger.info("Starting OCR monitor")
        
        region = self.config.get('monitoring.ocr.region', [100, 100, 400, 300])
        scan_interval = self.config.get('monitoring.ocr.scan_interval', 10)
        
        try:
            while True:
                # Capture screen region
                screenshot = self.ImageGrab.grab(bbox=tuple(region))
                
                # Run OCR
                text = self.pytesseract.image_to_string(screenshot)
                
                # Process text for drops
                self.process_text(text)
                
                time.sleep(scan_interval)
        
        except KeyboardInterrupt:
            self.logger.info("OCR monitor stopped")
    
    def process_text(self, text):
        """Process OCR text for drop messages"""
        lines = text.split('\n')
        
        for line in lines:
            if any(pattern in line for pattern in ['Valuable drop', 'Untradeable', 'funny feeling']):
                self.logger.info(f"OCR detected: {line}")
                # Parse and report similar to log file monitor
                # Implementation similar to LogFileMonitor.process_line()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='OSRS Drop Monitor')
    parser.add_argument('--config', default='config.yaml', help='Config file path')
    parser.add_argument('--method', choices=['logfile', 'ocr'], help='Override monitoring method')
    parser.add_argument('--server', help='Override server URL')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/monitor.log'),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger('monitor')
    logger.info("Starting OSRS Drop Monitor")
    
    # Load config
    config = Config(args.config)
    
    # Get method
    method = args.method or config.get('monitoring.method', 'logfile')
    server_url = args.server or f"http://{config.get('server.host')}:{config.get('server.port')}"
    
    # Start appropriate monitor
    if method == 'logfile':
        monitor = LogFileMonitor(config, server_url)
    elif method == 'ocr':
        monitor = OCRMonitor(config, server_url)
    else:
        logger.error(f"Unknown monitoring method: {method}")
        sys.exit(1)
    
    try:
        monitor.start()
    except KeyboardInterrupt:
        logger.info("Monitor stopped by user")
    except Exception as e:
        logger.error(f"Monitor error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
