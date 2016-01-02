## Islamic Cron Jobs
This script enables system admins and Linux/Unix users to create cron jobs that run according to the Hijri calendar and can be related to prayer times.
For example, if you would like a reminder about Zakah every Hijri year, or if you want to reminder about fasting the 13, 14 and 15th days of every Hijri month, or if you wanto a simple reminder about something before Asr prayer on Friday.

### Installation
- Download the code and put it in a folder.
- Copy the file crontabs/islamic_cron.tab.default and edit the copy by adding your jobs
  cp crontabs/islamic_cron.tab.default crontabs/my_cron.tab

- Run the script as follows:
  cd /path_to_script && ./islamic_crond.py crontabs/my_cron.tab

**Set the URL to pull the prayer times**
Navigate to the corresponding link for the monthly prayer times of your city in Islamicfinder.com 
Here is an example for Doha, Qatar
http://www.islamicfinder.org/prayerDetail.php?country=qatar&city=Doha&state=01&id=719&month=&year=&email=&home=2015-12-28&lang=&aversion=&athan=&monthly=1

Then click on the right button of "Monthly Schedule" which will open a print friendly version like this:
http://www.islamicfinder.org/prayerPrintable.php?city2=Doha&state=01&id=719&longi=51.5333&lati=25.2867&country2=Qatar&zipcode=&today_date_flag=2015-12-28&changeTime=16&pmethod=4&HanfiShafi=1&dhuhrInterval=1&maghribInterval=1&dayLight=0&dayl=0&timez=3.00&dayLight_self_change=&prayerCustomize=&lang=&fajrTwilight=0&ishaTwilight=0&ishaInterval=0&month=12&year=2015

remove the month and the year attributes from the end of the URL and set it in the URL constant on the top of the file

### Future work:
- Better Unit testing
- Cleaner code
- Support for windows
- Better validation for crontab file


