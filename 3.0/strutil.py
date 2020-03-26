
from bs4 import NavigableString, BeautifulSoup, Tag, Comment
import soupsieve as sv

def stringify(tag):
    # return str(tag.encode('utf-8'))
    return str(tag)

def extact_code(code):
    content = code.select_one('code')
    return extract(content)

def extract(tag):
    if type(tag) is NavigableString:
        return stringify(tag)
    if type(tag) is Comment:
        return str()
    text = ''
    for item in tag.contents:
        if type(item) is NavigableString:
            text += stringify(item)
        elif type(item) is Comment:
            pass
        elif item.name == 'br':
            text += '\n'
        elif item.name == 'p':
            text += '\n'
            text += extract(item)
        elif item.name == 'b':
#            text += '[b]'
            text += extract(item)
#            text += '[/b]'
#        elif item.name == 'i':
#            text += '[i]'
#            text += extract(item)
#            text += '[/i]'
        elif sv.match('div.codebox', item):
            text += '[code]'
            text += extact_code(item)
            text += '[/code]'
        else:
            text += '\n'
            text += extract(item) 
    return text


