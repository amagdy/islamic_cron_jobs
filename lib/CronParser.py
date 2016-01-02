from CronParseError import CronParseError
import os
import re

NUMBER_OF_FIELDS = 8
EXTREME_NEGATIVE_MINUTE_OFFSET = -1000
EXTREME_POSITIVE_MINUTE_OFFSET =  1000

def if_not_in_range_raise_error(field_name, value, start, inclusive_end):
    if value not in xrange(start, inclusive_end+1):
        raise CronParseError("{0} cannot be {1} it must be between {2} and {3}".format(field_name, value, start, inclusive_end))

def sanitize_range(value, start, inclusive_end, field_name):
    if value == "*":
        return xrange(start, inclusive_end+1)
    elif re.match(r'^[0-9]+$', value):
        value = int(value)
        if_not_in_range_raise_error(field_name, value, start, inclusive_end)       
        return [value]
    elif re.match(r'^[0-9]+(,[0-9]+)+$', value):
        arr_values = [int(v) for v in value.split(",")]
        for single_value in arr_values:
            if_not_in_range_raise_error(field_name, single_value, start, inclusive_end)
        return arr_values
    else:
        raise CronParseError("value cannot be {0}".format(value))


def sanitize_month(value, field_name):
    return sanitize_range(value, 1, 12, field_name)

def sanitize_day_of_month(value, field_name, is_hijri=False):
    if is_hijri:
        last_day_of_month = 30
    else:
        last_day_of_month = 31
    return sanitize_range(value, 1, last_day_of_month, field_name)

def sanitize_day_of_week(value):
    return sanitize_range(value, 0, 6, "Day of week")

def sanitize_prayer(value):
    return sanitize_range(value, 0, 5, "Prayers")

def sanitize_minutes(value):
    if re.match(r'^-?[0-9]+$', value) != None:
        value = int(value)
        if value >= EXTREME_NEGATIVE_MINUTE_OFFSET and value <= EXTREME_POSITIVE_MINUTE_OFFSET:
            return value    
    raise CronParseError("Minutes offset must be an integer between {0} and {1}".format(EXTREME_NEGATIVE_MINUTE_OFFSET, EXTREME_POSITIVE_MINUTE_OFFSET))


class CronParser(object):

    def _get_file_path(self, cron):
        directory = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.realpath("{}/../cache/{}_{}.bin".format(directory, time_instance.getYear(), time_instance.getMonth()))
        return file_path


    def _is_comment_or_empty_line(self, line):
        if re.match(r'^ *#', line) is not None: return True
        if re.match(r'^[\s\t]*$', line) is not None: return True
        return False


    def _is_import_line(self, line):
        return re.match(r'^ *@import', line) is not None

    def _get_imported_file_path(self, line):
        return os.path.realpath( re.search(r'^ *@import *\( *\"? *([^\(\)\"]+) *\"? *\) *', line).group(1) )

    def _parse_line(self, line):
        parts = re.split(r'[\s\t]+', line.strip())
        if len(parts) < NUMBER_OF_FIELDS:
            raise CronParseError("The line should have {0} fields, only {1} were found.".format(NUMBER_OF_FIELDS, len(parts)))
        hash_cron_entry = {
                "gm":   sanitize_month (         parts[0]    , "Gregorian month"),
                "gd":   sanitize_day_of_month (  parts[1]    , "Gregorian day of month"),
                "hm":   sanitize_month (         parts[2]    , "Hijri month"),
                "hd":   sanitize_day_of_month (  parts[3]    , "Hijri day of month", is_hijri=True),
                "dow":  sanitize_day_of_week (   parts[4]    ),
                "pr":   sanitize_prayer (        parts[5]    ),
                "min":  sanitize_minutes (       parts[6]    ),
                "cmd":  " ".join (               parts[7:]   )
            }
        return hash_cron_entry


    """
    Returns this array of cron entries as dictionaries :
    [
        {
            "gm":   xrange(1, 13),
            "gd":   xrange(1, 32),
            "hm":   xrange(1, 13),
            "hd":   xrange(1, 31),
            "dow":  xrange(0, 7),
            "pr":   xrange(0, 6),
            "min":  0,
            "cmd":  "cmd \"commend\" $gm $gd $hm $hd $dow $pr $min"
        }
    ]
    This stands for 
    * * * * * * 0 cmd "commend" $gm $gd $hm $hd $dow $pr $min
    """
    def readCrontabFile(self, cron_file_path):
        cron_file_path = os.path.realpath(cron_file_path)
        cron_file = open(cron_file_path, 'r')
        lines = cron_file.read().split("\n")
        cron_file.close()
        arr_cron_entries = []
        i = 1
        for line in lines:
            if self._is_comment_or_empty_line(line):
                pass
            elif self._is_import_line(line):
                imported_file_path = self._get_imported_file_path(line)
                arr_imported_file_rules = self.readCrontabFile( imported_file_path )
                arr_cron_entries.extend( arr_imported_file_rules )
            else:
                try:
                    entry = self._parse_line(line)
                    arr_cron_entries.append(entry)
                except CronParseError as e:
                    raise CronParseError(str(e.args) + ": File= {0} - Line: {1}".format(cron_file_path, i))
            i += 1 
        return arr_cron_entries