from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import re
import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np

#날짜 입력
print("="*50+"\n\t   이 날은 얼마나 따뜻해졌을까?"+"\n"+"="*50)
query_txt = input(print("날짜를 입력해주세요(MMMM/YY/DD) : "))
#query_txt = str(19651213)
year = int(query_txt[:4])
month = int(query_txt[4:6])
day = int(query_txt[6:])

#사이트 주소 생성
start_year = 1960
site_1 = "https://www.weather.go.kr/w/obs-climate/land/past-obs/obs-by-day.do?stn=108&yy="
site_2 = "&mm="
site_3 = "&obs=1"

#크롬 드라이버
options = webdriver.ChromeOptions()
options.add_argument("headless")
options.add_argument("disable-gpu")
driver = webdriver.Chrome(options=options)
go = True
purify, avg_temp, high_temp, low_temp, avg_cloud, avg_rain, all_year = ([] for _ in range(7))
s_time = time.time()
while(go):
    purify=[]
    driver.get(site_1+str(start_year)+site_2+str(month)+site_3)
    time.sleep(1)

    date = 0
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    content = soup.find_all(class_='table-col table-cal')
    content = soup.find_all('td')

    #텍스트 정제
    def clean_txt(element):
        return element.get_text().replace('\n','').replace('℃','').replace('\xa0','').replace(' ','')

    for i in content:
        purify.append(clean_txt(i))
    purify = [item for item in purify if len(item) >= 4]
    purify = list(filter(None, purify))

    #데이터 저장
    for element in purify:
        match_1 = re.search('평균기온:(.*?)\최고',element)
        if match_1 is not None:
            date = date+1
            if day == date :
                all_year.append(start_year)
                avg_temp.append(match_1.group(1))

        match_2 = re.search('최고기온:(.*?)\최저',element)
        if match_2 is not None:
            if day == date:
                high_temp.append(match_2.group(1))

        match_3 = re.search('최저기온:(.*?)\평균',element)
        if match_3 is not None:
            if day == date:
                low_temp.append(match_3.group(1))

        match_4 = re.search('운량:(.*?)\일',element)
        if match_4 is not None:
            if day == date:
                avg_cloud.append(match_4.group(1))
                
        match_5 = re.search('수량:(.*?)mm',element)
        if match_5 is not None:
            if day == date:
                avg_rain.append(match_5.group(1))
        elif match_5 is None:
            if day == date:
                avg_rain.append(0)
    
    start_year+=1
    if(start_year > year):
        go = False

#데이터 프레임 생성 및 csv 저장
df = pd.DataFrame({
    'Year': all_year,
    'Avg.temp': avg_temp,
    'High.temp': high_temp,
    'Low.temp': low_temp,
    'Avg.cloud': avg_cloud,
    'Avg.rain': avg_rain
})

df.to_csv("c:\personal_python\Weather\weather_data.csv", index=False)

e_time = time.time()
t_time = e_time - s_time
print("총 소요시간은 %s 초 입니다" %round(t_time,1))

#그래프그리기
df['Avg.temp'] = df['Avg.temp'].astype(float)   #데이터 실수화
df['High.temp'] = df['High.temp'].astype(float)
df['Low.temp'] = df['Low.temp'].astype(float)
df['Avg.cloud'] = df['Avg.cloud'].astype(float)
df['Avg.rain'] = df['Avg.rain'].astype(float)

x = df['Year']
y1 = df['Avg.temp']
y2 = df['High.temp']
y3 = df['Low.temp']
y4 = df['Avg.cloud']
y5 = df['Avg.rain']

#선그래프
fig, ax1 = plt.subplots()

ax1.plot(x, y1, color='g', alpha=0.5, label='Avg.temp', linewidth = 2, marker='o')
ax1.plot(x, y2, color='r', alpha=0.5, label='High.temp', linewidth = 2, marker='o')
ax1.plot(x, y3, color='b', alpha=0.5, label='Low.temp', linewidth = 2, marker='o')

ax1.set_yticks(np.arange(min(min(y1), min(y2), min(y3)), max(max(y1), max(y2), max(y3))+1, 1.0))    #Y축 범위 지정
ax1.legend(loc='upper left')    #범례
plt.xticks(x, rotation=45, fontsize='small')    #X축 설정
ax1.set_ylabel('temperture')    #Y축 라벨 지정

ax2 = ax1.twinx()   #오른쪽에 y축 하나 더 만들기

ax2.bar(x, y4, color='gray', alpha=0.5, label='Avg.cloud')
ax2.bar(x, y5, color='c', alpha=0.5, label='Avg.rain')

ax2.set_yticks(np.arange(min(min(y4), min(y5)), max(max(y4), max(y5))+1, 1.0))
ax2.legend(loc='upper right')
ax2.set_ylabel('cloud/rain')

plt.title("1960."+str(month)+"."+str(day)+"~"+str(start_year-1)+"."+str(month)+"."+str(day))
plt.xlabel("year")

plt.show()