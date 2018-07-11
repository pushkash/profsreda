from .models import Answer, Response, QuestionnaireResult, ResponseResult


def levels(level, level_grad=[1,0.75,0.65,0.55,0.45]):
    if level > level_grad[1]:
        return 'Очень высокий'
    if level > level_grad[2]:
        return 'Высокий'
    if level > level_grad[3]:
        return 'Средний'
    if level > level_grad[4]:
        return 'Низкий'
    else:
        return 'Ниже среднего'


def cos_result_processor(resp_pk):
    answers = Answer.objects.filter(response=resp_pk)
    communication = 0
    organisation = 0
    for answer in answers:
        k = answer.question.sort_id % 4
        if k == 1:
            if answer.body.choice == 'Да':
                communication+=1
        if k == 2:
            if answer.body.choice == 'Да':
                organisation+=1
        if k == 3:
            if answer.body.choice == 'Нет':
                communication+=1
        if k == 4:
            if answer.body.choice == 'Нет':
                organisation+=1

    c = communication / 20
    o = organisation / 20

    com_level = levels(c)
    org_level = levels(o, [1, 0.8, 0.7, 0.65, 0.55])

    return {
        'com_level': com_level,
        'com_score': int(c*100),
        'org_level': org_level,
        'org_score': int(o*100)
    }


def human_human_processor(resp_pk):
    answers = Answer.objects.filter(response=resp_pk)
    score = 0
    for answer in answers:
        score += int(answer.body.choice)

    return int(score * 100 / 30)


def categorical_processor(resp_pk):
    response = Response.objects.get(pk=resp_pk)
    variants = QuestionnaireResult.objects.filter(questionnaire=response.questionnaire)
    answers = Answer.objects.filter(response=resp_pk)
    categories = {}
    for v in variants:
        categories[v.category.name] = 0
    for a in answers:
        if a.body == True:
            categories[a.question.category.name] += 1

    for k in categories.keys():
        qr = variants.get(category__name=k)
        score = categories[k]
        rr = ResponseResult(qr=qr, response=response, score=score)
        rr.save()

    dominating = max(categories, key=categories.get)
    variant = variants.get(category__name=dominating)
    result = {
        'category': variant.category.name,
        'main_description': variant.main_description,
        'descr1': variant.description1,
        'descr2': variant.description2,
    }
    return result


def result_processor(q, resp):
    funcs = {
        1: cos_result_processor,
        2: categorical_processor,
    }
    return funcs[q](resp)
