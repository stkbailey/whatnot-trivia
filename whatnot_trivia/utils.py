# %%
import datetime
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
import datetime

import pandas
import pathlib
from .models import Quiz, Answer


def start_driver(livestream_id: str):
    # Replace this with the path to your Chrome WebDriver executable
    chromedriver_path = "assets/chromedriver"
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
    bank_fname = pathlib.Path("assets/question_bank.csv")
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


def load_chat(fname="assets/chat.csv"):
    p = pathlib.Path(fname)
    if p.exists():
        df = pandas.read_csv(p)
    else:
        df = pandas.DataFrame(columns=["scraped_at", "username", "chat"])
    return df


def write_chat(df: pandas.DataFrame, fname="assets/chat.csv"):
    df.to_csv(fname, index=False)


def load_quizzes(fname="assets/quizzes.csv"):
    p = pathlib.Path(fname)
    if p.exists():
        df = pandas.read_csv(p)
    else:
        df = pandas.DataFrame(columns=Quiz.schema()["properties"].keys())
    return df


def write_quiz(quiz: Quiz, fname="assets/quizzes.csv"):
    quizzes = load_quizzes(fname)
    tmp = pandas.DataFrame([quiz.dict()])
    quizzes = pandas.concat([quizzes, tmp], axis=0, ignore_index=True)
    quizzes.to_csv(fname, index=False)


def load_answers(fname="assets/answers.csv"):
    p = pathlib.Path(fname)
    if p.exists():
        df = pandas.read_csv(p)
    else:
        df = pandas.DataFrame(columns=Answer.schema()["properties"].keys())
    return df


def write_answers(df: pandas.DataFrame, fname="assets/answers.csv"):
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


def clear_assets():
    for ii in ["answers", "chat", "quizzes"]:
        p = pathlib.Path(f"assets/{ii}.csv")
        if p.exists():
            p.unlink()


def scrape_chat(driver, chat: pandas.DataFrame):
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


# #%%
# # Find the "div" element with the specified inline style attributes
# target_div = driver.find_elements(by=By.XPATH, value="//div[@style='display: flex; width: 100%; align-items: flex-start; margin-bottom: 12px; border-radius: 4px;']")

# # Print the text content of the target "div" element
# print(f"Count elements {len(target_div)}")

# print("Last Target div content:")
# print(target_div[-1].text)


# #%%

# # Wait 5 seconds for the content to load
# time.sleep(5)

# # Get the entire body of the page
# driver.
# body_content = driver.find_element_by_tag_name("body").get_attribute("innerHTML")

# # Save the content to a local file
# with open("output.html", "w", encoding="utf-8") as f:
#     f.write(body_content)

# #%%
# # Close the browser
# driver.quit()

# print("The content has been saved to output.html")


# # def fetch_soup(livestream_id):
# #     url =
# #     response = requests.get(url)
# #     return BeautifulSoup(response.text, "html.parser")


# # if __name__ == "__main__":
# #     from selenium import webdriver
# #     from selenium.webdriver.common.keys import Keys
# #     from selenium.webdriver.common.by import By

# #     driver = webdriver.Firefox()
# #     driver.get("http://www.python.org")
# #     assert "Python" in driver.title
# #     elem = driver.find_element(By.NAME, "q")
# #     elem.clear()
# #     elem.send_keys("pycon")
# #     elem.send_keys(Keys.RETURN)
# #     assert "No results found." not in driver.page_source
# #     driver.close()
