class CronExecutor(object):
    def __init__(self):
        # cron cache key is {<Date String YYY-mm-dd>: {<timestamp>: [<string command 1>...]}
        self._cache = {} 

