def full_score(questions):
    full_score = 0
    for question in questions:
        if question.is_scored():
            if question.is_bonus:
                if question.score():
                    full_score += question.weight()
            else:
                full_score += question.weight()

    return full_score


def total_score(questions):
    total = 0
    for question in questions:
        if question.is_scored():
            if question.is_bonus:
                if question.score():
                    total += question.score()
            else:
                total += question.score()

    return total
