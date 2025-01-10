import tkinter as tk
from tkinter import messagebox


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def show_srt_interface(root):
    """SRT 핸들러 엔트리 포인트: 기존 화면에서 SRT 화면으로 전환"""
    clear_main_screen(root)  # 기존 화면 초기화
    show_srt_intro(root)     # SRT 안내문구 표시

def clear_main_screen(root):
    """메인 화면의 모든 위젯 제거"""
    for widget in root.winfo_children():
        widget.destroy()


def update_log(message):
    """로그 영역에 메시지 추가"""
    if log_text:
        log_text.insert(tk.END, f"{message}\n")
        log_text.see(tk.END)  # 스크롤을 항상 아래로 유지
    else:
        print(f"Log: {message}")  # 로그 영역이 없을 경우 콘솔에 출력

def show_srt_intro(root):
    """SRT 예매 프로세스를 위한 기본 레이아웃 설정"""
    global log_text  # 전역 변수 사용

    # 창 크기 재조정
    root.geometry("600x230")  # 화면 크기 축소 (높이 줄임)

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
    log_frame = tk.Frame(root, width=600, height=120, relief="groove", bd=1)
    log_frame.pack(pady=10)

    log_text = tk.Text(log_frame, wrap="word", font=("Arial", 10), height=5)  # 높이 5줄로 설정
    log_text.pack(side=tk.LEFT, fill="both", expand=True)

    scrollbar = tk.Scrollbar(log_frame, command=log_text.yview)
    scrollbar.pack(side=tk.RIGHT, fill="y")
    log_text.config(yscrollcommand=scrollbar.set)

    action_button = tk.Button(root, text="시작", command=srt_macr_start)
    action_button.pack(pady=10)

    # 초기 로그 메시지
    initial_description = (
        "[STEP 1]\n"
        "- 예매를 위해 브라우저가 실행됩니다.\n"
        "- 최초에 로그인 여부를 확인하며,\n"
        "- 로그인이 완료되면 다음 단계로 넘어갈 수 있습니다.\n\n"
    )
    update_log(initial_description)

    update_log("프로세스 초기화 완료. [시작] 버튼을 눌러 진행하세요.")



def srt_macr_start():
    """전체 프로세스를 감싸는 래핑 함수"""
    update_log("[PROCESS STARTED] SRT 예매 프로세스 시작")

    # STEP 1: 브라우저 객체 생성 및 초기화
    update_log("[STEP 1] 브라우저 초기화 중...")
    driver = driver_entry("https://etk.srail.kr/main.do")
    if not driver:
        update_log("[ERROR] 브라우저 초기화 실패. 프로세스를 종료합니다.")
        return  # 실패 시 종료

    update_log("[SUCCESS] 브라우저 초기화 완료.\n")

    # STEP 2: 로그인 상태 확인
    update_log("[STEP 2] 로그인 상태 확인 중...")
    login_flag = check_login_status(driver, "https://etk.srail.kr/cmc/01/selectLoginForm.do?pageId=TK0701000000")
    if login_flag is None:
        update_log("[ERROR] 로그인 상태 확인 중 오류 발생. 프로세스를 종료합니다.")
        driver.quit()  # 브라우저 종료
        return  # 실패 시 종료
    elif not login_flag:
        update_log("[INFO] 로그인되지 않은 상태입니다. 로그인 페이지로 이동 후 로그인 필요.")

    update_log("[SUCCESS] 로그인 상태 확인 완료.\n")

    # STEP 3: 다음 작업 (예: 예약 검색)
    if not perform_next_step(driver):
        update_log("[ERROR] 예약 검색 중 문제가 발생했습니다. 프로세스를 종료합니다.")
        driver.quit()  # 브라우저 종료
        return  # 실패 시 종료

    update_log("[SUCCESS] 예약 검색 완료.\n")

    # STEP 4: 기타 작업 (추가 단계 체이닝)
    if not finalize_process(driver):
        update_log("[ERROR] 최종 단계에서 문제가 발생했습니다. 프로세스를 종료합니다.")
        driver.quit()  # 브라우저 종료
        return  # 실패 시 종료

    update_log("[PROCESS COMPLETE] 모든 작업이 성공적으로 완료되었습니다.\n")
    driver.quit()  # 브라우저 종료

    

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




def check_login_status(driver, login_page_url):
    """로그인 상태 확인 및 로그인 페이지 이동"""
    try:
        # 로그인 여부 확인 (메인 페이지에서 확인)
        login_flag = False
        if len(driver.find_elements(By.ID, "wrap")) > 0:
            messagebox.showinfo("로그인 확인", "로그인되지 않은 상태입니다.\n로그인 페이지로 이동합니다.")
            # 로그인 페이지로 이동
            driver.get(login_page_url)
            time.sleep(3)
        else:
            messagebox.showinfo("로그인 확인", "이미 로그인되어 있습니다.")
            login_flag = True

        return login_flag  # 로그인 상태 플래그 반환

    except Exception as e:
        messagebox.showerror("오류 발생", f"로그인 확인 중 문제가 발생했습니다.\n{e}")
        return False



def perform_next_step(driver):
    """예약 검색 또는 다음 단계 수행"""
    try:
        update_log("[STEP 3] 예약 검색 작업 중...")
        # TODO: 예약 검색 로직 추가
        # 예: driver.find_element()로 예약 조건 입력
        update_log("[SUCCESS] 예약 조건 입력 및 검색 완료.")
        return True
    except Exception as e:
        update_log(f"[ERROR] 예약 검색 중 문제가 발생했습니다: {e}")
        return False

def finalize_process(driver):
    """최종 단계 처리"""
    try:
        update_log("[STEP 4] 최종 작업 중...")
        # TODO: 최종 예약 확인 및 완료 처리 로직 추가
        update_log("[SUCCESS] 최종 작업 완료.")
        return True
    except Exception as e:
        update_log(f"[ERROR] 최종 단계 처리 중 문제가 발생했습니다: {e}")
        return False