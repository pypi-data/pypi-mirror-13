from datetime import datetime, timedelta

frmstr = '%Y-%m-%dT%H:%M:%S'
collectionlimit = 31    # days
now = datetime.now()
past180 = now - timedelta(days=180)
colltill = past180 + timedelta(days=collectionlimit)

print('now      = {}'.format(now.strftime(frmstr)))
print('past180  = {}'.format(past180.strftime(frmstr)))
print('colltill = {}'.format(colltill.strftime(frmstr)))


indate = '2015-12-02T13:28:41+0100'

print(indate[:-5])
print(indate.split('+')[0])
conv = datetime.strptime(indate.split('+')[0], frmstr)
print(datetime.strftime(conv, frmstr))