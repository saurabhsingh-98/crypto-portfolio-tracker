"""
Author: Saurabh Kumar Singh
"""

import requests
import json
from datetime import datetime
import time
import os
from typing import Dict, Optional, List

class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # Grayscale
    WHITE = '\033[97m'
    GRAY = '\033[90m'
    BLACK = '\033[30m'
    
    # Accent colors
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    YELLOW = '\033[93m'

class UI:
    
    @staticmethod
    def clear():
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def line(char='─', length=60):
        return char * length
    
    @staticmethod
    def header(text: str):
        print()
        print(f"{Colors.BOLD}{Colors.WHITE}{text.center(60)}{Colors.RESET}")
        print(f"{Colors.GRAY}{UI.line()}{Colors.RESET}")
        print()
    
    @staticmethod
    def section(text: str):
        print(f"\n{Colors.BOLD}{Colors.WHITE}{text}{Colors.RESET}")
        print(f"{Colors.GRAY}{UI.line('─', len(text))}{Colors.RESET}")
    
    @staticmethod
    def info(label: str, value: str, color=Colors.WHITE):
        print(f"{Colors.GRAY}{label:<20}{Colors.RESET}{color}{value}{Colors.RESET}")
    
    @staticmethod
    def success(message: str):
        print(f"{Colors.GREEN}✓{Colors.RESET} {message}")
    
    @staticmethod
    def error(message: str):
        print(f"{Colors.RED}✗{Colors.RESET} {message}")
    
    @staticmethod
    def prompt(message: str) -> str:
        return input(f"{Colors.CYAN}› {Colors.RESET}{message} ")
    
    @staticmethod
    def menu_item(number: int, text: str, description: str = ""):
        num = f"{Colors.BOLD}{Colors.WHITE}{number}{Colors.RESET}"
        title = f"{Colors.WHITE}{text}{Colors.RESET}"
        desc = f"{Colors.GRAY}{description}{Colors.RESET}" if description else ""
        print(f"  {num}  {title}")
        if desc:
            print(f"     {desc}")
    
    @staticmethod
    def divider():
        print(f"{Colors.GRAY}{UI.line()}{Colors.RESET}")
    
    @staticmethod
    def space(lines=1):
        print('\n' * (lines - 1))


