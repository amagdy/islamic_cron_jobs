import re
import os
import urllib2
from TimeInstance import TimeInstance

PRAYERS = ['fajr', 'shrooq', 'dhuhr', 'asr', 'maghrib', 'isha']
DAYS_OF_WEEK = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat']
class PrayerTimesGetter(object):
    def __init__(self):
        # Change this URL to match your city make sure that the URL does NOT contain the month and year params
        self._URL = "http://www.islamicfinder.org/prayerPrintable.php?city2=Krakow&state=77&id=24506&longi=19.9167&lati=50.0833&country2=Poland&zipcode=&today_date_flag=2015-12-28&changeTime=16&pmethod=1&HanfiShafi=1&dhuhrInterval=1&maghribInterval=1&dayLight=1&dayl=1&timez=1.00&dayLight_self_change=&prayerCustomize=&lang=&fajrTwilight=0&ishaTwilight=0&ishaInterval=0"
        self._cache = {}


    def _format_time(self, hour_minute, prayerName):
        (hour, minute) = hour_minute.split(":")
        hour = int(hour)
        minute = int(minute)
        if hour > 0 and hour < 12:
            if prayerName == 'dhuhr' and hour < 5:
                hour += 12
            else:
                if prayerName in PRAYERS[3:]:
                    hour += 12
        return (hour, minute)


    # @param time_instance : TimeInstance
    def _get_month_prayer_times_from_site(self, time_instance):
        month = time_instance.getMonth()
        month_url = "{0}&month={1}&year={2}".format(self._URL, month, time_instance.getYear())
        NUMBER_OF_FIELDS = 10
        RECORD_SEP = '#####'
        FIELD_SEP = '@@@@@'
        html = urllib2.urlopen(month_url).read()
        html = re.search(r'(<table [^>]* width=475[^>]*>([\d\D]+)<\/TABLE>)', html).group(2)
        html = re.sub(r'(?i)<(?!tr|th|td)[^>]*>[^>]*<\/(?!tr|th|td)>', '', html)
        html = re.sub(r'(?i)<\/tr>', RECORD_SEP, html)
        html = re.sub(r'(?i)<\/td>', FIELD_SEP, html)
        html = re.sub(r'<[^>]+>', '', html)
        html = html.replace('&nbsp;', '').strip()
        html = re.sub(r'Day' + FIELD_SEP + '[^#]+' + RECORD_SEP, '', html)
        html = html.replace("\n", '').strip()
        month_prayer_times = {}
        for day_line in html.split(RECORD_SEP):
            day_line = day_line.replace("/", FIELD_SEP)
            day_data = day_line.split(FIELD_SEP)
            day_data = [i.strip() for i in day_data]
            if len(day_data) >= NUMBER_OF_FIELDS: 
                day_of_week, gregorian_day, hijri_day, hijri_month,  = day_data[:4]
                prayers = dict(zip(PRAYERS, day_data[4:10]))
                prayers = {PRAYERS.index(k): self._format_time(v, k) for k, v in prayers.items()}
                day_prayer_times = {
                    "gm": month,
                    "gd": int(gregorian_day),
                    "dow": DAYS_OF_WEEK.index(day_of_week.lower()),
                    "hm": int(hijri_month),
                    "hd": int(hijri_day),
                    "pr": prayers
                }
                month_prayer_times[day_prayer_times["gd"]] = day_prayer_times
        return month_prayer_times


    def _get_file_path(self, time_instance):
        directory = os.path.dirname(os.path.realpath(__file__))
        directory = os.path.realpath("{}/../cache/{}_{}.bin".format(directory, time_instance.getYear(), time_instance.getMonth()))
        return directory


    def _write_prayer_times_to_file(self, month_prayer_times, time_instance):
        file_path = self._get_file_path(time_instance)
        target = open(file_path, 'w')
        target.truncate()
        target.write(str(month_prayer_times))
        target.close()


    def _read_prayer_times_from_file(self, time_instance):
        cache_key = self._get_cache_key_for_time(time_instance)
        if cache_key in self._cache:
            return self._cache[cache_key]
        file_path = self._get_file_path(time_instance)
        target = open(file_path, 'r')
        month_prayer_times = eval(target.read())
        target.close()
        return month_prayer_times


    def _get_cache_key_for_time(self, time_instance):
        return "{}_{}".format(time_instance.getYear(), time_instance.getMonth())


    def _cache_exists(self, time_instance):
        file_path = self._get_file_path(time_instance)
        return os.path.isfile(file_path)


    def _fetch_and_cache_month_prayer_times_or_return_if_in_cache(self, time_instance):
        cache_key = self._get_cache_key_for_time(time_instance)
        if self._cache_exists(time_instance):
            self._cache[cache_key] = self._read_prayer_times_from_file(time_instance)
        else: # file does not exist then get info from internet then cache it
            self._cache[cache_key] = self._get_month_prayer_times_from_site(time_instance)
            self._write_prayer_times_to_file(self._cache[cache_key], time_instance)
        return self._cache[cache_key]


    def getMonthPrayerTimes(self, time_instance):
        return self._fetch_and_cache_month_prayer_times_or_return_if_in_cache(time_instance)


    def getPrayerTimesForTodayAndTomorrow(self, today_time_instance):
        tomorrow = today_time_instance.getTimeInstanceForOffset(TimeInstance.DAY)
        time_instances = (today_time_instance, tomorrow)
        return [self._fetch_and_cache_month_prayer_times_or_return_if_in_cache(time_ins)[time_ins.getDayOfMonth()] for time_ins in time_instances]

