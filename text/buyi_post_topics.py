from urllib.request import urlopen
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

records_lst =[]
for idx in range(10):   # There are 1470 pages, for each there is 50 records.
    print(idx)
    URL = 'http://www.booyee.com.cn/bbs/list.jsp?startrow={}&startflag=1'.format(idx*50)
    bbspage = requests.get(URL)
    text = bbspage.text

    soup = BeautifulSoup(text.encode('utf-8','ignore'), 'html.parser', )
    txt_table = soup.findAll('table',{"class":"txt"})
    records = txt_table[1].findAll('tr')
    
    for record in records:        #Records only with "[蠹鱼会]" are selected.
        
        if "[蠹鱼会]" in record.text:
            record_lst = []      # for each desired record all relevant elements are stored into a list

            for elem in record.find_all('td'):
                if elem.text:
                    record_lst.append(elem.text.replace('\n','').replace('\r','').replace(' ',''))
                
                    print(elem.text)

                if elem.find_all('a'):
                    for ref in elem.find_all('a'):
                        print(ref.attrs['href'].split('=')[1])
                        record_lst.append(ref.attrs['href'].split('=')[1])

            records_lst.append(record_lst)

print('Finshed scraping.')
print('Scraping records: {}'.format(len(records_lst)))


records_df = pd.DataFrame(np.array(records_lst), columns=['Topic','PostID','Author','AuthorID','Reply/Click','LastUpdate','Follower','FollowerID'])

### convert Reply/Click into two columns
reply_lst = records_df['Reply/Click'].str.split('/')
clicks = [click[1] for click in reply_lst]
replies = [reply[0] for reply in reply_lst]

records_df.insert(loc=4, column='Reply', value=replies)
records_df.insert(loc=5, column='Click', value=clicks)
records_df = records_df.drop(['Reply/Click'],axis=1)


### convert LastUpdate into two columns ['LastUpdate_date', 'LastUpdate_time']
records_df.insert(loc= 6, column='LastUpdate_date', value=records_df.LastUpdate.str[:10])
records_df.insert(loc= 7, column='LastUpdate_time', value=records_df.LastUpdate.str[10:])
records_df = records_df.drop(['LastUpdate'], axis=1)

records_df.index += 1
records_df.to_csv('Posts_{}.csv'.format(len(records_df)), encoding='utf_8_sig')