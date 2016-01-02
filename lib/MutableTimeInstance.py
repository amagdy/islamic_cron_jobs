from TimeInstance import TimeInstance
import time
import datetime

class MutableTimeInstance(TimeInstance):

    def __init__(self, initial_timestamp=int(time.time())):
        TimeInstance.__init__(self, initial_timestamp)
        self._reset_timestamp = initial_timestamp


    # accepts a time tuple (month, day, hour, minute)
    @classmethod
    def createInstanceByTimeTuple(cls, time_tuple):
        str_date_time = "%d/%d/%d %d:%d" % ((TimeInstance.now().getYear(), ) + time_tuple)
        timestamp = int( time.mktime( datetime.datetime.strptime(str_date_time, "%Y/%m/%d %H:%M").timetuple() ) )
        return MutableTimeInstance(timestamp)


    def reset(self):
        self._initial_timestamp = self._reset_timestamp


    def incrementSeconds(self, increment=60):
        self._initial_timestamp += increment
