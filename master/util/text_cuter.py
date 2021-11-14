import jieba


def lcut(string: str):
    return [i for i in jieba.lcut(string)]