import tkinter as tk
from srt_handler import show_srt_interface
from ktx_handler import show_ktx_interface
import webbrowser

def main():
    root = tk.Tk()
    root.title("Smart Rail 예매 프로그램")
    root.geometry("400x260")  # 창 크기 조정

    # 초기 화면 구성
    setup_main_screen(root)

    root.mainloop()

def setup_main_screen(root):
    """
    메인 화면 UI 구성
    """
    # 상단 제목 라벨
    tk.Label(root, text="기차 예약 프로그램", font=("Arial", 18)).pack(pady=20)

    # 설명 추가
    description_frame = tk.Frame(root)
    description_frame.pack(pady=5)
    tk.Label(description_frame, text="자동예약을 위한 시스템을 선택해주세요", font=("Arial", 9)).pack()
    tk.Label(description_frame, text="예매를 위해 브라우저상에서 로그인이 필요할 수 있습니다.", font=("Arial", 9)).pack()

    # 열차 선택 (Radio Button)
    train_type = tk.StringVar(value="SRT")  # SRT를 기본값으로 설정
    radio_frame = tk.Frame(root)
    radio_frame.pack(pady=10)
    tk.Radiobutton(radio_frame, text="SRT", variable=train_type, value="SRT").pack(side=tk.LEFT, padx=20)
    tk.Radiobutton(radio_frame, text="KTX", variable=train_type, value="KTX").pack(side=tk.LEFT, padx=20)

    # 시작 버튼
    def start_program():
        selected_train = train_type.get()
        if selected_train == "SRT":
            show_srt_interface(root)  # SRT 핸들러 호출
        elif selected_train == "KTX":
            show_ktx_interface(root)  # KTX 핸들러 호출
        else:
            tk.messagebox.showerror("오류", "올바른 열차를 선택하세요!")

    tk.Button(root, text="시작", command=start_program, width=10).pack(pady=2)

    # Footer (Developer : @d0il | Buy me a coffee)
    setup_footer(root)

def setup_footer(root):
    """
    Footer 구성
    """
    def open_github():
        webbrowser.open("https://github.com/D0iloppa")  # GitHub 프로필 링크

    def open_coffee_link():
        webbrowser.open("https://buymeacoffee.com/doil")  # 후원 링크

    footer_frame = tk.Frame(root)
    footer_frame.pack(side=tk.BOTTOM, pady=10)

    # Footer 구성
    tk.Label(footer_frame, text="Developer :", font=("Arial", 8)).pack(side=tk.LEFT)

    # GitHub 링크 (@d0il)
    link_label = tk.Label(footer_frame, text="@d0il", font=("Arial", 8), fg="blue", cursor="hand2")
    link_label.pack(side=tk.LEFT)
    link_label.bind("<Button-1>", lambda e: open_github())

    # 구분 심볼
    tk.Label(footer_frame, text=" | ", font=("Arial", 8)).pack(side=tk.LEFT)

    # Buy me a coffee (일반 텍스트처럼 표시)
    coffee_label = tk.Label(footer_frame, text="Buy me a coffee", font=("Arial", 8), fg="black", cursor="hand2")
    coffee_label.pack(side=tk.LEFT)
    coffee_label.bind("<Button-1>", lambda e: open_coffee_link())


if __name__ == "__main__":
    main()
