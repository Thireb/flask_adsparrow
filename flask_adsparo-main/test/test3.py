from bs4 import BeautifulSoup as bs
from rich import print

# f_name = 'test/thing-497762418942517.html'
f_name = "..\\thing-677530023619473.html"
# f_name = 'thing-497762418942517.html'
file = open(f_name,'r')
x = file.read()
file.close()

bx = bs(x,'html.parser')

all_span = []


all_span.append(bx.find_all('span')[0].getText()) # Profile
all_span.append(bx.find_all('span')[3].getText()) # Paid By
# if bx.find_all('span')[9].getText().lower() == 'learn more':
#     all_span.append(bx.find_all('span')[8].getText()) # main_text
# else:
#     all_span.append(bx.find_all('span')[9].getText()) # main_text



# all_span = bx.get_text()

# for 
# all_text = all_span.replace('\n',' ').split(' ')
# print()


print(bx.find_all('div', class_="_4ik4 _4ik5")[1].getText())

# print(type(all_span))


for i in range(len(all_span)):
    if all_span[i].__contains__('\n'):
        all_span[i] = all_span[i].replace("\n", " ")
print(all_span)

all_img = bx.find_all('img')

img_link = []

for img in all_img:
    img_link.append(img.get('src'))

# print(img_link)

all_links = bx.find_all('a')

links = []

for link in all_links:
    links.append(link.get('href'))

# print(links)

'''
https://l.facebook.com/l.php?u=https%3A%2F%2Foregonlive.com%2Feducation%2F2022%2F10%2Foregon-school-performance-craters-relative-to-national-averages-elementary-and-middle-school-math-scores-rank-6th-worst-in-us.html&h=AT22CgP5nO0Lq56HUAQk6oZv_2Uak_qMvHlxsDVRxsQNfJA5FvjS3qrb_1daI4M_vUW0v8--1IzpTyODjo209P-HSPPElUiAaBNesE1ZuyiigMdcqvfHNQL8FA2lv_QL0OUdHmvRTJC9ZA
'''
'''
https://l.facebook.com/l.php?u=https%3A%2F%2Foregonlive.com%2Feducation%2F2022%2F10%2Foregon-school-performance-craters-relative-to-national-averages-elementary-and-middle-school-math-scores-rank-6th-worst-in-us.html&h=AT22CgP5nO0Lq56HUAQk6oZv_2Uak_qMvHlxsDVRxsQNfJA5FvjS3qrb_1daI4M_vUW0v8--1IzpTyODjo209P-HSPPElUiAaBNesE1ZuyiigMdcqvfHNQL8FA2lv_QL0OUdHmvRTJC9ZA
'''