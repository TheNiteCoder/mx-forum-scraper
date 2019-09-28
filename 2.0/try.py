
import forum 
import requestor
import curses

session = requestor.Session()
session.login('https://forum.mxlinux.org/login.php', 'TheNiteCoder', '02commandercody08')

req = requestor.Requestor(session=session)

f = forum.ForumPage('https://forum.mxlinux.org')
f.construct(req)

print('=== ' + f.title + ' ===')

for section in f.sections:
    for item in section.items:
        if type(item) is forum.TopicView:
            print(item.title)
