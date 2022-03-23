from cgitb import enable
from gettext import find
from signal import signal
from turtle import back
from xml.dom.minidom import Element
from selenium import webdriver
from appium import webdriver
from selenium.webdriver.common.by import By
# selenium에서 webdriver 가져오기
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from appium.webdriver.common.touch_action import TouchAction

import requests
import json

import random
import os
import cv2
import time
import pyperclip
import gspread
from oauth2client.service_account import ServiceAccountCredentials

##################################### 필독 ! #####################################
# 사전 셋팅 1. 단말에서는 Chrome 브라우저와 K STADIUM APP 모두 실행 중인 상태.
# 사전 셋팅 2. 실행 직전 화면은 Chrome 브라우저가 보여지는 상태.
# 사전 셋팅 3. Chrome 브라우저는 Explorer 화면이 보이도록 하며, '새 탭'을 하나 열어준 상태.
#################################################################################

## 구글 시트 연동
scope = [
'https://spreadsheets.google.com/feeds',
'https://www.googleapis.com/auth/drive',
]

# 다운로드 받은 json 파일명
json_file_name = 'magnetic-guild-344406-995fb0bf0ab3.json'
credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file_name, scope)
gc = gspread.authorize(credentials)

# 연동할 구글시트 url (작성될 문서에 따라 url 변경)
spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1n6RD-FGHSxRRxNOCghORfYwuDJ8d8x93xroOu9-QQNA/edit#gid=0'

# 스프레스시트 문서 가져오기 
doc = gc.open_by_url(spreadsheet_url)

# 시트 선택하기 (작성될 시트명에 따라 변경)
worksheet = doc.worksheet('sheet1')


## Appium 단말정보 입력
desired_caps = {
    "platformName": "Android",
    "appium:platformVersion": "11",
    "appium:deviceName": "GalaxyFold3",
    "appium:app": "Users/wayne/medium/autotest/appium/apk/kstadium--app-stage_0.8.26.apk",
    "appium:automationName": "UIAutomator2",
}

path = os.getcwd()
driver = webdriver.Remote('http://0.0.0.0:4723/wd/hub', desired_caps)
actions = TouchAction(driver)
driver.implicitly_wait(10)
wait = WebDriverWait

#view type 정의
appview = driver.contexts[0] #NATIVE_APP
chromeview = driver.contexts[1] #chrome
webview = driver.contexts[2] #KSTADIUM Webview

# webview 활용
driver.switch_to.context(driver.contexts[2])

# 변수
# 로그인 할 변수
id = "wayne2"
password = "qqqqqqq1"
# 구글시트에 입력되는 행/열
gs_write_row = 6
gs_write_col = 2

# 랜덤 숫자 생성 -> 10부터 100사이의 임의의 정수
# num = random.randint(10,100)


class KstadiumAPI:
    #ID/PW 입력하여 Access token 값 가져오기
    def get_id_accesstoken(login_id, password):
        #API 정보
        loginCookies = ''
        kstadium_url = 'https://app.stage.kstadium.io:8080/kstadium'
        api_url = kstadium_url + '/api/comm/member/login/login'
        headers = {
            'accept' : 'application/json',
            'X-AUTH-MOBILE' : 'true',
            'Content-Type' : 'application/json'
        }

        data = {"password": password, "userId": login_id}


        response = requests.post(api_url, headers=headers, data=json.dumps(data), cookies=loginCookies)

        res = json.loads(response.text) # response.text는 String type임. 이것을 json 형태로 변환

        access_token = res.get('data')
        
        return access_token['accessToken']
        
    # Access Token 값을 활용하여 해당 ID의 Address, KOK, SOP 정보 가져오기
    def get_assets_api(status, login_id, password):
        #해당 ID AccessToken 정보 가져오기
        token = KstadiumAPI.get_id_accesstoken(login_id, password)

        loginCookies = ''
        kstadium_url = 'https://app.stage.kstadium.io:8080/kstadium'
        api_url = kstadium_url + '/api/comm/octet/my/balance'

        headers = {
            'accept' : 'application/json',
            'X-AUTH-TOKEN' : token
        }
        #params = {'X-AUTH-TOKEN' : token}
        response = requests.get(api_url, headers=headers, cookies=loginCookies)

        res = json.loads(response.text) # response.text는 String type임. 이것을 json 형태로 변환

        data = res.get('data')
        # print('Address : ' + data['address'])
        # print('KOK : ' + data['KOK'])
        # print('SOP : ' + data['SOP'])
        wallet_address = data['address']
        wallet_kok_amount = data['KOK']
        wallet_sop_amount = data['SOP']
        if status == 'before':
            worksheet.update_cell(gs_write_row, gs_write_col, wallet_address)
            worksheet.update_cell(gs_write_row, gs_write_col+1, wallet_kok_amount)
            worksheet.update_cell(gs_write_row, gs_write_col+2,wallet_sop_amount)
        else:
            worksheet.update_cell(gs_write_row, gs_write_col+4, wallet_address)
            worksheet.update_cell(gs_write_row, gs_write_col+5, wallet_kok_amount)
            worksheet.update_cell(gs_write_row, gs_write_col+6,wallet_sop_amount)


