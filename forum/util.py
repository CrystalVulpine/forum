import datetime

def time_ago(timestamp):
    age = int(datetime.datetime.utcnow().timestamp()) - timestamp

    if age < 60:
            return "just now"
    elif age < 3600:
        minutes = int(age / 60)
        if minutes == 1:
            return "1 minute ago"
        else:
            return str(minutes) + " minutes ago"
    elif age < 86400:
        hours = int(age / 3600)
        if hours == 1:
            return "1 hour ago"
        else:
            return str(hours) + " hours ago"
    elif age < 2592000:
        days = int(age / 86400)
        if days == 1:
            return "1 day ago"
        else:
            return str(days) + " days ago"
    elif age < 31536000:
        months = int(age / 2592000)
        if months == 1:
            return "1 month ago"
        else:
            return str(months) + " months ago"
    else:
        years = int(age / 31536000)
        if years == 1:
            return "1 year ago"
        else:
            return str(years) + " years ago"

