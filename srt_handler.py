import tkinter as tk
from tkinter import messagebox
from tkinter import Toplevel, Label, Entry, Button, Spinbox, StringVar
from tkinter import ttk  # ttk 모듈 임포트

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import Select
import time

from types import SimpleNamespace

global_root = None  # 모듈 내 전역 변수
log_text = None  # 로그 텍스트 위젯도 전역 변수

def show_srt_interface(root):
    """SRT 핸들러 엔트리 포인트: 기존 화면에서 SRT 화면으로 전환"""
    clear_main_screen(root)  # 기존 화면 초기화
    show_srt_intro(root)     # SRT 안내문구 표시

def clear_main_screen(root):
    """메인 화면의 모든 위젯 제거"""
    for widget in root.winfo_children():
        widget.destroy()



# 태그 스타일 정의
TAGS = SimpleNamespace(
    BOLD="${bold}",
    BOLD_END="${/bold}",
    RED="${color:red}",
    RED_END="${/color:red}",
    GREEN="${color:green}",
    GREEN_END="${/color:green}",
    BLUE="${color:blue}",
    BLUE_END="${/color:blue}",
)

import queue
import threading

# 전역 로그 큐 생성
log_queue = queue.Queue()

def printlog(message):
    """
    메시지를 큐에 추가하여 별도 스레드에서 로그를 처리.
    지원 태그:
    - ${bold}...${/bold}: 굵게 표시
    - ${color:red}...${/color}: 색상 적용
    - 중첩 지원
    :param message: 태그를 포함한 메시지
    """
    log_queue.put(message)  # 메시지를 큐에 추가

def process_log_queue():
    """
    큐에 있는 로그 메시지를 하나씩 꺼내 GUI에 추가.
    """
    while not log_queue.empty():
        message = log_queue.get()
        if log_text:  # 로그 출력 창이 있는 경우
            stack = []  # 태그 추적을 위한 스택
            start_idx = 0

            while start_idx < len(message):
                # 태그 시작 검색
                start_tag = message.find("${", start_idx)
                if start_tag == -1:
                    # 남은 일반 텍스트 추가
                    log_text.insert(tk.END, message[start_idx:] + "\n")
                    break

                # 태그 종료 검색
                end_tag = message.find("}", start_tag)
                if end_tag == -1:
                    raise ValueError("Malformed tag in message.")

                # 태그 내용 추출
                tag_content = message[start_tag + 2 : end_tag]

                # 태그 이전 일반 텍스트 추가
                log_text.insert(tk.END, message[start_idx:start_tag])

                if not tag_content.startswith("/"):
                    # 시작 태그 처리
                    stack.append((tag_content, log_text.index(tk.INSERT)))
                else:
                    # 종료 태그 처리
                    if not stack or stack[-1][0] != tag_content[1:]:
                        raise ValueError(f"Unmatched closing tag: {tag_content}")

                    # 태그 적용
                    tag_type, tag_start = stack.pop()
                    tag_end = log_text.index(tk.INSERT)

                    if tag_type == "bold":
                        log_text.tag_add("bold", tag_start, tag_end)
                    elif tag_type.startswith("color:"):
                        color = tag_type.split(":")[1]
                        log_text.tag_add(f"color_{color}", tag_start, tag_end)

                # 태그 이후로 이동
                start_idx = end_tag + 1

            # 스타일 설정
            log_text.tag_config("bold", font=("Arial", 10, "bold"))
            log_text.tag_config("color_red", foreground="red")
            log_text.tag_config("color_blue", foreground="blue")
            log_text.tag_config("color_green", foreground="green")
            log_text.tag_config("color_yellow", foreground="yellow")

            # 스크롤을 항상 아래로 유지
            log_text.see(tk.END)

    global global_root  # 전역 root 참조
    if global_root is None:
        raise ValueError("Root is not initialized.")
    # 100ms 주기로 큐를 확인
    global_root.after(100, process_log_queue)


# root.after 관리
def schedule_task(delay, callback, *args):
    """
    Tkinter root.after()를 전역 함수처럼 사용.
    :param delay: 딜레이 시간 (밀리초)
    :param callback: 실행할 콜백 함수
    :param args: 콜백 함수에 전달할 인자
    """
    global global_root  # 전역 root 참조
    if global_root is None:
        raise ValueError("Root is not initialized.")
    global_root.after(delay, callback, *args)


