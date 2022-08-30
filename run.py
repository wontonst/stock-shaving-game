from __future__ import print_function

import collections
import curses
import itertools
import random
import time

FPS = 30
REFRESH_TIME = float(1)/FPS
STARTING_CASH = 100
GRAPH_MAX_WIDTH = 80


class PriceTrends(object):
    STABLE = 0
    CRASH = 1
    POP = 2
    UP = 3
    DOWN = 4

    def __init__(self):
        self.price_time = time.time()
        self.trend_time = time.time()
        self.trend_up = random.randint(0, 1)
        self._buy = 5
        self._sell = 5.01
        self.price_history = collections.deque()

    @property
    def buy(self):
        return self._buy

    @property
    def sell(self):
        return self._sell

    def update_price(self):
        if self.price_time > time.time():
            return

        if self.trend_time < time.time():
            self.trend_time = time.time() + random.uniform(5, 15)
            self.trend_up = random.randint(0, 1)
        change = round(random.uniform(-0.03 if not self.trend_up else -0.02, 0.03 if self.trend_up else 0.02), 2)

        self._buy += change
        self._sell = self.buy + float(random.randrange(1, 2)) / 100
        self.price_time = time.time() + float(random.randrange(5, 20)) / 10
        self.price_history.append(self.buy)
        if len(self.price_history) > GRAPH_MAX_WIDTH:
            self.price_history.popleft()


class ShavingGame(object):

    def __init__(self):
        self.cash = STARTING_CASH
        self.owned = 0
        self.debug_str = ''
        self.render_time = time.time()
        self.buy_limits = collections.defaultdict(lambda:0)
        self.sell_limits = collections.defaultdict(lambda:0)
        self.price_mgr = PriceTrends()

    def draw_graph(self, values, height=10):
        lines = ['Price History']
        if not values:
            return lines
        mx = max(values)
        mn = min(values)
        diff = mx - mn
        for i in range(height):
            line = ''
            for val in values:
                line += ' ' if mn + (height-i) * diff / height > val else 'X'
                # line =  str(i * diff / height > val)
            line = '{0:>80}'.format(line)
            lines.append(line)
        return lines

    @property
    def sell(self):
        return self.price_mgr.sell

    @property
    def buy(self):
        return self.price_mgr.buy
        
    def update_price(self):
        self.price_mgr.update_price()

        for price in (price for price in self.buy_limits if price >= self.sell):
            self.owned += self.buy_limits[price]
            self.buy_limits[price] = 0
        for price in (_ for _ in self.sell_limits if _ <= self.buy):
            self.cash += self.sell_limits[price] * price
            self.sell_limits[price] = 0
        
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
            if user_in == 'd' and self.owned > 0:
                self.owned -= 1
                self.sell_limits[self.sell] += 1
            if user_in == 'n' and self.cash > self.buy:
                self.cash -= self.buy
                self.buy_limits[self.buy] += 1
            if user_in == 'x':
                for price in self.buy_limits:
                    self.cash += price * self.buy_limits[price]
                    self.buy_limits[price] = 0
                for price in self.sell_limits:
                    self.owned += self.sell_limits[price]
                    self.sell_limits[price] = 0

    @property
    def value(self):
        return (self.cash + self.owned*self.buy
                + sum(k * v for k, v in self.buy_limits.items())
                + sum(k*v for k, v in self.sell_limits.items()))

    def run(self, screen):
        screen.nodelay(True)
        while True:
            if time.time() < self.render_time + REFRESH_TIME:
                time.sleep((self.render_time + REFRESH_TIME) - time.time())
            screen.erase()
            output = [
                'Cash: ${:,.2f}      Shares: {}'.format(self.cash, self.owned),
                'Buy: ${:,.2f}       Sell: {:,.2f}'.format(self.buy, self.sell),
                'Value: ${:,.2f}      Gain: {:,.1f}%'.format(self.value, ((self.value - STARTING_CASH) / STARTING_CASH)*100),
                'Debug: {}'.format(self.debug_str),
            ]
            output.append('{:<40}{:>40}'.format('Limit Buy Orders', 'Limit Sell Orders'))
            buys = [(price, self.buy_limits[price]) for price in self.buy_limits if self.buy_limits[price]]
            buys = sorted(buys, key=lambda x: x[0])
            sells = [(price, self.sell_limits[price]) for price in self.sell_limits if self.sell_limits[price]]
            sells = sorted(sells, key=lambda x: x[0])
            for buy_tup, sell_tup in itertools.izip_longest(buys, sells):
                buy_msg = ''
                if buy_tup:
                    buy_msg = "${:,.2f} - {} shares".format(buy_tup[0], buy_tup[1])
                sell_msg = ''
                if sell_tup:
                    sell_msg = "${:,.2f} - {} shares".format(sell_tup[0], sell_tup[1])
                output.append('{:<40}{:>40}'.format(buy_msg, sell_msg))
            output += self.draw_graph(self.price_mgr.price_history)
            for i, s in enumerate(output):
                screen.addstr(i, 0, s)
            self.render_time = time.time()
            self.process_input(screen)
            self.update_price()

            if time.time() <= self.price_mgr.price_time:
                self.update_price()
            # self.debug_str = 'trend_up={}'.format(self.trend_up)

if __name__ == '__main__':
    game = ShavingGame()
    curses.wrapper(game.run)
