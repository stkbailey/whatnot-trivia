import os
import openai
import random
import logging

from .models import TrivaQuestion

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

openai.api_key = os.getenv("OPENAI_API_KEY")

CATEGORIES = [
    "pokemon",
    "pokemon cards",
    "nintendo",
    "mens fashion",
    "womens fashion",
    "return pallets",
    "coral",
    "baseball cards",
    "sports cards",
    "ecommerce",
    "magic: the gathering",
    "marvel comics",
    "dc comics",
    "independent comics",
    "geography",
    "data analysis",
    "botany",
    "nerds",
    "ancient religions",
    "art forms",
    "greek mythology",
    "norse mythology",
    "marine biology",
    "dentistry",
    "potatoes",
    "pokemon red",
]


class WhatBot(object):
    def __init__(self, model: str = "gpt-3.5-turbo"):
        self.model = model

    def generate_answer_set(self, raw_string: str) -> dict:
        options = raw_string.split("\n")
        correct_answer = options[0]
        random.shuffle(options)

        alpha_vals = "ABCDEFGHIJK"
        correct_index = options.index(correct_answer)

        choices = [f"{alpha_vals[ii]}. {options[ii]}" for ii in range(len(options))]

        return dict(
            raw_string=raw_string,
            options=choices,
            correct_answer=correct_answer,
            correct_answer_alpha=alpha_vals[correct_index],
        )

    def parse_answers_string(self, s: str) -> list[str]:
        return s.split("\n")

    def pick_category(self) -> str:
        return random.choice(CATEGORIES)

    def generate_trivia_question(self, category: str = None) -> TrivaQuestion:
        if not category:
            category = self.pick_category()

        question = self._make_question(category)
        logger.debug(f"Generated question: {question}")

        answers = self._make_answers(question)
        logger.debug(f"Generated answers: {answers['options']}")

        return TrivaQuestion(
            category=category,
            question=question,
            options=answers["options"],
            correct_answer=answers["correct_answer"],
            correct_answer_alpha=answers["correct_answer_alpha"],
        )

    def _make_question(self, category: str) -> str:
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are running a game show. Provide only the question with no supporting text.",
                },
                {
                    "role": "user",
                    "content": f"Generate a challenging trivia question in the category of {category}",
                },
            ],
        )
        question = response["choices"][0]["message"]["content"]
        return question

    def _make_answers(self, question: str) -> dict:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are running a game show. Provide only the answers with no supporting text.",
                },
                {
                    "role": "user",
                    "content": f"""
                    Provide four answers to this question: {question}.
                    Put them in a list with one answer on each line. The first answer should be the correect answer.
                    The last answer should be a silly answer. Do not provide any additional text besides the answers.
                """,
                },
            ],
        )
        answer_raw = response["choices"][0]["message"]["content"]

        return self.generate_answer_set(answer_raw)
