import json
import streamlit
import datetime
import pandas

# from streamlit_autorefresh import st_autorefresh

from whatnot_trivia.models import Quiz, Answer
from whatnot_trivia.utils import *

POLL_SECONDS = 10

livestream_id = streamlit.text_input(
    "Enter livestream id",
    value="b38e75f5-1f91-49a2-887c-397f8f0f5da8",
    key="livestream_id",
)

if "driver" not in streamlit.session_state:
    driver = start_driver(livestream_id)
    streamlit.session_state["driver"] = driver
else:
    driver = streamlit.session_state["driver"]

if "chat" not in streamlit.session_state:
    chat = load_chat()
    streamlit.session_state["chat"] = chat
else:
    chat = streamlit.session_state["chat"]

pressed = streamlit.button("Get quiz")
quiz = fetch_quiz()


# Load for a quiz
answers = load_answers()
chat = scrape_chat(driver, chat)
quiz.started_at = datetime.datetime.now()

# Write the quiz
streamlit.text(f"Livestream ID {livestream_id}")
streamlit.text(f"Quiz ID {quiz.quiz_id}")
streamlit.text(quiz.question)
streamlit.text(f"Quiz started at {quiz.started_at}")

# poll for answers
for ii in range(POLL_SECONDS):
    # streamlit.markdown(f"Polling for answers: {ii}")
    chat = scrape_chat(driver, chat)
    time.sleep(1)
write_chat(chat)

# save
quiz.ended_at = datetime.datetime.now()
in_quiz_window = (pandas.to_datetime(chat.scraped_at) >= quiz.started_at) & (
    pandas.to_datetime(chat.scraped_at) <= quiz.ended_at
)
answers_list = []
for ii, s in chat.loc[in_quiz_window].iterrows():
    qa = Answer(
        quiz_id=quiz.quiz_id,
        username=s.username,
        created_at=s.scraped_at,
        value=s.chat,
        is_correct="the" in str(s.chat).lower(),
        # is_correct=s.chat.lower() == quiz.answer.lower(),
    )
    if s.username not in map(lambda x: x.username, answers_list):
        answers_list.append(qa)

tmp_answers = pandas.DataFrame([qa.dict() for qa in answers_list])
answers = pandas.concat([answers, tmp_answers], axis=0, ignore_index=True)
write_answers(answers)
write_quiz(quiz)

streamlit.markdown("## Answers during chat")
streamlit.dataframe(tmp_answers)

# Show results
winners = answers.loc[
    (answers.quiz_id == quiz.quiz_id) & (answers.is_correct)
].username.tolist()
score_totals = (
    answers.groupby(["username"])
    .agg({"quiz_id": "count", "is_correct": "sum"})
    .reset_index()
)
streamlit.markdown("## Summary")
streamlit.text(f"Users with answers: {in_quiz_window.sum()}")
streamlit.text(f"Users with correct answers: {winners}")
streamlit.dataframe(score_totals)