def show_srt_intro(root):
    """SRT 예매 프로세스를 위한 기본 레이아웃 설정"""
    global log_text  # 전역 변수 사용
    global global_root  # 전역 root 선언

    # root를 전역 변수로 설정
    global_root = root

    # 창 크기 재조정
    root.geometry("600x260")  # 화면 크기 축소 (높이 줄임)

    # 기존 화면 초기화
    for widget in root.winfo_children():
        widget.destroy()

    # Process title
    title_frame = tk.Frame(root)
    title_frame.pack(pady=10)
    tk.Label(title_frame, text="SRT 예약", font=("Arial", 18)).pack()

     # SYSTEM LOG 라벨
    tk.Label(root, text="SYSTEM LOG :", font=("Arial", 12, "bold")).pack(anchor="w", padx=10)


    # Log 영역 (스크롤바 포함)
    log_frame = tk.Frame(root, width=600, height=100, relief="groove", bd=1)
    log_frame.pack(pady=10)

    log_text = tk.Text(log_frame, wrap="word", font=("Arial", 10), height=6)  # 텍스트 라인수 설정
    log_text.pack(side=tk.LEFT, fill="both", expand=True)

    scrollbar = tk.Scrollbar(log_frame, command=log_text.yview)
    scrollbar.pack(side=tk.RIGHT, fill="y")
    log_text.config(yscrollcommand=scrollbar.set)

    # 로그 큐 처리 시작
    process_log_queue()

    def srt_macr_start():
        """SRT 매크로 실행"""
        try:
            # 버튼 비활성화
            action_button.config(state=tk.DISABLED)
            printlog("[INFO] SRT 매크로 실행을 시작합니다.\n")

            # 전체 프로세스 실행
            start_process(root)

        except Exception as e:
            # 예기치 못한 에러 처리
            printlog(f"{TAGS.RED}[ERROR] 프로세스 중 문제가 발생했습니다: {e}{TAGS.RED_END}")
            messagebox.showerror("오류 발생", "문제가 발생했습니다.")

        finally:
            # 버튼 활성화
            action_button.config(state=tk.NORMAL)

    action_button = tk.Button(root, text="시작", command=srt_macr_start)
    action_button.pack(pady=5)

    # 초기 로그 메시지
    initial_description = (
        f"{TAGS.BOLD}[WELCOME]{TAGS.BOLD_END}\n"
        f"- 예매를 위해 브라우저가 실행됩니다.\n"
        f"- 최초에 로그인 여부를 확인하며, 로그인이 완료되면 다음 단계로 넘어갈 수 있습니다.\n\n"
        f"진행을 원하시면 {TAGS.BLUE}{TAGS.BOLD}[시작]{TAGS.BOLD_END}{TAGS.BLUE_END} 버튼을 눌러주세요."
    )


    # 파싱 및 로그 업데이트
    printlog(initial_description)






step = 1

def start_process(root):
    """전체 프로세스를 감싸는 래핑 함수"""
    global step, driver  # 전역 변수 사용
    step = 1
    driver = None

    def next_step():
        """현재 STEP을 증가시키고 반환"""
        global step
        step += 1
        return step

    # 단계별 로그 추가 함수
    def process_steps(step_index=1):
        global driver  # 전역 변수 참조
        try:
            if step_index == 1:
                # STEP 1: 브라우저 객체 생성 및 초기화
                printlog(f"[STEP {step}] 브라우저 초기화 중...")
                driver = driver_entry("https://etk.srail.kr/main.do")
                if not driver:
                    printlog(f"{TAGS.RED}[STEP {step}:ERROR] 브라우저 초기화 실패. 프로세스를 종료합니다.{TAGS.RED_END}")
                    return
                printlog(f"[STEP {step}:SUCCESS] 브라우저 초기화 성공.\n")
                schedule_task(100, process_steps, step_index + 1)

            elif step_index == 2:
                # STEP 2: 로그인 상태 확인 및 모니터링
                next_step()
                printlog(f"[STEP {step}] 로그인 상태 확인 중...")
                login_page_url = "https://etk.srail.kr/cmc/01/selectLoginForm.do?pageId=TK0701000000"

                loginChk = monitor_login(driver, login_page_url, retryCnt=3, timeout=60)

                if not loginChk:  # 로그인 실패 시
                    printlog(f"{TAGS.RED}[STEP {step}:ERROR] 로그인 프로세스 실패. 브라우저를 종료합니다.{TAGS.RED_END}")
                    driver.quit()
                    return
                

                printlog(f"[STEP {step}:SUCCESS] 로그인 확인 성공.\n")
                schedule_task(100, process_steps, step_index + 1)

            elif step_index == 3:
                # STEP 3: 이후 작업 진행
                next_step()
                printlog(f"[STEP {step}] 자동 예매 대상 검색")
                reserveChk = create_search_window(step, process_steps, step_index, driver)
                if not reserveChk:  # 예매매 실패 시
                    printlog(f"{TAGS.RED}[STEP {step}:ERROR] 예매 대상 검색 실패. 브라우저를 종료합니다.{TAGS.RED_END}")
                    driver.quit()   
                    return

                schedule_task(100, process_steps, step_index + 1)

            elif step_index == 4:
                # STEP 완료 로그
                printlog(f"{TAGS.GREEN}[PROCESS COMPLETE] 모든 작업이 성공적으로 완료되었습니다.{TAGS.GREEN_END}\n")

        except Exception as e:
            printlog(f"{TAGS.RED}[ERROR] 예기치 못한 에러 발생: {e}{TAGS.RED_END}")
            driver.quit()

    # 실행 시작
    process_steps()


    

    

