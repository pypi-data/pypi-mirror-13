#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""The module is for run function within special interval"""


from datetime import datetime, timedelta
from threading import Timer
import math
from time import sleep

__author__ = 'pb'


class IntervalTimer(object):
    """
        This class is for run task in delay thread periodically
    """

    def __init__(self, task_list=[], parameters_dict={}, interval=1):
        if type(interval).__name__ == "int" or type(interval).__name__ == "float":
            self.interval = interval

        if task_list is not None:
            self.task_list = task_list if type(task_list) == list else [task_list]

        if parameters_dict is not None:
            self.parameters_dict = parameters_dict if type(parameters_dict) == dict else dict()

    def run(self):
        start_time = datetime.now()
        for task in self.task_list:
            if task.__name__ in self.parameters_dict.keys():
                task(*self.parameters_dict[task.__name__])
        finish_time = datetime.now()

        if start_time + timedelta(seconds=self.interval) > finish_time + timedelta(microseconds=10):  # All tasks are finished before the interval time expired
            next_start_time = start_time + timedelta(seconds=self.interval) - finish_time
        else:
            next_start_time = start_time + timedelta(seconds=math.ceil((finish_time-start_time).total_seconds()/self.interval)*self.interval) - finish_time
        Timer(next_start_time.total_seconds(), self.run).start()

    def start(self):
        Timer(self.interval, self.run).start()



if __name__ == '__main__':
    def say_hello1(name):
        sleep(0.6)
        print(str(datetime.now().time()) + ' : hello1 ' + name)
    def say_hello2(name):
        sleep(0.6)
        print(str(datetime.now().time()) + ' : hello2 ' + name)
    say_hello1("test")
    t = IntervalTimer([say_hello1, say_hello2], {"say_hello1": ["pb"], "say_hello2": ["n2"]},  1)
    t.start()