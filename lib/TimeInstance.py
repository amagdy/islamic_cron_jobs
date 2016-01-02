import time
import datetime

class TimeInstance(object):

    DAY = (24*3600)

    def _fix_timestamp_to_minutes(self, timestamp):
        return timestamp - (timestamp % 60)

    def __init__(self, initial_timestamp=int(time.time())):
        self._initial_timestamp = self._fix_timestamp_to_minutes(initial_timestamp)


    def getTimeTuple(self):
        return (self.getMonth(), self.getDayOfMonth(), self.getHour(), self.getMinute())


    def _get_time(self, format):
        return int(datetime.datetime.fromtimestamp(self._initial_timestamp).strftime(format))


    def getYear(self):
        return self._get_time("%Y")


    def getMonth(self):
        return self._get_time("%m")


    def getDayOfMonth(self):
        return self._get_time("%d")


    def getDayOfWeek(self):
        return self._get_time("%w")


    def getHour(self):
        return self._get_time("%H")


    def getMinute(self):
        return self._get_time("%M")


    def getTimeInstanceForOffset(self, offset):
        return TimeInstance(self._initial_timestamp + offset)

    @classmethod
    def now(cls):
        return cls(time.time())