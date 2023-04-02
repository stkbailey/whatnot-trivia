# %%
import datetime
import time
import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
import datetime

import pandas
import pathlib
from .models import Quiz, Answer

logger = logging.getLogger(__name__)


def start_driver(livestream_id: str):
    # Replace this with the path to your Chrome WebDriver executable
    chromedriver_path = "db/chromedriver"
    chrome_options = Options()
    # chrome_options.add_argument("--headless")

    # Replace this with the URL you want to scrape
    url = f"https://www.whatnot.com/live/{livestream_id}"

    # Initialize the Chrome WebDriver
    service = ChromeService(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Open the URL
    driver.get(url)
    return driver


def stop_driver(driver):
    driver.quit()


def fetch_quiz():
    bank_fname = pathlib.Path("db/question_bank.csv")
    if bank_fname.exists():
        bank_df = pandas.read_csv(bank_fname)
        s = bank_df.sample(1).iloc[0]
        quiz = Quiz(
            question=s.question,
            answer=s.answer,
        )
    else:
        quiz = Quiz(
            question="What is the answer to life, the universe, and everything?",
            answer="42",
        )
    return quiz


def load_chat(fname="db/chat.csv"):
    p = pathlib.Path(fname)
    if p.exists():
        df = pandas.read_csv(p)
    else:
        df = pandas.DataFrame(columns=["scraped_at", "username", "chat"])
    return df


def write_chat(df: pandas.DataFrame, fname="db/chat.csv"):
    df.to_csv(fname, index=False)


def load_quizzes(fname="db/quizzes.csv"):
    p = pathlib.Path(fname)
    if p.exists():
        df = pandas.read_csv(p)
    else:
        df = pandas.DataFrame(columns=Quiz.schema()["properties"].keys())
    return df


def write_quiz(quiz: Quiz, fname="db/quizzes.csv"):
    quizzes = load_quizzes(fname)
    tmp = pandas.DataFrame([quiz.dict()])
    quizzes = pandas.concat([quizzes, tmp], axis=0, ignore_index=True)
    quizzes.to_csv(fname, index=False)


def load_answers(fname="db/answers.csv"):
    p = pathlib.Path(fname)
    if p.exists():
        df = pandas.read_csv(p)
    else:
        df = pandas.DataFrame(columns=Answer.schema()["properties"].keys())
    return df


def write_answers(df: pandas.DataFrame, fname="db/answers.csv"):
    df.to_csv(fname, index=False)


def get_username(div_text: str):
    parts = div_text.split("\n")
    if len(parts[0]) == 2 and parts[0].upper() == parts[0]:
        return parts[1]
    return parts[0]


def get_chat_comment(div_text: str):
    parts = div_text.split("\n")
    if len(parts[0]) == 2 and parts[0].upper() == parts[0]:
        parts.pop(0)
    return " ".join(parts[1:])


def clear_db():
    for ii in ["answers", "chat", "quizzes"]:
        p = pathlib.Path(f"db/{ii}.csv")
        if p.exists():
            p.unlink()


def scrape_chat(driver, chat: pandas.DataFrame = None):
    if chat is None:
        chat = pandas.DataFrame(columns=["scraped_at", "username", "chat"])

    cursor = chat.shape[0]
    dt = datetime.datetime.now()
    chat_divs = driver.find_elements(
        by=By.XPATH,
        value="//div[@style='display: flex; width: 100%; align-items: flex-start; margin-bottom: 12px; border-radius: 4px;']",
    )

    for ii in range(len(chat_divs) - cursor):
        idx = cursor + ii
        div_text = chat_divs[idx].text

        record = {
            "scraped_at": dt,
            "username": get_username(div_text),
            "chat": get_chat_comment(div_text),
        }

        tmp = pandas.DataFrame([record])
        chat = pandas.concat([chat, tmp], axis=0, ignore_index=True)
    return chat
