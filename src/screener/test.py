from datetime import datetime, timedelta

now = datetime.now()
datetime_str = '02/02/24 07:35:26'
datetime_object = datetime.strptime(datetime_str, '%m/%d/%y %H:%M:%S')
if now-timedelta(hours=4) <= datetime_object <= now:
    print("è dentro le 4 ore!")
else:
    print("è fuori!")