import json
import os


STATE_FILE = "state.json"


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

    def to_dict(self):
        return {
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer
        }


def create_default_quizzes():
    return [
        Quiz(
            "영화 '기생충'의 감독은 누구일까요?",
            ["박찬욱", "봉준호", "이창동", "최동훈"],
            2
        ),
        Quiz(
            "영화 '친절한 금자씨'에서 금자가 복수하려는 인물은 누구일까요?",
            ["백 선생", "최 반장", "장 선생", "박 사장"],
            1
        ),
        Quiz(
            "영화 '트루먼 쇼'에서 트루먼이 살고 있는 마을의 이름은 무엇일까요?",
            ["씨헤이븐", "리버데일", "힐밸리", "스프링필드"],
            1
        ),
        Quiz(
            "영화 '시네마 천국'에서 어린 토토에게 영화를 가르쳐주는 영사기사의 이름은 무엇일까요?",
            ["알프레도", "마르코", "살바토레", "로베르토"],
            1
        ),
        Quiz(
            "영화 '겨울왕국'에서 엘사의 동생 이름은?",
            ["안나", "모아나", "라푼젤", "메리다"],
            1
        ),
        Quiz(
            "영화 '장화, 홍련'의 주요 사건이 벌어지는 장소는 어디일까요?",
            ["한적한 시골의 집", "학교 기숙사", "병원", "호텔"],
            1
        )
    ]


class QuizGame:
    def __init__(self):
        self.quizzes = []
        self.best_score = None
        self.best_correct = 0
        self.best_total = 0
        self.load_state()

    def show_menu(self):
        print("\n========================================")
        print("           🎬 나만의 영화 퀴즈")
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
                    print("⚠️ 빈 입력은 사용할 수 없습니다.")
                    continue

                number = int(value)

                if number < min_value or number > max_value:
                    print(f"⚠️ {min_value}~{max_value} 사이의 숫자를 입력하세요.")
                    continue

                return number

            except ValueError:
                print("⚠️ 숫자를 입력하세요.")

    def play_quiz(self):
        if not self.quizzes:
            print("⚠️ 등록된 퀴즈가 없습니다.")
            return

        score = 0
        total = len(self.quizzes)

        print(f"\n📝 퀴즈를 시작합니다! 총 {total}문제")

        for index, quiz in enumerate(self.quizzes, start=1):
            print("\n----------------------------------------")
            print(f"[문제 {index}]")
            quiz.display()

            answer = self.get_number_input("정답 입력 (1-4): ", 1, 4)

            if quiz.check_answer(answer):
                print("✅ 정답입니다!")
                score += 1
            else:
                print(f"❌ 오답입니다. 정답은 {quiz.answer}번입니다.")

        percentage = int(score / total * 100)

        print("\n========================================")
        print(f"🏆 결과: {total}문제 중 {score}문제 정답! ({percentage}점)")
        print("========================================")

        if self.best_score is None or percentage > self.best_score:
            self.best_score = percentage
            self.best_correct = score
            self.best_total = total
            print("🎉 새로운 최고 점수입니다!")

        self.save_state()

    def add_quiz(self):
        print("\n📌 새로운 퀴즈를 추가합니다.")

        while True:
            question = input("문제를 입력하세요: ").strip()

            if question:
                break

            print("⚠️ 문제를 입력해야 합니다.")

        choices = []

        for i in range(1, 5):
            while True:
                choice = input(f"선택지 {i}: ").strip()

                if choice:
                    choices.append(choice)
                    break

                print("⚠️ 선택지를 입력해야 합니다.")

        answer = self.get_number_input("정답 번호 (1-4): ", 1, 4)

        self.quizzes.append(
            Quiz(question, choices, answer)
        )

        self.save_state()
        print("✅ 퀴즈가 추가되었습니다!")

    def list_quizzes(self):
        if not self.quizzes:
            print("⚠️ 등록된 퀴즈가 없습니다.")
            return

        print(f"\n📋 등록된 퀴즈 목록 (총 {len(self.quizzes)}개)")
        print("----------------------------------------")

        for i, quiz in enumerate(self.quizzes, start=1):
            print(f"[{i}] {quiz.question}")

        print("----------------------------------------")

    def show_score(self):
        if self.best_score is None:
            print("\n아직 퀴즈를 풀지 않았습니다.")
            return

        print(
            f"\n🏆 최고 점수: {self.best_score}점 "
            f"({self.best_total}문제 중 "
            f"{self.best_correct}문제 정답)"
        )

    def save_state(self):
        data = {
            "quizzes": [
                quiz.to_dict()
                for quiz in self.quizzes
            ],
            "best_score": self.best_score,
            "best_correct": self.best_correct,
            "best_total": self.best_total
        }

        try:
            with open(
                STATE_FILE,
                "w",
                encoding="utf-8"
            ) as file:
                json.dump(
                    data,
                    file,
                    ensure_ascii=False,
                    indent=4
                )

        except OSError:
            print("⚠️ 데이터를 저장하는 중 오류가 발생했습니다.")

    def load_state(self):
        if (
            not os.path.exists(STATE_FILE)
            or os.path.getsize(STATE_FILE) == 0
        ):
            self.quizzes = create_default_quizzes()
            self.save_state()
            print("📂 기본 퀴즈 데이터를 불러왔습니다.")
            return

        try:
            with open(
                STATE_FILE,
                "r",
                encoding="utf-8-sig"
            ) as file:
                data = json.load(file)

            self.quizzes = [
                Quiz(
                    item["question"],
                    item["choices"],
                    item["answer"]
                )
                for item in data.get("quizzes", [])
            ]

            if not self.quizzes:
                self.quizzes = create_default_quizzes()

            self.best_score = data.get("best_score")
            self.best_correct = data.get(
                "best_correct",
                0
            )
            self.best_total = data.get(
                "best_total",
                0
            )

            score_text = (
                "기록 없음"
                if self.best_score is None
                else f"{self.best_score}점"
            )

            print(
                f"📂 저장된 데이터를 불러왔습니다. "
                f"(퀴즈 {len(self.quizzes)}개, "
                f"최고점수 {score_text})"
            )

        except (
            json.JSONDecodeError,
            OSError,
            KeyError,
            TypeError
        ):
            print(
                "⚠️ state.json이 손상되어 "
                "기본 데이터로 복구합니다."
            )

            self.quizzes = create_default_quizzes()
            self.best_score = None
            self.best_correct = 0
            self.best_total = 0
            self.save_state()

    def run(self):
        try:
            while True:
                self.show_menu()
                choice = input("선택: ").strip()

                if choice == "":
                    print(
                        "⚠️ 빈 입력입니다. "
                        "1~5 사이의 숫자를 입력하세요."
                    )

                elif choice == "1":
                    self.play_quiz()

                elif choice == "2":
                    self.add_quiz()

                elif choice == "3":
                    self.list_quizzes()

                elif choice == "4":
                    self.show_score()

                elif choice == "5":
                    self.save_state()
                    print("프로그램을 종료합니다.")
                    break

                else:
                    print(
                        "⚠️ 잘못된 입력입니다. "
                        "1~5 사이의 숫자를 입력하세요."
                    )

        except (KeyboardInterrupt, EOFError):
            print("\n⚠️ 입력이 중단되었습니다.")
            print("데이터를 저장하고 안전하게 종료합니다.")
            self.save_state()


if __name__ == "__main__":
    game = QuizGame()
    game.run()