def driver_entry(main_page_url):
    """Selenium 브라우저 객체 생성 및 반환"""
    try:
        # ChromeDriver 설정
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        # 브라우저 객체 생성
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        # 지정된 URL로 이동
        driver.get(main_page_url)
        
        # 명시적 대기: 특정 요소가 로드될 때까지 기다림
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "wrap"))  # 메인 페이지의 특정 요소
        )

        return driver  # 브라우저 객체 반환

    except Exception as e:
        messagebox.showerror("오류 발생", f"브라우저 초기화 중 문제가 발생했습니다.\n{e}")
        return None



def is_logged_in(driver):
    """
    로그인 여부를 확인. 현재 DOM 상태를 기반으로 로그인 여부를 반환.
    :param driver: Selenium WebDriver 객체
    :return: True(로그인됨), False(로그인되지 않음 또는 확인 불가)
    """
    try:
        # 특정 클래스 조합을 만족하는 요소 확인
        login_wrap = driver.find_element(By.CSS_SELECTOR, "div.login_wrap.val_m.fl_r")
        links = login_wrap.find_elements(By.TAG_NAME, "a")

        for idx, link in enumerate(links):
            text_content = driver.execute_script("return arguments[0].innerText;", link).strip()
            href_content = link.get_attribute("href")

            # '로그인' 텍스트 또는 특정 href 포함 여부 확인
            if text_content == "로그아웃" or (href_content and "selectLogoutInfo" in href_content):
                return True  # 로그인되지 않은 상태

        return False  # '로그인' 링크가 없으면 로그인된 상태

    except NoSuchElementException:
        print("[DEBUG] login_wrap 요소를 찾지 못했습니다. 로그인 여부 확인 불가.")
        return False  # 확인 불가 시 로그인되지 않은 상태로 간주
    except Exception as e:
        print(f"[DEBUG] 예외 발생: {e}")
        raise  # 예외 발생 시 로그인되지 않은 상태로 간주




