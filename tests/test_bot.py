from whatbot.bot import WhatBot, CATEGORIES, TrivaQuestion


def test_categories():
    # given
    wb = WhatBot()

    # when

    # then
    assert wb.pick_category() in CATEGORIES


def test_trivia_question():
    # given
    wb = WhatBot()

    # when
    # todo: mock the openai api
    question = wb.generate_trivia_question()

    # then
    assert isinstance(question, TrivaQuestion)
    assert question.category in CATEGORIES
    assert question.question
    assert question.options
    assert question.correct_answer
    assert question.correct_answer_alpha