class CryptoTracker:
    
    def __init__(self):
        self.api_base = "https://api.coingecko.com/api/v3"
        self.portfolio: Dict = {}
        self.portfolio_file = 'portfolio.json'
        self.settings_file = 'settings.json'
        self.currency = 'usd'  # Default currency
        self.goals = {
            'target_value': 0,
            'target_date': '',
            'initial_investment': 0
        }
        self.load_portfolio()
        self.load_settings()
    
    def load_portfolio(self):
        if os.path.exists(self.portfolio_file):
            try:
                with open(self.portfolio_file, 'r') as f:
                    self.portfolio = json.load(f)
                UI.success("Portfolio loaded")
            except:
                self.portfolio = {}
        else:
            self.portfolio = {}
    
    def load_settings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    data = json.load(f)
                    self.currency = data.get('currency', 'usd')
                    self.goals = data.get('goals', self.goals)
            except:
                pass
    
    def save_settings(self):
        with open(self.settings_file, 'w') as f:
            json.dump({
                'currency': self.currency,
                'goals': self.goals
            }, f, indent=2)
    
    def save_portfolio(self):
        with open(self.portfolio_file, 'w') as f:
            json.dump(self.portfolio, f, indent=2)
    
    def get_price(self, crypto_id: str) -> Optional[Dict]:
        try:
            url = f"{self.api_base}/simple/price"
            params = {
                'ids': crypto_id,
                'vs_currencies': self.currency,
                'include_24hr_change': 'true',
                'include_market_cap': 'true'
            }
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if crypto_id in data:
                return {
                    'price': data[crypto_id][self.currency],
                    'change_24h': data[crypto_id].get(f'{self.currency}_24h_change', 0),
                    'market_cap': data[crypto_id].get(f'{self.currency}_market_cap', 0)
                }
            return None
        except Exception as e:
            UI.error(f"Connection error: {str(e)}")
            return None
    
    def get_currency_symbol(self):
        symbols = {
            'usd': '$',
            'inr': '₹',
            'eur': '€',
            'gbp': '£'
        }
        return symbols.get(self.currency, '$')
    
    def get_currency_name(self):
        names = {
            'usd': 'USD',
            'inr': 'INR',
            'eur': 'EUR',
            'gbp': 'GBP'
        }
        return names.get(self.currency, 'USD')
    
    def switch_currency(self):
        UI.clear()
        UI.header("CURRENCY SETTINGS")
        
        print(f"{Colors.GRAY}Current: {Colors.WHITE}{self.get_currency_name()}{Colors.RESET}\n")
        
        currencies = {
            '1': ('usd', 'USD - US Dollar'),
            '2': ('inr', 'INR - Indian Rupee'),
            '3': ('eur', 'EUR - Euro'),
            '4': ('gbp', 'GBP - British Pound')
        }
        
        for key, (code, name) in currencies.items():
            current = " (current)" if code == self.currency else ""
            print(f"{Colors.GRAY}{key}.{Colors.RESET} {Colors.WHITE}{name}{Colors.RESET}{Colors.GRAY}{current}{Colors.RESET}")
        
        print()
        choice = UI.prompt("Select currency")
        
        if choice in currencies:
            self.currency = currencies[choice][0]
            self.save_settings()
            UI.success(f"Currency changed to {self.get_currency_name()}")
        else:
            UI.error("Invalid choice")
        
        time.sleep(1.5)
    
    def search(self, query: str) -> List[Dict]:
        try:
            url = f"{self.api_base}/search"
            response = requests.get(url, params={'query': query}, timeout=10)
            data = response.json()
            return data.get('coins', [])[:5]
        except:
            return []
    
    def add_holding(self, crypto_id: str, amount: float, purchase_price: Optional[float] = None):
        price_data = self.get_price(crypto_id)
        
        if not price_data:
            UI.error("Could not fetch price data")
            return False
        
        if purchase_price is None:
            purchase_price = price_data['price']
        
        if crypto_id in self.portfolio:
            # Update existing
            old_amount = self.portfolio[crypto_id]['amount']
            old_avg = self.portfolio[crypto_id]['avg_price']
            new_amount = old_amount + amount
            new_avg = ((old_avg * old_amount) + (purchase_price * amount)) / new_amount
            
            self.portfolio[crypto_id]['amount'] = new_amount
            self.portfolio[crypto_id]['avg_price'] = new_avg
        else:
            # Add new
            self.portfolio[crypto_id] = {
                'amount': amount,
                'avg_price': purchase_price,
                'added': datetime.now().strftime("%Y-%m-%d")
            }
        
        self.save_portfolio()
        UI.success(f"Added {amount} {crypto_id.upper()}")
        return True
    
    def remove_holding(self, crypto_id: str, amount: Optional[float] = None):
        """Remove cryptocurrency from portfolio"""
        if crypto_id not in self.portfolio:
            UI.error("Not in portfolio")
            return False
        
        if amount is None or amount >= self.portfolio[crypto_id]['amount']:
            del self.portfolio[crypto_id]
            UI.success(f"Removed {crypto_id.upper()}")
        else:
            self.portfolio[crypto_id]['amount'] -= amount
            UI.success(f"Removed {amount} {crypto_id.upper()}")
        
        self.save_portfolio()
        return True
    
    def display_portfolio(self):
        UI.clear()
        currency_display = f"{self.get_currency_name()}"
        UI.header(f"PORTFOLIO ({currency_display})")
        
        if not self.portfolio:
            print(f"{Colors.GRAY}{'No holdings yet'.center(60)}{Colors.RESET}")
            UI.space(2)
            return
        
        total_value = 0
        total_invested = 0
        holdings_data = []
        symbol = self.get_currency_symbol()
        
        # Fetch all data
        for crypto_id, holding in self.portfolio.items():
            price_data = self.get_price(crypto_id)
            if price_data:
                holdings_data.append({
                    'id': crypto_id,
                    'amount': holding['amount'],
                    'avg_price': holding['avg_price'],
                    'current_price': price_data['price'],
                    'change_24h': price_data['change_24h']
                })
                time.sleep(0.3)  # Rate limiting
        
        # Display each holding
        for data in holdings_data:
            crypto_id = data['id']
            amount = data['amount']
            avg_price = data['avg_price']
            current_price = data['current_price']
            change_24h = data['change_24h']
            
            value = current_price * amount
            invested = avg_price * amount
            profit = value - invested
            profit_pct = (profit / invested * 100) if invested > 0 else 0
            
            total_value += value
            total_invested += invested
            
            # Crypto name
            print(f"{Colors.BOLD}{Colors.WHITE}{crypto_id.upper()}{Colors.RESET}")
            
            # Holdings
            UI.info("Holdings", f"{amount:.8f}".rstrip('0').rstrip('.'))
            
            # Current value
            value_color = Colors.GREEN if profit >= 0 else Colors.RED
            UI.info("Value", f"{symbol}{value:,.2f}", value_color)
            
            # Profit/Loss
            sign = "+" if profit >= 0 else ""
            UI.info("P/L", f"{sign}{symbol}{profit:,.2f} ({sign}{profit_pct:.2f}%)", value_color)
            
            # 24h change
            change_color = Colors.GREEN if change_24h >= 0 else Colors.RED
            change_sign = "+" if change_24h >= 0 else ""
            UI.info("24h", f"{change_sign}{change_24h:.2f}%", change_color)
            
            print()
        
        # Summary
        UI.divider()
        total_profit = total_value - total_invested
        total_profit_pct = (total_profit / total_invested * 100) if total_invested > 0 else 0
        summary_color = Colors.GREEN if total_profit >= 0 else Colors.RED
        
        UI.info("Total Value", f"{symbol}{total_value:,.2f}", Colors.BOLD + Colors.WHITE)
        sign = "+" if total_profit >= 0 else ""
        UI.info("Total P/L", f"{sign}{symbol}{total_profit:,.2f} ({sign}{total_profit_pct:.2f}%)", summary_color)
        
        # Show goals progress if set
        if self.goals['target_value'] > 0:
            UI.space()
            self.show_goals_progress(total_value)
        
        UI.space(2)
    
    def display_trending(self):
        UI.clear()
        UI.header("TRENDING")
        
        try:
            url = f"{self.api_base}/search/trending"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if 'coins' in data:
                for i, item in enumerate(data['coins'][:7], 1):
                    coin = item['item']
                    rank = coin.get('market_cap_rank', 'N/A')
                    print(f"{Colors.GRAY}{i}.{Colors.RESET} {Colors.WHITE}{coin['name']}{Colors.RESET} {Colors.GRAY}{coin['symbol'].upper()}{Colors.RESET}")
                    print(f"   {Colors.GRAY}Rank #{rank}{Colors.RESET}")
                    if i < 7:
                        print()
        except:
            UI.error("Could not fetch trending data")
        
        UI.space(2)
    
    def quick_price(self, crypto_id: str):
        UI.clear()
        UI.header("PRICE CHECK")
        
        price_data = self.get_price(crypto_id)
        symbol = self.get_currency_symbol()
        
        if price_data:
            print(f"{Colors.BOLD}{Colors.WHITE}{crypto_id.upper()}{Colors.RESET}\n")
            UI.info("Price", f"{symbol}{price_data['price']:,.2f}", Colors.WHITE)
            
            change = price_data['change_24h']
            change_color = Colors.GREEN if change >= 0 else Colors.RED
            sign = "+" if change >= 0 else ""
            UI.info("24h Change", f"{sign}{change:.2f}%", change_color)
            
            if price_data['market_cap'] > 0:
                UI.info("Market Cap", f"{symbol}{price_data['market_cap']:,.0f}", Colors.GRAY)
        else:
            UI.error("Could not fetch price")
        
        UI.space(2)
    
    def set_investment_goals(self):
        UI.clear()
        UI.header("INVESTMENT GOALS")
        
        print(f"{Colors.GRAY}Set your crypto investment targets{Colors.RESET}\n")
        
        try:
            symbol = self.get_currency_symbol()
            
            # Get target value
            target = UI.prompt(f"Target portfolio value ({symbol})")
            if target:
                self.goals['target_value'] = float(target)
            
            # Get target date
            date = UI.prompt("Target date (YYYY-MM-DD)")
            if date:
                # Validate date format
                datetime.strptime(date, "%Y-%m-%d")
                self.goals['target_date'] = date
            
            # Get initial investment
            initial = UI.prompt(f"Initial investment ({symbol})")
            if initial:
                self.goals['initial_investment'] = float(initial)
            
            self.save_settings()
            UI.success("Goals saved!")
            
            # Show summary
            if self.goals['target_value'] > 0:
                print()
                UI.info("Target", f"{symbol}{self.goals['target_value']:,.2f}")
                if self.goals['target_date']:
                    UI.info("Target Date", self.goals['target_date'])
                if self.goals['initial_investment'] > 0:
                    UI.info("Initial", f"{symbol}{self.goals['initial_investment']:,.2f}")
        
        except ValueError:
            UI.error("Invalid input format")
        
        time.sleep(2)
    
    def show_goals_progress(self, current_value: float):
        if self.goals['target_value'] <= 0:
            return
        
        symbol = self.get_currency_symbol()
        target = self.goals['target_value']
        progress_pct = (current_value / target * 100) if target > 0 else 0
        remaining = target - current_value
        
        UI.divider()
        print(f"{Colors.BOLD}{Colors.WHITE}Investment Goal Progress{Colors.RESET}\n")
        
        UI.info("Target", f"{symbol}{target:,.2f}")
        UI.info("Current", f"{symbol}{current_value:,.2f}")
        
        if remaining > 0:
            UI.info("Remaining", f"{symbol}{remaining:,.2f}", Colors.YELLOW)
        else:
            UI.info("Exceeded by", f"{symbol}{-remaining:,.2f}", Colors.GREEN)
        
        # Progress bar
        bar_length = 30
        filled = int(bar_length * min(progress_pct / 100, 1))
        bar = "█" * filled + "░" * (bar_length - filled)
        progress_color = Colors.GREEN if progress_pct >= 100 else Colors.CYAN
        
        print(f"{Colors.GRAY}Progress{' ' * 10}{Colors.RESET}{progress_color}{bar} {progress_pct:.1f}%{Colors.RESET}")
        
        # Days until target
        if self.goals['target_date']:
            try:
                target_date = datetime.strptime(self.goals['target_date'], "%Y-%m-%d")
                days_left = (target_date - datetime.now()).days
                
                if days_left > 0:
                    UI.info("Days Left", f"{days_left} days", Colors.GRAY)
                elif days_left == 0:
                    UI.info("Status", "Target date is TODAY!", Colors.YELLOW)
                else:
                    UI.info("Status", f"Target date passed ({-days_left} days ago)", Colors.RED)
            except:
                pass
    
    def view_goals(self):
        UI.clear()
        UI.header("MY INVESTMENT GOALS")
        
        if self.goals['target_value'] <= 0:
            print(f"{Colors.GRAY}{'No goals set yet'.center(60)}{Colors.RESET}\n")
            print(f"{Colors.GRAY}Use option 7 to set your goals!{Colors.RESET}")
            UI.space(2)
            return
        
        symbol = self.get_currency_symbol()
        
        # Calculate current portfolio value
        current_value = 0
        if self.portfolio:
            for crypto_id, holding in self.portfolio.items():
                price_data = self.get_price(crypto_id)
                if price_data:
                    current_value += price_data['price'] * holding['amount']
                time.sleep(0.3)
        
        # Show goals
        UI.info("Target Value", f"{symbol}{self.goals['target_value']:,.2f}", Colors.WHITE)
        if self.goals['target_date']:
            UI.info("Target Date", self.goals['target_date'], Colors.WHITE)
        if self.goals['initial_investment'] > 0:
            UI.info("Initial Investment", f"{symbol}{self.goals['initial_investment']:,.2f}", Colors.WHITE)
        
        print()
        
        # Show progress
        self.show_goals_progress(current_value)
        
        # ROI if initial investment set
        if self.goals['initial_investment'] > 0 and current_value > 0:
            roi = ((current_value - self.goals['initial_investment']) / self.goals['initial_investment'] * 100)
            roi_color = Colors.GREEN if roi >= 0 else Colors.RED
            sign = "+" if roi >= 0 else ""
            print()
            UI.info("ROI", f"{sign}{roi:.2f}%", roi_color)
        
        UI.space(2)