def monitor_login(driver, login_page_url, retryCnt=3, timeout = 60):
    """
    로그인 상태를 확인하고, 로그인 필요 시 로그인 페이지로 이동.
    로그인될 때까지 반복적으로 상태를 확인하며, 재시도를 수행.
    :param driver: Selenium WebDriver 객체
    :param login_page_url: 로그인 페이지 URL
    :param retryCnt: 최대 재시도 횟수
    :param timeout: 각 시도에 대한 타임아웃 (초)
    :return: True(로그인 성공), False(로그인 실패)
    """
    def wait_for_login(timeout):
        """
        timeout 동안 로그인 상태를 반복적으로 확인.
        :param timeout: 최대 대기 시간 (초)
        :return: True(로그인 성공), False(로그인되지 않음)
        """
        elapsed_time = 0
        check_interval = 0.1  # 100ms 간격으로 상태 확인

        while elapsed_time < timeout:
            try:
                if is_logged_in(driver):
                    return True  # 로그인 성공
            except Exception as e:
                printlog(f"{TAGS.RED}[ERROR] 상태 확인 중 예외 발생: {e}{TAGS.RED_END}")

            # GUI 업데이트 및 대기
            time.sleep(check_interval)
            global_root.update()
            elapsed_time += check_interval

        return False  # 타임아웃 초과

    # STEP 1: 최초 로그인 상태 확인
    try:
        printlog(" - 로그인 상태 확인 중...")
        
        if is_logged_in(driver):
            printlog(f"{TAGS.BLUE}로그인 확인 완료. 다음 단계로 진행합니다.{TAGS.BLUE_END}\n")
            return True  # 로그인 성공

        printlog(" - 로그인이 확인되지 않은 상태입니다. 로그인 페이지로 이동합니다.\n")
        driver.get(login_page_url)

        # STEP 2: 로그인 상태 재시도
        for attempt in range(retryCnt):
            printlog(f" - 로그인 확인 시도 {attempt + 1}/{retryCnt}... | {timeout}초 대기 중...")
            if wait_for_login(timeout):
                printlog(f"{TAGS.BLUE}로그인 확인 완료. 다음 단계로 진행합니다.{TAGS.BLUE_END}\n")
                return True  # 로그인 성공

            printlog(" - 로그인을 확인하지 못했습니다. 로그인 페이지로 이동합니다.\n")
            driver.get(login_page_url)

        return False  # 최대 재시도 초과
    except Exception as e:
        printlog(f"{TAGS.RED}[ERROR] 예기치 못한 에러 발생: {e}{TAGS.RED_END}")
        raise




from datetime import datetime
import tkinter as tk
from tkinter import messagebox

# 환승역만 존재하는 경우 체크
def check_search_result(driver):
    """
    환승역만 존재하는 경우를 확인하고, 메시지 박스로 알림.
    :param driver: Selenium WebDriver 객체
    """
    try:
        # alert_box 클래스의 div 요소 찾기
        alert_box = driver.find_element(By.CSS_SELECTOR, "div.alert_box strong")
        
        # strong 태그의 텍스트 가져오기
        alert_text = alert_box.text
        
        # 특정 텍스트가 포함되어 있는지 확인
        if "환승으로 조회" in alert_text:
            printlog(" 환승역만 가능한 경우입니다.")
            return 1


        elif "조회 결과가 없습니다" in alert_text:
            printlog(" 조회 결과가 없습니다.")
            return -1
            
        else:
            return 0

    except NoSuchElementException:
        print("alert_box 요소를 찾을 수 없습니다.")

