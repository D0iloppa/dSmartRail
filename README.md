# 가상환경 생성
python -m venv dSmartRail


# 활성화
source dSmartRail/Scripts/activate

# 비활성화
deactivate

----------------------------
# 설치된 라이브러리 확인
pip freeze

# 의존성 관리 txt 생성
pip freeze > requirements.txt

# 의존성 파일 설치
pip install -r requirements.txt

