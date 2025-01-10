import tkinter as tk

# 기본 GUI 생성
def main():
    root = tk.Tk()
    root.title("SRT 예약 프로그램")
    root.geometry("400x300")  # 창 크기 설정

    tk.Label(root, text="SRT 예약 프로그램", font=("Arial", 18)).pack(pady=20)
    tk.Button(root, text="시작", command=lambda: print("프로그램 시작")).pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()