def show_menu():
    UI.clear()
    UI.header("CRYPTO TRACKER")
    
    UI.menu_item(1, "Portfolio", "View your holdings")
    UI.menu_item(2, "Add", "Add cryptocurrency")
    UI.menu_item(3, "Remove", "Remove cryptocurrency")
    UI.menu_item(4, "Trending", "See what's hot")
    UI.menu_item(5, "Price", "Quick price check")
    UI.menu_item(6, "Currency", "Switch USD/INR/EUR/GBP")
    UI.menu_item(7, "Set Goals", "Set investment targets")
    UI.menu_item(8, "View Goals", "Check goal progress")
    UI.menu_item(9, "Exit", "Save and quit")
    
    UI.space()
    UI.divider()


def add_crypto_flow(tracker: CryptoTracker):
    UI.clear()
    UI.header("ADD CRYPTO")
    
    query = UI.prompt("Search")
    if not query:
        return
    
    results = tracker.search(query)
    
    if not results:
        UI.error("No results found")
        time.sleep(1.5)
        return
    
    print()
    for i, coin in enumerate(results, 1):
        print(f"{Colors.GRAY}{i}.{Colors.RESET} {Colors.WHITE}{coin['name']}{Colors.RESET} {Colors.GRAY}{coin['symbol'].upper()}{Colors.RESET}")
    
    print()
    choice = UI.prompt("Select (1-5)")
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(results):
            crypto_id = results[idx]['id']
            
            print()
            price_data = tracker.get_price(crypto_id)
            symbol = tracker.get_currency_symbol()
            if price_data:
                print(f"{Colors.GRAY}Current price: {symbol}{price_data['price']:,.2f}{Colors.RESET}\n")
            
            amount = float(UI.prompt("Amount"))
            
            use_current = UI.prompt("Use current price? (y/n)").lower()
            
            if use_current == 'y':
                tracker.add_holding(crypto_id, amount)
            else:
                purchase_price = float(UI.prompt(f"Purchase price {symbol}"))
                tracker.add_holding(crypto_id, amount, purchase_price)
            
            time.sleep(1.5)
    except ValueError:
        UI.error("Invalid input")
        time.sleep(1.5)


