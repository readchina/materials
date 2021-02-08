from urllib.request import urlopen
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

posts = pd.read_csv('Posts_22.csv')
file_idx = 0

for post, topic in zip(posts['PostID'], posts['Topic']):
    file_idx +=1

    ### Getting all content in this post by requesting URL
    URL = 'http://www.booyee.com.cn/bbs/thread.jsp?threadid={}&forumid=96&get=1'.format(post)
    bbspage = requests.get(URL)

    content_page = requests.get(URL)
    text = content_page.text

    soup = BeautifulSoup(text.encode('utf-8','ignore'), 'html.parser', )
    content = soup.find_all('table', attrs = {'style':'TABLE-LAYOUT: fixed'})

    ###dealing with the content postted by author
    answers = []
    user_tag, context = content[0].find_all('td')
    user_info = user_tag.text.strip().replace('\r','').replace('\xa0','').replace('\n','')

    user_id = user_tag.find('a').attrs['href']

    answers.append(user_id[user_id.find('userid=')+7:])
    answers.append(user_info[3:user_info.find(' ')])
    answers.append(user_info[user_info.find('提交日期：')+5:])

    context = context.text.strip().replace('\r','').replace('\xa0','').replace('\n','')
    print(context)
    answers.append(context)



    # dealing with the contents postted by all followers
    inhalt = content[1].find_all('td')

    for idx, answer in enumerate(inhalt[::2]):
        #print(idx)
        user_info = answer.text.strip().replace('\r','').replace('\xa0','').replace('\n','')
        #print(user_info)

        user_id = answer.find('a').attrs['href']

        answers.append(user_id[user_id.find('userid=')+7:])
        answers.append(user_info[3:user_info.find(' ')])
        answers.append(user_info[user_info.find('提交日期：')+5:])

        context = inhalt[idx*2+1].text.strip().replace('\r','').replace('\xa0','').replace('\n','')
        print(context)
        answers.append(context)

    #saving all contents into a dataframe
    answers_df = pd.DataFrame(np.array(answers).reshape(int(len(answers)/4), 4), columns=['AuthorID', 'Author', 'Reply','Text'])
    
    ### convert Reply information into two columns ['Reply_date', 'Reply_time']
    answers_df.insert(loc= 2, column='Reply_date', value=answers_df.Reply.str[:10])
    answers_df.insert(loc= 3, column='Reply_time', value=answers_df.Reply.str[11:])
    answers_df = answers_df.drop(['Reply'], axis=1)

    answers_df.to_csv('Posts_22/{}{}.csv'.format(topic[5:],post), encoding='utf_8_sig')
    print('Finished {}{}'.format(post,topic))
    print('Saving the {}th file ({} files) in the folder "I_1048"--------------------'.format(len(posts),file_idx))