try: import displaying.LCD_2004
except: pass

import threading
import os
import daemon.utils as utils
import telebot
import time
from termcolor import colored
import timetable.utils
import configuration
from datetime import datetime
import daemon.ring_callbacks as ring_callbacks

class Daemon(threading.Thread):
    today_timetable: list
    muted_rings: list
    order = 0
    last_called_timing: str = '00:00'
    next_called_timing: str = '00:00'
    gpio_mode = False
    debugger : telebot.TeleBot
    day: int
    status: bool = True

    def __init__(self, table, muted):
        super().__init__()
        self.daemon = True
        self.update(table, muted)
        self.day = datetime.now().day

        if (os.system('echo 1 > /sys/class/gpio10/value && echo 0 > /sys/class/gpio10/value') == 0):
            self.gpio_mode = True
        
        ring_callbacks.init()
        self.update_ring_order()

        try: displaying.LCD_2004.initial_output(self.today_timetable)
        except: print("[GPIO] .initial_output")

    def update_ring_order(self):
        self.order = utils.nearest_forward_ring_index(self.today_timetable)

    def update(self, new_timetable, new_muted):
        self.today_timetable, self.muted_rings = new_timetable, new_muted # Обращаться к sqlite из другого потока нельзя
        self.today_timetable = list(map(lambda e: e.zfill(5), self.today_timetable))
        
        try: displaying.LCD_2004.update(self.today_timetable, self.order, self.next_called_timing)
        except: print("[GPIO] .update")

        print(colored('[DAEMON] ', 'blue') + "Updated timetable:", self.today_timetable)
        print(colored('[DAEMON] ', 'blue') + "Updated muted list:", *self.muted_rings)

    def run(self):
        while self.status:
            time.sleep(1)
            timing = str(datetime.now().time())[:5]
            timing_forward = timetable.utils.sum_times(timing, configuration.pre_ring_delta)

            if (timing == '00:00' and datetime.now().day != self.day): 
                self.update(*timetable.getting.get_time(datetime.now()))
                self.day = datetime.now().day

            if (timing in self.today_timetable and timing != self.last_called_timing):
                self.order += 1

                self.order = self.today_timetable.index(str(datetime.now().time())[:5])

                if self.muted_rings[self.order] == 0:
                    ring_callbacks.start_ring()
                    for id in configuration.debug_info_receivers:
                        self.debugger.send_message(id, '🛎️  Звонок по расписанию успешно подан')

                    self.last_called_timing = timing
                    time.sleep(configuration.ring_duration)
                    ring_callbacks.stop_ring()
                else:
                    print(f'No ring (muted ring at {timing})')
                    self.last_called_timing = timing
                    for id in configuration.debug_info_receivers:
                        self.debugger.send_message(id, '🚫 Звонок по расписанию заглушен и не подан')

                tempIdx = self.today_timetable.index(timing)
                if tempIdx != len(self.today_timetable)-1:
                    self.next_called_timing = self.today_timetable[tempIdx+1]

                    try: displaying.LCD_2004.next(self.today_timetable, tempIdx+1)
                    except: print("[GPIO] .next")

                else:
                    self.next_called_timing = "-1" # no more rings for today
                    
                    try: displaying.LCD_2004.no_more_rings()
                    except: print("[GPIO] .no_more_rings")

                    for id in configuration.debug_info_receivers:
                        self.debugger.send_message(id, '⏰ Сегодня больше нет звонков')
                
                if self.order + 1 <= len(self.today_timetable) - 1:
                    if self.today_timetable[self.order+1] == self.today_timetable[self.order]:
                        try: displaying.LCD_2004.next(self.today_timetable, self.order+1)
                        except: print("[GPIO] .next")

            if (timing_forward in self.today_timetable and timing != self.last_called_timing):
                self.order = self.today_timetable.index(timing_forward)

                if self.order % 2 != 0: continue

                if self.muted_rings[self.order] == 0:
                    ring_callbacks.start_pre_ring()

                    for id in configuration.debug_info_receivers:
                        self.debugger.send_message(id, '🧨  Предзвонок по расписанию успешно подан')

                    self.last_called_timing = timing
                    time.sleep(configuration.pre_ring_duration)
                    ring_callbacks.stop_ring()
                    self.last_called_timing = timing
                else:
                    print(f'No prering (muted ring at {timing})')
                    self.last_called_timing = timing

        try: displaying.LCD_2004.next(self.next_called_timing)
        except: print("[GPIO] .next")

    def instant_ring(self, duration: float):
        ring_callbacks.start_ring()
        for id in configuration.debug_info_receivers:
            self.debugger.send_message(id, '🛎️  Ручной звонок успешно подан')
        time.sleep(duration if duration <= configuration.max_ring_duration else configuration.max_ring_duration)
        ring_callbacks.stop_ring()
