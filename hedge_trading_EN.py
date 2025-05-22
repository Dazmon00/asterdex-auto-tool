import requests
import time
import hmac
import hashlib
from urllib.parse import urlencode
import json
import os
import math
from datetime import datetime
import threading
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text

class TradingUI:
    def __init__(self):
        self.console = Console()
        self.layout = Layout()
        self.account1_status = {
            'position_side': 'NONE',
            'quantity': 0,
            'entry_price': 0,
            'unrealized_pnl': 0,
            'system_status': 'Initializing',
            'initial_balance': 0,
            'current_balance': 0,
            'margin': 0,
            'liquidation_price': 0
        }
        self.account2_status = self.account1_status.copy()
        self.current_price = 0
        self.running = True
        self.stats = {
            'trade_count': 0,
            'current_funding_rate': 0,
            'last_trade_time': None,
            'symbol': '',
            'leverage': 0,
            'wait_seconds': 0,
            'last_order_price': 0,
            'total_volume': 0,
            'total_volume_usdt': 0,
            'initial_total_balance': 0
        }
        
    def generate_layout(self):
        # Create title panel
        title_panel = Panel(
            Text("AsterDex Hedge Trading System", justify="center", style="bold white"),
            style="blue"
        )
        
        author_panel = Panel(
            Text("Free and Open Source, Twitter: @ddazmon", justify="center", style="bold white"),
            style="blue"
        )
        
        # Create market information table
        total_pnl = (self.account1_status['current_balance'] - self.account1_status['initial_balance'] + 
                    self.account2_status['current_balance'] - self.account2_status['initial_balance'])
        
        market_table = Table.grid(padding=1)
        market_table.add_column("Item", style="cyan")
        market_table.add_column("Value", style="green")
        
        market_table.add_row("Trading Pair", self.stats['symbol'])
        market_table.add_row("Current Price", f"{self.current_price} USDT")
        market_table.add_row("Current Leverage", f"{self.stats['leverage']}x")
        market_table.add_row("Current Funding Rate", f"{self.stats['current_funding_rate']*100:.4f}%")
        market_table.add_row("Holding Time", f"{self.stats['wait_seconds']} seconds")
        market_table.add_row("Trade Count", str(self.stats['trade_count']))
        market_table.add_row("Total Trading Volume", f"{self.stats['total_volume_usdt']:.2f} USDT")
        market_table.add_row("Account 1 Balance", f"{self.account1_status['current_balance']:.4f} USDT")
        market_table.add_row("Account 2 Balance", f"{self.account2_status['current_balance']:.4f} USDT")
        market_table.add_row("Initial Total Assets", f"{self.stats['initial_total_balance']:.4f} USDT")
        market_table.add_row("Total Profit/Loss", f"{total_pnl:.4f} USDT")
        market_table.add_row("Last Trade Time", self.stats['last_trade_time'] or 'None')
        market_table.add_row("Current Time", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        market_panel = Panel(
            market_table,
            title="Market Information",
            border_style="green"
        )
        
        # Create account status table
        account_table = Table(show_header=True, padding=1)
        account_table.add_column("Account", style="cyan", justify="left", width=8)
        account_table.add_column("Position Side", style="yellow", justify="center", width=10)
        account_table.add_column("Position Quantity", style="yellow", justify="right", width=12)
        account_table.add_column("Entry Price", style="yellow", justify="right", width=12)
        account_table.add_column("Unrealized P/L", style="yellow", justify="right", width=20)
        account_table.add_column("Margin", style="yellow", justify="right", width=20)
        account_table.add_column("Liquidation Price", style="yellow", justify="right", width=20)
        
        account_table.add_row(
            "Account 1",
            self.account1_status['position_side'],
            f"{self.account1_status['quantity']:>12.3f}",
            f"{self.account1_status['entry_price']:>12.2f}",
            f"{self.account1_status['unrealized_pnl']:>20.8f} USDT",
            f"{self.account1_status['margin']:>20.8f} USDT",
            f"{self.account1_status['liquidation_price']:>20.8f} USDT"
        )
        account_table.add_row(
            "Account 2",
            self.account2_status['position_side'],
            f"{self.account2_status['quantity']:>12.3f}",
            f"{self.account2_status['entry_price']:>12.2f}",
            f"{self.account2_status['unrealized_pnl']:>20.8f} USDT",
            f"{self.account2_status['margin']:>20.8f} USDT",
            f"{self.account2_status['liquidation_price']:>20.8f} USDT"
        )
        
        account_panel = Panel(
            account_table,
            title="Account Status",
            border_style="yellow"
        )

        # Combine all panels
        self.layout.split(
            Layout(name="header", size=6),
            Layout(name="main"),
        )
        
        self.layout["header"].split(
            Layout(title_panel, ratio=1),
            Layout(author_panel, ratio=1)
        )
        self.layout["main"].split_row(
            Layout(market_panel, ratio=1),
            Layout(account_panel, ratio=2)
        )
        
        return self.layout
    
    def update_status(self, account1_status, account2_status, current_price):
        self.account1_status = account1_status
        self.account2_status = account2_status
        self.current_price = current_price
        
    def update_stats(self, funding_rate=0, symbol='', leverage=0, wait_seconds=0, last_order_price=0, volume=0):
        self.stats['trade_count'] += 1
        self.stats['current_funding_rate'] = funding_rate
        self.stats['last_trade_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.stats['symbol'] = symbol
        self.stats['leverage'] = leverage
        self.stats['wait_seconds'] = wait_seconds
        self.stats['last_order_price'] = last_order_price
        self.stats['total_volume'] += volume
        self.stats['total_volume_usdt'] += volume * last_order_price
        
        # Update initial total assets (only on first update)
        if self.stats['initial_total_balance'] == 0:
            self.stats['initial_total_balance'] = (
                self.account1_status['initial_balance'] + 
                self.account2_status['initial_balance']
            )
        
    def show(self):
        with Live(self.generate_layout(), refresh_per_second=1) as live:
            while self.running:
                live.update(self.generate_layout())
                time.sleep(1)
    
    def stop(self):
        self.running = False

class AsterDexAPI:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://fapi.asterdex.com"
        self.recv_window = 5000
        
    def _generate_signature(self, params):
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _get_server_time(self):
        response = requests.get(self.base_url + "/fapi/v1/time")
        return response.json()['serverTime']
    
    def _get_timestamp(self):
        server_time = self._get_server_time()
        local_time = int(time.time() * 1000)
        time_diff = server_time - local_time
        return int(time.time() * 1000) + time_diff
    
    def get_account_info(self):
        """Get account information"""
        endpoint = "/fapi/v2/account"
        params = {
            "timestamp": self._get_timestamp(),
            "recvWindow": self.recv_window
        }
        params['signature'] = self._generate_signature(params)
        headers = {"X-MBX-APIKEY": self.api_key}
        response = requests.get(self.base_url + endpoint, params=params, headers=headers)
        return response.json()
    
    def get_account_balance(self):
        """Get account balance"""
        account_info = self.get_account_info()
        for asset in account_info['assets']:
            if asset['asset'] == 'USDT':
                return float(asset['walletBalance'])
        return 0.0
    
    def get_current_price(self, symbol):
        endpoint = "/fapi/v1/ticker/price"
        params = {"symbol": symbol}
        response = requests.get(self.base_url + endpoint, params=params)
        return float(response.json()['price'])
    
    def get_position_info(self, symbol):
        endpoint = "/fapi/v2/positionRisk"
        params = {
            "symbol": symbol,
            "timestamp": self._get_timestamp(),
            "recvWindow": self.recv_window
        }
        params['signature'] = self._generate_signature(params)
        headers = {"X-MBX-APIKEY": self.api_key}
        response = requests.get(self.base_url + endpoint, params=params, headers=headers)
        return response.json()
    
    def get_funding_rate(self, symbol):
        endpoint = "/fapi/v1/premiumIndex"
        params = {"symbol": symbol}
        response = requests.get(self.base_url + endpoint, params=params)
        return float(response.json()['lastFundingRate'])
    
    def set_leverage(self, symbol, leverage):
        endpoint = "/fapi/v1/leverage"
        params = {
            "symbol": symbol,
            "leverage": leverage,
            "timestamp": self._get_timestamp(),
            "recvWindow": self.recv_window
        }
        params['signature'] = self._generate_signature(params)
        headers = {"X-MBX-APIKEY": self.api_key}
        response = requests.post(self.base_url + endpoint, params=params, headers=headers)
        return response.json()
    
    def calculate_quantity_from_usdt(self, symbol, usdt_amount, leverage=10):
        current_price = self.get_current_price(symbol)
        quantity = usdt_amount / current_price
        quantity = max(0.001, quantity)
        final_quantity = round(quantity, 3)
        return final_quantity
    
    def place_order(self, symbol, side, order_type, quantity, position_side="BOTH"):
        if quantity <= 0:
            raise ValueError(f"Invalid order quantity: {quantity}")
            
        endpoint = "/fapi/v1/order"
        params = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
            "positionSide": position_side,
            "timestamp": self._get_timestamp(),
            "recvWindow": self.recv_window
        }
        params['signature'] = self._generate_signature(params)
        headers = {"X-MBX-APIKEY": self.api_key}
        response = requests.post(self.base_url + endpoint, params=params, headers=headers)
        return response.json()
    
    def close_position(self, symbol, side, order_type, quantity, position_side="BOTH"):
        opposite_side = "SELL" if side == "BUY" else "BUY"
        return self.place_order(symbol, opposite_side, order_type, quantity, position_side)
    
    def close_all_positions(self, symbol):
        """Close all positions for the specified trading pair"""
        try:
            position_info = self.get_position_info(symbol)
            if float(position_info[0]['positionAmt']) != 0:
                quantity = abs(float(position_info[0]['positionAmt']))
                side = "SELL" if float(position_info[0]['positionAmt']) > 0 else "BUY"
                return self.place_order(
                    symbol=symbol,
                    side=side,
                    order_type="MARKET",
                    quantity=quantity,
                    position_side="BOTH"
                )
        except Exception as e:
            print(f"Error closing positions: {str(e)}")
        return None

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise Exception("Error: config.json file not found")
    except json.JSONDecodeError:
        raise Exception("Error: Invalid config file format")

def update_position_status(api, symbol, ui, account_num):
    while True:
        try:
            position_info = api.get_position_info(symbol)
            current_price = api.get_current_price(symbol)
            account_info = api.get_account_info()
            
            # Get USDT asset information
            usdt_asset = next((asset for asset in account_info['assets'] if asset['asset'] == 'USDT'), None)
            if usdt_asset:
                current_balance = float(usdt_asset['walletBalance'])
                margin_balance = float(usdt_asset['marginBalance'])
                unrealized_pnl = float(usdt_asset['unrealizedProfit'])
            else:
                current_balance = 0
                margin_balance = 0
                unrealized_pnl = 0
            
            status = {
                'position_side': 'LONG' if float(position_info[0]['positionAmt']) > 0 else 'SHORT',
                'quantity': abs(float(position_info[0]['positionAmt'])),
                'entry_price': float(position_info[0]['entryPrice']),
                'unrealized_pnl': unrealized_pnl,
                'system_status': 'Running',
                'current_balance': current_balance,
                'margin': margin_balance,
                'liquidation_price': float(position_info[0]['liquidationPrice'])
            }
            
            if account_num == 1:
                if ui.account1_status['initial_balance'] == 0:
                    status['initial_balance'] = current_balance
                else:
                    status['initial_balance'] = ui.account1_status['initial_balance']
                ui.account1_status = status
            else:
                if ui.account2_status['initial_balance'] == 0:
                    status['initial_balance'] = current_balance
                else:
                    status['initial_balance'] = ui.account2_status['initial_balance']
                ui.account2_status = status
                
            ui.update_status(ui.account1_status, ui.account2_status, current_price)
            
        except Exception as e:
            status = {
                'position_side': 'NONE',
                'quantity': 0,
                'entry_price': 0,
                'unrealized_pnl': 0,
                'system_status': f'Error: {str(e)}',
                'current_balance': 0,
                'initial_balance': 0,
                'margin': 0,
                'liquidation_price': 0
            }
            
            if account_num == 1:
                ui.account1_status = status
            else:
                ui.account2_status = status
                
            ui.update_status(ui.account1_status, ui.account2_status, 0)
            
        time.sleep(1)

def cleanup_positions(account1, account2, symbol):
    """Clear all positions for both accounts"""
    console = Console()
    console.print("[yellow]Clearing positions...[/yellow]")
    
    # Close positions for account 1
    result1 = account1.close_all_positions(symbol)
    if result1:
        console.print("[green]Account 1 positions cleared[/green]")
    else:
        console.print("[red]Failed to clear Account 1 positions[/red]")
    
    # Close positions for account 2
    result2 = account2.close_all_positions(symbol)
    if result2:
        console.print("[green]Account 2 positions cleared[/green]")
    else:
        console.print("[red]Failed to clear Account 2 positions[/red]")

def main():
    try:
        # Initialize UI
        ui = TradingUI()
        
        # Load configuration
        config = load_config()
        
        # Create API instances
        account1 = AsterDexAPI(
            config['account1']['api_key'],
            config['account1']['api_secret']
        )
        account2 = AsterDexAPI(
            config['account2']['api_key'],
            config['account2']['api_secret']
        )
        
        # Get trading parameters
        trading_config = config['trading']
        symbol = trading_config['symbol']
        position_side = trading_config['position_side']
        order_type = trading_config['order_type']
        wait_seconds = trading_config['wait_seconds']
        leverage = trading_config['leverage']
        usdt_amount = trading_config['usdt_amount']
        
        # Start status update threads
        update_thread1 = threading.Thread(target=update_position_status, args=(account1, symbol, ui, 1))
        update_thread2 = threading.Thread(target=update_position_status, args=(account2, symbol, ui, 2))
        update_thread1.daemon = True
        update_thread2.daemon = True
        update_thread1.start()
        update_thread2.start()
        
        # Start UI display thread
        ui_thread = threading.Thread(target=ui.show)
        ui_thread.daemon = True
        ui_thread.start()
        
        # Wait for UI initialization
        time.sleep(2)
        
        # Set leverage
        leverage_result1 = account1.set_leverage(symbol, leverage)
        leverage_result2 = account2.set_leverage(symbol, leverage)
        
        if leverage_result1.get('leverage') != leverage or leverage_result2.get('leverage') != leverage:
            raise ValueError("Failed to set leverage")
        
        while True:
            try:
                # Calculate trading quantity
                quantity = account1.calculate_quantity_from_usdt(symbol, usdt_amount, leverage)
                
                # Get current funding rate and price
                funding_rate = account1.get_funding_rate(symbol)
                current_price = account1.get_current_price(symbol)
                
                # Execute trades
                long_order = account1.place_order(
                    symbol=symbol,
                    side="BUY",
                    order_type=order_type,
                    quantity=quantity,
                    position_side=position_side
                )
                
                short_order = account2.place_order(
                    symbol=symbol,
                    side="SELL",
                    order_type=order_type,
                    quantity=quantity,
                    position_side=position_side
                )
                
                # Update statistics
                ui.update_stats(
                    funding_rate=funding_rate,
                    symbol=symbol,
                    leverage=leverage,
                    wait_seconds=wait_seconds,
                    last_order_price=current_price,
                    volume=quantity * 2  # Each trade involves both accounts
                )
                
                time.sleep(wait_seconds)
                
                # Close positions
                close_long = account1.close_position(
                    symbol=symbol,
                    side="BUY",
                    order_type=order_type,
                    quantity=quantity,
                    position_side=position_side
                )
                
                close_short = account2.close_position(
                    symbol=symbol,
                    side="SELL",
                    order_type=order_type,
                    quantity=quantity,
                    position_side=position_side
                )
                
                # Wait before starting next round
                time.sleep(5)
                
            except Exception as e:
                console = Console()
                console.print(f"[red]Trading error: {str(e)}[/red]")
                time.sleep(5)  # Wait before retrying after an error
                continue
        
    except KeyboardInterrupt:
        console = Console()
        console.print("[yellow]Program interrupted by user[/yellow]")
    except Exception as e:
        console = Console()
        console.print(f"[red]Error: {str(e)}[/red]")
    finally:
        if 'ui' in locals():
            ui.stop()
        if 'account1' in locals() and 'account2' in locals():
            cleanup_positions(account1, account2, symbol)

if __name__ == "__main__":
    main()