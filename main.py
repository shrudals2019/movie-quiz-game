class Quiz:
    def __init__(self, question, choices, answer):
        self.question = question
        self.choices = choices
        self.answer = answer

    def display(self):
        print(self.question)
        for i, choice in enumerate(self.choices, start=1):
            print(f"{i}. {choice}")

    def check_answer(self, user_answer):
        return user_answer == self.answer


def create_default_quizzes():
    return [
        Quiz(
            "영화 '기생충'의 감독은 누구일까요?",
            ["박찬욱", "봉준호", "이창동", "최동훈"],
            2
        ),
        Quiz(
            "영화 '타이타닉'의 감독은 누구일까요?",
            ["제임스 카메론", "스티븐 스필버그", "크리스토퍼 놀란", "리들리 스콧"],
            1
        ),
        Quiz(
            "영화 '어벤져스: 엔드게임'에서 타노스가 사용하는 물건은?",
            ["묠니르", "인피니티 건틀렛", "캡틴의 방패", "아크 리액터"],
            2
        ),
        Quiz(
            "영화 '인터스텔라'의 감독은 누구일까요?",
            ["제임스 건", "크리스토퍼 놀란", "조던 필", "팀 버튼"],
            2
        ),
        Quiz(
            "영화 '겨울왕국'에서 엘사의 동생 이름은?",
            ["안나", "모아나", "라푼젤", "메리다"],
            1
        )
    ]