import logging
import random
from flask import Flask, request, jsonify
from typing import Optional

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

sessionStorage = {}


@app.route("/", methods=["GET", "POST"])
def main() -> dict:
    if request.method == "GET":
        return "Server is running!", 200
    
    logging.info(f"Request: {request.json!r}")
    
    response = {
        "session": request.json["session"],
        "version": request.json["version"],
        "response": {
            "end_session": False,
            "text": ""
        }
    }
    handle_dialogue(response, request.json)
    logging.info(f"Response: %r", response)
    return jsonify(response)


def handle_dialogue(res: dict, req: dict) -> None:
    user_id = req["session"]["user_id"]
    
    if req["session"]["new"]:
        res["response"]["text"] = "Привет! Я могу переводить слова.\nПросто скажи: 'Переведи слово <слово>'"
        return
    
    text = req["request"]["original_utterance"].lower()
    
    if "переведи слово" in text or "переведите слово" in text:
        word = text.replace("переведи слово", "").replace("переведите слово", "").strip()
        
        if not word:
            res["response"]["text"] = "Вы не указали слово для перевода. Попробуйте так: 'Переведи слово стакан'"

        translation = translate_word(word)
        
        if translation:
            res["response"]["text"] = translation
        else:
            res["response"]["text"] = f"Не удалось перевести слово {word}"
    else:
        res["response"]["text"] = "Я могу переводить слова. Скажите: 'Переведи слово <слово>'"


def translate_word(word: str) -> Optional[str]:
    try:
        url = f"https://api.mymemory.translated.net/get?q={word}&langpair=ru|en"
        response = request.get(url)
        data = response.json()
        
        if response.status_code == 200 and data.get("responseData"):
            return data["responseData"]["translatedText"].lower()
        return None
    except Exception as e:
        logging.error(f"Ошибка перевода: {e}")
        return None


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