def create_search_window(step, process_steps, step_index, driver):
    """
    새로운 창을 생성하고 창 닫힘까지 대기하며, 상태 값을 반환.
    """
    # 새로운 창 생성
    input_window = tk.Toplevel(global_root)
    input_window.title("SRT 조회 정보 입력")
    input_window.geometry("400x320")

    # 상태 값 초기화
    input_window.result = None  # 창 닫힘 상태 관리

    # 출발역과 도착역 목록 가져오기
    stations = fetch_station_options(driver)
    station_labels = [station["label"] for station in stations]

    # 출발역 선택
    tk.Label(input_window, text="출발역:", font=("Arial", 10)).pack(pady=5)
    departure_var = tk.StringVar(value=station_labels[0])  # 기본값 설정
    departure_select = ttk.Combobox(input_window, textvariable=departure_var, values=station_labels, state="readonly")
    departure_select.pack(pady=5)

    # 도착역 선택
    tk.Label(input_window, text="도착역:", font=("Arial", 10)).pack(pady=5)
    arrival_var = tk.StringVar(value=station_labels[0])  # 기본값 설정
    arrival_select = ttk.Combobox(input_window, textvariable=arrival_var, values=station_labels, state="readonly")
    arrival_select.pack(pady=5)

    # 날짜 입력 (기본값: 오늘 날짜)
    tk.Label(input_window, text="날짜 (YYYY.MM.DD):", font=("Arial", 10)).pack(pady=5)
    today_date = datetime.now().strftime("%Y.%m.%d")
    date_entry = tk.Entry(input_window, width=30)
    date_entry.insert(0, today_date)  # 기본값 설정
    date_entry.pack(pady=5)

   # 시간 옵션 가져오기
    time_options = fetch_time_options(driver)
    if not time_options:
        tk.messagebox.showerror("데이터 오류", "시간 옵션을 불러오지 못했습니다. 다시 시도해주세요.")
        input_window.destroy()
        return

    time_labels = [option["label"] for option in time_options]

    # 시간 선택
    tk.Label(input_window, text="시간 선택:", font=("Arial", 10)).pack(pady=5)
    selected_time = tk.StringVar(value=time_labels[0])  # 기본값 설정
    time_select = ttk.Combobox(input_window, textvariable=selected_time, values=time_labels, state="readonly")
    time_select.pack(pady=5)

    # 시간 무관 체크박스
    time_unchecked = tk.BooleanVar(value=False)  # 기본값: 체크 해제
    tk.Checkbutton(input_window, text="시간 무관", variable=time_unchecked).pack(pady=5)

    # 조회 버튼
    def search():
        departure = departure_var.get()
        arrival = arrival_var.get()
        date = date_entry.get()
        selected_time_label = time_select.get()
        time = next((option['value'] for option in time_options if option['label'] == selected_time_label), None)

        no_time = time_unchecked.get()

        # 입력값 검증
        if not departure or not arrival:
            tk.messagebox.showerror("입력 오류", "출발역과 도착역을 입력하세요.")
            return
        if not validate_date_format(date):
            tk.messagebox.showerror("입력 오류", "날짜 형식이 잘못되었습니다. YYYY.MM.DD 형식으로 입력하세요.")
            return
        if not time:
            tk.messagebox.showerror("입력 오류", "유효한 시간을 선택하세요.")
            return

        # 입력값 driver로 전달
        flag = perform_driver_search(driver, departure, arrival, date, time, no_time)

        if flag:
            # 검색 결과 검증 (환승역 조회, 조회결과 없는 상태)
            csr = check_search_result(driver)
            if csr == -1 :
                printlog(" 가능한 역이 존재하지 않습니다.")
                search_result_frame.pack_forget()
                input_window.geometry("400x320")
                return

            cto = False
            if csr == 1 :  # 환승역만 존재하는 경우
                printlog(" 환승역만 존재하는 경우입니다. 환승역으로 진행합니다.")
                cto = True  

            # 검색 조건 라벨 업데이트
            label_text = f"({date} {selected_time_label}) {departure} -> {arrival}"
            if cto:
                label_text += " (환승만 가능)"
            search_result_label.config(text=label_text)
            search_result_frame.pack()  # 검색에 성공하면 프레임을 표시
            input_window.geometry("400x360")
        else:
            # 검색 실패한 경우 프레임을 숨김
            search_result_frame.pack_forget()
            input_window.geometry("400x320")
        

            

    tk.Button(input_window, text="조회", command=search).pack(pady=10)

    separator = tk.Frame(input_window, height=2, bd=1, relief=tk.SUNKEN)
    separator.pack(fill=tk.X, pady=10)  

    search_result_frame = tk.Frame(input_window)
    search_result_frame.pack(pady=10)
    search_result_frame.pack_forget()  # 최초에는 보이지 않도록 설정

    def execute_search():
        # 실행 버튼 클릭 시 수행할 작업을 여기에 추가
        printlog("실행 버튼이 클릭되었습니다.")

    execute_button = tk.Button(search_result_frame, text="실행", command=execute_search)
    execute_button.pack(side=tk.RIGHT, padx=5)

    # 검색 조건 라벨
    search_result_label = tk.Label(search_result_frame, text="", font=("Arial", 10))
    search_result_label.pack(side=tk.LEFT, padx=5)

    # 창 닫힘 이벤트 처리
    def on_close():
        input_window.result = False  # 강제 종료 상태
        input_window.destroy()

    input_window.protocol("WM_DELETE_WINDOW", on_close)

    # 창 닫힘 대기
    global_root.wait_window(input_window)

    # 창 닫힌 후 상태 값 반환
    return input_window.result