class Kstadium:    


    #sign in 화면 진입
    def sign_in():
        # sign in 화면 진입
        driver.find_element(By.XPATH, '//ion-button[@id="btnSignIn"]').click()
        time.sleep(2)

        # id 입력
        driver.find_element(By.XPATH, '//input[@name="loginId"]').send_keys(str(id))
        time.sleep(1)

        #비밀번호 입력
        driver.find_element(By.XPATH, '//input[@name="loginPw"]').send_keys(str(password))
        time.sleep(2)
        
        submit_button = driver.find_element(By.XPATH, '//ion-button[@id="btnSignInSubmit"]')
        if submit_button.is_enabled():
            submit_button.click()
        else:
            print("ID/PW 재 확인 필요")
            driver.quit()
        
    def click_wallet(x, y):
        time.sleep(2)
        actions.tap(None, x, y, 1)
        actions.perform()
        time.sleep(2)
            
    ## Wallet 화면(전송 전)
    def wallet_before_send():
        # Wallet 주소 가져오기
        print("=======================================================================================")
        print("Step1 : 전송 전 [지갑주소 / KOK 수량 / SOP 수량]")
        time.sleep(2) 

        wallet_address = driver.find_element(By.XPATH, '//div[@id="root"]/ion-app/div/ion-tabs/div/ion-router-outlet/div[2]/ion-content/div[1]/div[1]/div/a')
        print("지갑주소:", wallet_address.text)

        # KOK 값 읽어오기
        wallet_kok_amount = driver.find_element(By.XPATH, '//div[@id="root"]/ion-app/div/ion-tabs/div/ion-router-outlet/div[2]/ion-content/div[2]/ion-list/ion-item[1]/ion-note')
        print("KOK 수량:", wallet_kok_amount.text)

        # SOP 값 읽어오기
        wallet_sop_amount = driver.find_element(By.XPATH, '//div[@id="root"]/ion-app/div/ion-tabs/div/ion-router-outlet/div[2]/ion-content/div[2]/ion-list/ion-item[2]/ion-note')
        print("SOP 수량:", wallet_sop_amount.text)

        # 구글시트에 기록
        worksheet.update_cell(gs_write_row, gs_write_col, wallet_address.text)
        worksheet.update_cell(gs_write_row, gs_write_col+1, wallet_kok_amount.text)
        worksheet.update_cell(gs_write_row, gs_write_col+2,wallet_sop_amount.text)

        print("=======================================================================================")

    ## Wallet 화면(전송 후)
    def wallet_after_send():
        # Wallet 주소 가져오기
        time.sleep(2)
        print("Step3: 전송 후 [지갑주소 / KOK 수량 / SOP 수량]")
        wallet_address = driver.find_element(By.XPATH, '//div[@id="root"]/ion-app/div/ion-tabs/div/ion-router-outlet/div[2]/ion-content/div[1]/div[1]/div/a')
        print("지갑주소:", wallet_address.text)

        # KOK 값 읽어오기
        wallet_kok_amount = driver.find_element(By.XPATH, '//div[@id="root"]/ion-app/div/ion-tabs/div/ion-router-outlet/div[2]/ion-content/div[2]/ion-list/ion-item[1]/ion-note')
        print("KOK 수량:", wallet_kok_amount.text)

        # SOP 값 읽어오기
        wallet_sop_amount = driver.find_element(By.XPATH, '//div[@id="root"]/ion-app/div/ion-tabs/div/ion-router-outlet/div[2]/ion-content/div[2]/ion-list/ion-item[2]/ion-note')
        print("SOP 수량:", wallet_sop_amount.text)

        # 구글시트에 기록
        worksheet.update_cell(gs_write_row, gs_write_col+4,wallet_address.text)
        worksheet.update_cell(gs_write_row, gs_write_col+5,wallet_kok_amount.text)
        worksheet.update_cell(gs_write_row, gs_write_col+6,wallet_sop_amount.text)

        print("=======================================================================================")            

    ## SEND TO COMMUNITYPOOL 화면 ##
    def send_stc():
        # SEND TO COMMUNITYPOOL 버튼 선택
        stc_btn = driver.find_element(By.XPATH, '//div[@id="root"]/ion-app/div/ion-tabs/div/ion-router-outlet/div[2]/ion-content/div[1]/div[2]/ion-button').click()
        time.sleep(3)

        # SEND TO COMMUNITYPOOL 약관 선택
        policy_check1 = driver.find_element(By.XPATH, '//ion-checkbox[@name="agreePolicy1"]').click()
        time.sleep(1)
        policy_check2 = driver.find_element(By.XPATH, '//ion-checkbox[@name="agreePolicy2"]').click()
        time.sleep(1)
        policy_check3 = driver.find_element(By.XPATH,'//ion-checkbox[@name="agreePolicy3"]').click()
        time.sleep(1)
        policy_check4 = driver.find_element(By.XPATH,'//ion-checkbox[@name="agreePolicy4"]').click()
        time.sleep(1)

        # SEND TO COMMUNITYPOOL Amount 양 입력
        stc_input_amount = driver.find_element(By.XPATH,'//input[@name="amount"]')
        
        for i in range(100):
            num = random.randint(10,100)

        stc_input_amount.send_keys(num)
        time.sleep(2)
        driver.press_keycode(4)

        # NEXT버튼 선택
        stc_next_btn = driver.find_element(By.XPATH, '//form[@id="frmSendToPool"]/div/ion-button').click()
        
    ## SEND TO COMMUNITYPOOL > Confirm화면
    def confirm_stc():
        print("Step2 : 보내는 주소 / 보내는 KOK 수량")
        # SendTo 값 읽어오기
        confrim_send_to = driver.find_element(By.XPATH, '//div[@id="root"]/ion-app/div/ion-tabs/div/ion-router-outlet/div[4]/ion-content/ion-list/div[1]/ion-row[1]/ion-col[3]')
        print("보내는 주소    :", confrim_send_to.text)
        time.sleep(2)

        # Amount 값 읽어오기
        confrim_Amount = driver.find_element(By.XPATH, '//div[@id="root"]/ion-app/div/ion-tabs/div/ion-router-outlet/div[4]/ion-content/ion-list/div[1]/ion-row[2]/ion-col[2]/strong')
        print("보내는 KOK 수량:", confrim_Amount.text)
        time.sleep(2)

        # 구글시트에 기록
        worksheet.update_cell(gs_write_row, gs_write_col+3,confrim_Amount.text)

        # SEND 버튼 선택
        confrim_send_btn = driver.find_element(By.XPATH, '//div[@id="root"]/ion-app/div/ion-tabs/div/ion-router-outlet/div[4]/ion-content/div/ion-button').click()

        #  OK 버튼 선택
        time.sleep(10)
        success_ok_btn = driver.find_element(By.XPATH, '//div[@id="ion-react-wrapper"]/ion-footer/ion-button').click()
        print("=======================================================================================")
        time.sleep(3)

    
    ## Explorer 수수료 및 전송 토큰 양 확인
    def explorer_amount_fee():
        # Explorer 접속 
        print("Step4: Explorer Fee / Amount")
        tr_hash_btn = driver.find_element(By.XPATH, '//div[@id="root"]/ion-app/div/ion-tabs/div/ion-router-outlet/div[2]/ion-content/div[3]/ul[1]/li[1]/div[2]/ion-button').click()
        time.sleep(3)

        # 현재 활성화 중인 뷰 확인
        print(driver.contexts)

        # 크롬뷰로 변환
        driver.switch_to.context(driver.contexts[1])

        # 트랜잭션 Hash 가져오기
        explorer_txn_block = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div/div/main/section/div/div/div[2]/table/tbody/tr[3]/td[2]')))
        # explorer_txn_block = driver.find_element(By.XPATH, '/html/body/div/div/main/section/div/div/div[2]/table/tbody/tr[3]/td[2]')
        print("Explorer 트랜잭션 BLOCK :",explorer_txn_block.text)

        # 트랜잭션 상태 확인
        explorer_txn_st = driver.find_element(By.XPATH, '/html/body/div/div/main/section/div/div/div[2]/table/tbody/tr[2]/td[2]')
        print("Explorer 트랜잭션 상태  :",explorer_txn_st.text)

        # 토큰 양 가져오기
        explorer_amount = driver.find_element(By.XPATH, '/html/body/div/div/main/section/div/div/div[2]/table/tbody/tr[7]/td[2]')
        print("Explorer 보내는 수량    :",explorer_amount.text)

        # 수수료 값 가져오기
        explorer_fee = driver.find_element(By.XPATH, '/html/body/div/div/main/section/div/div/div[2]/table/tbody/tr[8]/td[2]')
        print("Explorer 수수료         :",explorer_fee.text)

        # 구글시트에 기록
        worksheet.update_cell(gs_write_row, gs_write_col+7,explorer_txn_block.text)
        worksheet.update_cell(gs_write_row, gs_write_col+8,explorer_txn_st.text)
        worksheet.update_cell(gs_write_row, gs_write_col+9,explorer_amount.text)
        worksheet.update_cell(gs_write_row, gs_write_col+10,explorer_fee.text)
        driver.close()
        print("=======================================================================================")

        # K Stadium webview 전환
        driver.switch_to.context(driver.contexts[2])
        driver.press_keycode(187)
        time.sleep(3)
        driver.press_keycode(187)
        print(driver.contexts)

    ## Exlplore에서 K Stadium App으로
        

Kstadium.sign_in()
Kstadium.click_wallet(880, 1985)

for i in range(0, 100):
    # Kstadium.wallet_before_send()
    KstadiumAPI.get_assets_api('before', 'wayne2', 'qqqqqqq1')
    Kstadium.send_stc()
    Kstadium.confirm_stc()
    # Kstadium.wallet_after_send()
    KstadiumAPI.get_assets_api('after', 'wayne2', 'qqqqqqq1')
    Kstadium.explorer_amount_fee()
    gs_write_row += 1









