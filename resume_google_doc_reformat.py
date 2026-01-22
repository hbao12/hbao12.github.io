from bs4 import BeautifulSoup

# read in html file

with open('Resume_V2.html', 'r', encoding='utf-8') as file:
    html_content = file.read()

# reformat indents

html_content = html_content.replace("list-style-position:inside", "list-style-position:outside").replace("text-indent:45pt", '""')
soup = BeautifulSoup(html_content, 'html.parser')
prettified_html = soup.prettify()

# write file

with open("resume.html", "w") as file:
    file.write(prettified_html)