def remove_crypto_flow(tracker: CryptoTracker):
    UI.clear()
    UI.header("REMOVE CRYPTO")
    
    if not tracker.portfolio:
        print(f"{Colors.GRAY}No holdings to remove{Colors.RESET}")
        time.sleep(1.5)
        return
    
    print()
    for i, crypto_id in enumerate(tracker.portfolio.keys(), 1):
        amount = tracker.portfolio[crypto_id]['amount']
        print(f"{Colors.GRAY}{i}.{Colors.RESET} {Colors.WHITE}{crypto_id.upper()}{Colors.RESET} {Colors.GRAY}({amount:.8f}){Colors.RESET}")
    
    print()
    choice = UI.prompt("Select")
    
    try:
        idx = int(choice) - 1
        crypto_id = list(tracker.portfolio.keys())[idx]
        
        amount_input = UI.prompt("Amount (or 'all')")
        
        if amount_input.lower() == 'all':
            tracker.remove_holding(crypto_id)
        else:
            amount = float(amount_input)
            tracker.remove_holding(crypto_id, amount)
        
        time.sleep(1.5)
    except (ValueError, IndexError):
        UI.error("Invalid input")
        time.sleep(1.5)


def price_check_flow(tracker: CryptoTracker):
    UI.clear()
    UI.header("PRICE CHECK")
    
    crypto_id = UI.prompt("Enter crypto ID").lower()
    if crypto_id:
        tracker.quick_price(crypto_id)
        UI.prompt("\nPress Enter to continue")


def main():
    tracker = CryptoTracker()
    
    while True:
        show_menu()
        choice = UI.prompt("Choose")
        
        if choice == '1':
            tracker.display_portfolio()
            UI.prompt("Press Enter to continue")
        
        elif choice == '2':
            add_crypto_flow(tracker)
        
        elif choice == '3':
            remove_crypto_flow(tracker)
        
        elif choice == '4':
            tracker.display_trending()
            UI.prompt("Press Enter to continue")
        
        elif choice == '5':
            price_check_flow(tracker)
        
        elif choice == '6':
            tracker.switch_currency()
        
        elif choice == '7':
            tracker.set_investment_goals()
        
        elif choice == '8':
            tracker.view_goals()
            UI.prompt("Press Enter to continue")
        
        elif choice == '9':
            UI.clear()
            print()
            print(f"{Colors.GRAY}{'Portfolio saved'.center(60)}{Colors.RESET}")
            print()
            break
        
        else:
            UI.error("Invalid choice")
            time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        UI.clear()
        print()
        print(f"{Colors.GRAY}{'Goodbye'.center(60)}{Colors.RESET}")
        print()
    except Exception as e:
        UI.error(f"Error: {str(e)}")
