import re

with open('Glossary.html') as f:
    text = f.read()
    h4_regex = r'<h4>(.*)</h4>'
    res = re.findall(h4_regex, text)
    with open('short_glossary', 'w') as g:
        for line in res:
            g.write(line + '\n')