def perform_driver_search(driver, departure, arrival, date, time, no_time):
    """
    Selenium을 사용하여 SRT 간편조회 영역에 입력값을 설정하고 조회 수행.
    :param driver: Selenium WebDriver 객체
    :param departure: 출발역 (예: '서울')
    :param arrival: 도착역 (예: '부산')
    :param date: 조회 날짜 (예: '2023.01.01')
    :param time: 조회 시간 (예: '12:00' 또는 None)
    :return: True(성공), False(실패)
    """

    # 옵션 전처리
    if no_time:
        time = "000000"  # 시간 무관인 경우

    try:
        # 1. SRT 메인 페이지로 이동
        driver.get("https://etk.srail.kr/main.do")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "wrap"))
        )

        # 2. 간편조회 영역 확인
        simple_search_form = driver.find_element(By.ID, "search-form")
        if not simple_search_form:
            printlog(f"{TAGS.RED}[ERROR] 간편조회 영역을 찾을 수 없습니다.{TAGS.RED_END}")
            return False

        
        
        # 3. 출발지 입력 | dptRsStnCd
        departure_select = Select(simple_search_form.find_element(By.ID, "dptRsStnCd"))
        departure_select.select_by_visible_text(departure)

        # 4. 도착지 입력 | arvRsStnCd
        arrival_select = Select(simple_search_form.find_element(By.ID, "arvRsStnCd"))
        arrival_select.select_by_visible_text(arrival)

        # 5. 날짜 입력
        '''
        date_input = simple_search_form.find_element(By.NAME, "dptDt")
        date_input.send_keys(date)
        '''
        calendar_button = simple_search_form.find_element(By.CSS_SELECTOR, "input.calendar2")
        calendar_button.click()

        formatted_date = date.replace(".", "")

        # 새 창이 열릴 때까지 기다림
        WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))

        # 새 창으로 전환
        original_window = driver.current_window_handle
        new_window = [window for window in driver.window_handles if window != original_window][0]
        driver.switch_to.window(new_window)

        # 새 창에서 selectDateInfo 함수를 실행
        driver.execute_script(f"selectDateInfo('{formatted_date}');")

        # 원래 창으로 돌아옴
        driver.switch_to.window(original_window)


        # 6. 시간 입력 | dptTm
        time_select = Select(simple_search_form.find_element(By.ID, "dptTm"))
        time_select.select_by_value(time)

        # 7. 조회 버튼 클릭
        search_button = simple_search_form.find_element(By.CSS_SELECTOR, "a.btn_midium.wp100.btn_burgundy_dark.corner.val_m")
        driver.execute_script("arguments[0].click();", search_button)

        printlog(f"[INFO] 조회 수행: 출발지={departure}, 도착지={arrival}, 날짜={date}, 시간={time or '시간 무관'}")
        return True

    except Exception as e:
        printlog(f"{TAGS.RED}[ERROR] 간편조회 수행 중 예외 발생: {e}{TAGS.RED_END}")
        return False

def fetch_station_options(driver):
    """
    Selenium WebDriver를 이용하여 출발역과 도착역 옵션을 파싱.
    :param driver: Selenium WebDriver 객체
    :return: [{"value": "역코드", "label": "역이름"}, ...]
    """
    try:
        # SRT 홈페이지에서 역 옵션 요소를 파싱
        driver.get("https://etk.srail.kr/main.do")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "dptRsStnCd"))
        )

        station_elements = driver.find_elements(By.CSS_SELECTOR, "select#dptRsStnCd option")
        stations = [
            {"value": el.get_attribute("value"), "label": el.text.strip()}
            for el in station_elements if el.get_attribute("value")
        ]
        return stations
    except Exception as e:
        printlog(f"{TAGS.RED}[ERROR] 역 옵션 파싱 실패: {e}{TAGS.RED_END}")
        return []

def fetch_time_options(driver):
    """
    SRT 페이지에서 시간 옵션을 파싱하여 반환.
    :param driver: Selenium WebDriver 객체
    :return: 시간 옵션 리스트 (예: [{'value': '000000', 'label': '00시 이후'}, ...])
    """
    try:
        driver.get("https://etk.srail.kr/main.do")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "search-form"))
        )

        # 시간 드롭다운에서 옵션 파싱
        time_dropdown = driver.find_element(By.ID, "dptTm")
        time_options = time_dropdown.find_elements(By.TAG_NAME, "option")

        # value와 label 모두 추출
        return [
            {"value": option.get_attribute("value"), "label": option.text.strip()}
            for option in time_options
            if option.get_attribute("value")
        ]
    except Exception as e:
        printlog(f"{TAGS.RED}[ERROR] 시간 옵션 파싱 중 예외 발생: {e}{TAGS.RED_END}")
        return []


def validate_date_format(date_str):
    """
    입력된 날짜가 YYYY.MM.DD 형식인지 검증.
    :param date_str: 입력된 날짜 문자열
    :return: True(유효한 형식), False(잘못된 형식)
    """
    try:
        datetime.strptime(date_str, "%Y.%m.%d")
        return True
    except ValueError:
        return False
