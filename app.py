"""
This app uses Streamlit to run a simple trivia game.

The first run through will:
- initialize a webdriver on a livestream
- load previous answers for a csv file

"""

import os
import streamlit
import datetime
import pandas

from streamlit_autorefresh import st_autorefresh

from whatbot.models import Answer
from whatbot.utils import *
from whatbot.bot import WhatBot


# Run the autorefresh about every N milliseconds (2 seconds) and stop
# after it's been refreshed 100 times.
count = st_autorefresh(interval=50000, limit=30, key="restart", )

POLL_SECONDS = 15
WAIT_SECONDS = 15
LIVESTREAM_ID = os.environ["LIVESTREAM_ID"]

if "driver" not in streamlit.session_state:
    driver = start_driver(LIVESTREAM_ID)
    streamlit.session_state["driver"] = driver
    streamlit.session_state["url"] = driver.command_executor._url       #"http://127.0.0.1:60622/hub"
    streamlit.session_state["session_id"] = driver.session_id           #'4e167f26-dc1d-4f51-a207-f761eaf73c31'
else:
    driver = streamlit.session_state["driver"]

# round_name = streamlit.text_input(
#     "Enter Game Round Identifier",
#     value=uuid.uuid4().hex,
#     key="round_name",
# )

# DEBUG_TEXT = f"""
# ## Debug Logs

# Question: {question.question}

# Answers:
# {options_str}

# Correct answer is {question.correct_answer_alpha}. {question.correct_answer}
# """
# streamlit.markdown(DEBUG_TEXT)


# initialize the chat logs
answers = load_answers()
chat = scrape_chat(driver)

# select category
category_name = streamlit.text_input(
    "Enter category",
    value=None,
    key="category_name",
)

# Create a container to hold the question
container = streamlit.empty()

# Load a Question
t = WhatBot()
question = t.generate_trivia_question(category_name)
options_str= '\n- ' + '\n- '.join(question.options)

# Print the quiz
question.started_at = datetime.datetime.now()
QUESTION_TEXT = f"""# Question

**category:** {question.category}

**{question.question}**

{options_str}

*Chat in only with the letter of the correct answer.*
"""
container.markdown(QUESTION_TEXT)

# poll for answers
for ii in range(POLL_SECONDS):
    # streamlit.markdown(f"Polling for answers: {ii}")
    chat = scrape_chat(driver, chat)
    time.sleep(1)

question.ended_at = datetime.datetime.now()

# save
after_start = pandas.to_datetime(chat.scraped_at) >= question.started_at
before_end = pandas.to_datetime(chat.scraped_at) <= question.ended_at
in_quiz_window = after_start & before_end

answers_list = []
for ii, s in chat.loc[in_quiz_window].iterrows():
    qa = Answer(
        quiz_id=question.id,
        username=s.username,
        created_at=s.scraped_at,
        value=s.chat,
        is_correct=question.correct_answer_alpha.lower() == str(s.chat).lower(),
    )
    if s.username not in map(lambda x: x.username, answers_list):
        answers_list.append(qa)

tmp_answers = pandas.DataFrame([qa.dict() for qa in answers_list])
answers = pandas.concat([answers, tmp_answers], axis=0, ignore_index=True)
write_answers(answers)
write_quiz(question)


# Show results
winners = answers.loc[
    (answers.quiz_id == question.id) & (answers.is_correct)
].username.tolist()
score_totals = (
    answers.groupby(["username"])
    .agg({"quiz_id": "count", "is_correct": "sum"})
    .reset_index()
)
score_totals["attempts"] = score_totals["quiz_id"]
score_totals["score"] = score_totals["is_correct"]
score_totals["rank"] = score_totals.score.rank(method="first", ascending=False)


ANSWER_TEXT = f"""# Answer

{question.correct_answer_alpha}. {question.correct_answer}

## Chat Scoreboard

- Users with answers: {in_quiz_window.sum()}
- Users with correct answers: {winners}

{answers.loc[answers.quiz_id == question.id, ['username', 'value', 'is_correct']].to_markdown(index=False)}
"""
container.markdown(ANSWER_TEXT)


time.sleep(WAIT_SECONDS)
RANKING_TEXT = f"""## Running Totals

{score_totals[["username", "attempts", "score", "rank"]].sort_values(by="rank", ascending=True).to_markdown(index=False)}
"""
container.markdown(RANKING_TEXT)