import json
import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_post_chat():
    response = client.post("/chat", json={"conversation_history": [], "user_query": "미성년자도 판매 회원 등록이 가능한가요?"})
    assert response.status_code == 200

    progress_stack = []
    for chunk in response.iter_lines():
        json_chunk = json.loads(chunk)

        status = json_chunk["status"]
        content = json_chunk["content"]
        if status == "progress":
            progress_stack.append(content)
        elif status == "done":
            completion = content["completion"]
        
    assert len(progress_stack) > 0
    assert len(completion["answer"]) > 0 and 2 >= len(completion["follow_up_questions"]) > 0
