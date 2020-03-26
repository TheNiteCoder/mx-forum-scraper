
import requestor
import pagination

import subprocess
import phpbb

import argparse
session = requestor.Session()
session.login('https://forum.mxlinux.org/login.php', 'Nite Coder', '02commandercody08')

req = requestor.Requestor(session=session)

mainpage = phpbb.SubForum('https://forum.mxlinux.org/viewforum.php?f=104')

url = 'https://forum.mxlinux.org'

postpage = phpbb.SubForum(url)

page1 = postpage.pages.at(0)

for section in page1.sections:
    for post in section.items:
        print('==========')
        print(post.title)





