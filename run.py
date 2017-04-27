from __future__ import print_function

import curses
import random
import time

FPS = 30
REFRESH_TIME = float(1)/FPS


class ShavingGame(object):

    def __init__(self):
        self.cash = 100
        self.buy = 5
        self.sell = 5.01
        self.owned = 0
        self.debug_str = ''
        self.render_time = time.time()
        self.price_time = time.time()
        self.trend_time = time.time()
        self.trend_up = 1

        
    def update_price(self):
        if self.price_time > time.time():
            return
        if self.trend_time < time.time():
            self.trend_time = time.time() + random.randint(5, 15)
            self.trend_up = random.randint(0, 1)
        change = float(random.randrange(-3 if not self.trend_up else -2, 4 if self.trend_up else 3))/100

        self.debug_str = "change={}trend_up={}".format(change, self.trend_up)
        self.buy += change
        self.sell = self.buy + float(random.randrange(1,2))/100
        self.price_time = time.time() + float(random.randrange(5,20))/10
        
    def process_input(self, screen):
        user_in = screen.getch()
        if user_in != -1:
            user_in = chr(user_in)
            if user_in == 'b' and self.cash > self.sell:
                self.cash -= self.sell
                self.owned += 1
            if user_in == 's' and self.owned > 0:
                self.owned -= 1
                self.cash += self.buy
                
    def run(self, screen):
        screen.nodelay(True)
        while True:
            if time.time() < self.render_time + REFRESH_TIME:
                time.sleep((self.render_time + REFRESH_TIME) - time.time())
            screen.erase()
            screen.addstr(
                0, 0, 'Cash: ${:,.2f}      Shares: {}'.format(self.cash, self.owned))
            screen.addstr(
                1, 0, 'Buy: ${:,.2f}       Sell: {:,.2f}'.format(self.buy, self.sell))
            screen.addstr(2,0, 'Debug: {}'.format(self.debug_str))
            self.render_time = time.time()
            self.process_input(screen)
            self.update_price()
            if time.time() <= self.price_time:
                self.update_price()
            # self.debug_str = 'trend_up={}'.format(self.trend_up)

if __name__ == '__main__':
    game = ShavingGame()
    curses.wrapper(game.run)
