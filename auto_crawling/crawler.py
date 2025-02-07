import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import config

class AirbnbfyCrawler:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # 백그라운드 실행
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        service = Service(config.CHROME_DRIVER_PATH)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    def open_site(self):
        """사이트 접속"""
        self.driver.get("https://airbnbfy.hanmesoft.com/")
        time.sleep(3)  # 페이지 로딩 대기

    def input_sentence(self, sentence):
        """문장을 입력"""
        try:
            # 입력창 찾기
            input_box = self.driver.find_element(By.CLASS_NAME, "form-control")
            input_box.clear()
            input_box.send_keys(sentence)  # 문장 입력
        except Exception as e:
            print(f"입력 실패: {sentence}, 오류: {e}")

    def click_convert_button(self):
        """변환 버튼을 여러 번 클릭하여 난독화된 문장 생성"""
        try:
            convert_button = self.driver.find_element(By.CLASS_NAME, "btn-primary")
            convert_button.click()
            time.sleep(1)  # 변환 대기

            # 변환된 문장 가져오기
            output_box = self.driver.find_elements(By.CLASS_NAME, "form-control")[-1]
            return output_box.get_attribute("value").strip()
        except Exception as e:
            print(f"변환 실패, 오류: {e}")
            return None

    def run(self, input_file="input_sentences.csv", output_file="results/obfuscated_sentences.csv"):
        df = pd.read_csv(input_file)
        review_count = config.review_count
        convert_count = config.convert_count

        results = []
        self.open_site()

        for i, row in df.iterrows():
            if i >= review_count:
                break  # 최대 review_count개만 처리

            original_text = row["리뷰"]
            self.input_sentence(original_text)  # 한 번만 입력

            for _ in range(convert_count):  # 변환 버튼만 여러 번 클릭
                obfuscated_text = self.click_convert_button()
                if obfuscated_text:
                    results.append({"원래 문장": original_text, "난독화된 문장": obfuscated_text})
                    # print(f"변환 완료: {original_text} → {obfuscated_text}")

        # 결과 저장
        results_df = pd.DataFrame(results)
        results_df.to_csv(output_file, index=False, encoding="utf-8-sig")
        print(f"크롤링 완료! 변환된 문장이 {output_file}에 저장됨.")

        # 브라우저 종료
        self.driver.quit()
