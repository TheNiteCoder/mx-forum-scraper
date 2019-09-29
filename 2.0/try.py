#!/usr/bin/python3
import forum 
import requestor
import curses

session = requestor.Session()

req = requestor.Requestor(session=session)

f = forum.ForumPage('https://forum.mxlinux.org')
f.construct(req)




