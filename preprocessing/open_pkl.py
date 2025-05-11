import pickle
import json
import re

# Pickle 파일 읽기
with open('../datas/final_result.pkl', 'rb') as f:
    data = pickle.load(f)

# 데이터 정제 함수
def clean_text(text):
    # BOM 제거
    text = text.replace('\ufeff', '')
    # 불필요한 공백 제거
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# 데이터 정제
cleaned_data = {clean_text(k): clean_text(v) for k, v in data.items()}

# JSON 형식으로 저장
with open('../datas/final_result.json', 'w', encoding='utf-8') as f:
    json.dump(cleaned_data, f, ensure_ascii=False, indent=2)

print("데이터가 final_result.json 파일로 저장되었습니다.")
