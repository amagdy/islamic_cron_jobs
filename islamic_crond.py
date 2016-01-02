#!/usr/bin/python
from lib import MutableTimeInstance
from lib import PrayerTimesGetter
from lib import TimeInstance
from lib import CronParser
from lib import CronParseError
import sys
import re
import time
import subprocess

def timeOffsetFromTimeTuple(time_tuple, minutes_offset):
    if minutes_offset == 0:
        return time_tuple
    else:
        mutable_time_instance = MutableTimeInstance.createInstanceByTimeTuple(time_tuple)
        mutable_time_instance.incrementSeconds(minutes_offset*60)
        return (mutable_time_instance.getMonth(), mutable_time_instance.getDayOfMonth(), mutable_time_instance.getHour(), mutable_time_instance.getMinute())


def evaluateCommandVariables(command, day_prayer_data, prayer_index, minutes_offset):
    variables = re.findall(r'\$([a-z]+)', command)
    command = command.replace('$pr', str(prayer_index))
    command = command.replace('$min', str(minutes_offset))
    for var in variables:
        command = command.replace('$'+var, str(day_prayer_data.get(var, '$'+var)))
    return command

# returns dictionary {<Tuple(month, day, hour, minute)>: <command with evaluated variables> }
def applyCronRules(cron_rules, days_prayer_times, time_instance):
    dict_times_and_commands = {}
    for day_prayer_data in days_prayer_times:
        for rule in cron_rules:
            if day_prayer_data['gm'] in rule['gm'] and day_prayer_data['gd'] in rule['gd'] and day_prayer_data['dow'] in rule['dow'] and day_prayer_data['hm'] in rule['hm'] and day_prayer_data['hd'] in rule['hd']:
                for prayer_index, prayer_time in day_prayer_data['pr'].items():
                    if prayer_index in rule['pr']:
                        key_time_tuple = timeOffsetFromTimeTuple((day_prayer_data['gm'], day_prayer_data['gd'], prayer_time[0], prayer_time[1]), rule['min'])
                        if key_time_tuple not in dict_times_and_commands:
                            dict_times_and_commands[key_time_tuple] = set([])
                        dict_times_and_commands[key_time_tuple].add( evaluateCommandVariables(rule['cmd'], day_prayer_data, prayer_index, rule['min']) )
    return dict_times_and_commands


def parseCommandToList(command):
    params = []
    raw_arr = []
    for tuple in re.findall(r' *"([^"]+)" *| *([^"\' \t]+) *| *\'([^\']+)\' *', command):
        raw_arr.extend(tuple)
    for param in raw_arr:
        if param != '':
            params.append(param)
    return params


def runCommandInBackground(command):
    command = parseCommandToList(command)
    subprocess.Popen(command)


if __name__ == "__main__":
    CRON_FILE = sys.argv[1]
    cron_parser = CronParser()
    cron_rules = cron_parser.readCrontabFile(CRON_FILE)
    prayer_time_getter = PrayerTimesGetter()
    now = None
    current_day = 0
    today_and_tomorrow_prayer_times = None
    daily_cron_rules = None
    while True:
        now = TimeInstance.now()
        if current_day != now.getDayOfMonth():
            current_day = now.getDayOfMonth()
            today_and_tomorrow_prayer_times = prayer_time_getter.getPrayerTimesForTodayAndTomorrow(now)
            daily_cron_rules = applyCronRules(cron_rules, today_and_tomorrow_prayer_times, now)
        key = now.getTimeTuple()
        commands = daily_cron_rules.get(key, [])
        if commands != []:
            for command in commands:
                runCommandInBackground(command)
        time.sleep(60)
