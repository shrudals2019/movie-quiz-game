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


class QuizGame:
    def __init__(self):
        self.quizzes = create_default_quizzes()
        self.best_score = None

    def show_menu(self):
        print("\n========================================")
        print("           나만의 영화 퀴즈")
        print("========================================")
        print("1. 퀴즈 풀기")
        print("2. 퀴즈 추가")
        print("3. 퀴즈 목록")
        print("4. 점수 확인")
        print("5. 종료")
        print("========================================")

    def get_number_input(self, message, min_value, max_value):
        while True:
            try:
                value = input(message).strip()

                if value == "":
                    print("빈 입력은 사용할 수 없습니다.")
                    continue

                number = int(value)

                if number < min_value or number > max_value:
                    print(f"{min_value}~{max_value} 사이의 숫자를 입력하세요.")
                    continue

                return number

            except ValueError:
                print("숫자를 입력하세요.")

    def play_quiz(self):
        if not self.quizzes:
            print("등록된 퀴즈가 없습니다.")
            return

        score = 0

        print(f"\n퀴즈를 시작합니다! 총 {len(self.quizzes)}문제")

        for index, quiz in enumerate(self.quizzes, start=1):
            print("\n----------------------------------------")
            print(f"[문제 {index}]")
            quiz.display()

            answer = self.get_number_input("정답 입력 (1-4): ", 1, 4)

            if quiz.check_answer(answer):
                print("정답입니다!")
                score += 1
            else:
                print(f"오답입니다. 정답은 {quiz.answer}번입니다.")

        percentage = int(score / len(self.quizzes) * 100)

        print("\n========================================")
        print(f"결과: {len(self.quizzes)}문제 중 {score}문제 정답! ({percentage}점)")
        print("========================================")

        if self.best_score is None or percentage > self.best_score:
            self.best_score = percentage
            print("새로운 최고 점수입니다!")

    def run(self):
        while True:
            try:
                self.show_menu()
                choice = input("선택: ").strip()

                if choice == "":
                    print("빈 입력은 사용할 수 없습니다.")

                elif choice == "1":
                    self.play_quiz()

                elif choice == "2":
                    print("퀴즈 추가 기능을 준비 중입니다.")

                elif choice == "3":
                    print("퀴즈 목록 기능을 준비 중입니다.")

                elif choice == "4":
                    print("점수 확인 기능을 준비 중입니다.")

                elif choice == "5":
                    print("프로그램을 종료합니다.")
                    break

                else:
                    print("잘못된 입력입니다. 1~5 사이의 숫자를 입력하세요.")

            except (KeyboardInterrupt, EOFError):
                print("\n입력이 중단되었습니다. 프로그램을 안전하게 종료합니다.")
                break


if __name__ == "__main__":
    game = QuizGame()
    game.run()