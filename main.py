import json
import random
from datetime import datetime
from pathlib import Path

STATE_FILE = Path(__file__).resolve().parent / "state.json"


class Quiz:
    """영화 퀴즈 한 문제를 나타냅니다."""

    def __init__(self, question, choices, answer, hint=""):
        self.question = question
        self.choices = choices
        self.answer = answer
        self.hint = hint

    def display(self):
        print(self.question)
        for index, choice in enumerate(self.choices, start=1):
            print(f"{index}. {choice}")

    def check_answer(self, user_answer):
        return user_answer == self.answer

    def to_dict(self):
        return {
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer,
            "hint": self.hint,
        }

    @classmethod
    def from_dict(cls, data):
        question = data["question"]
        choices = data["choices"]
        answer = data["answer"]
        default_hints = {quiz.question: quiz.hint for quiz in create_default_quizzes()}
        hint = data.get("hint", default_hints.get(question, ""))
        if not isinstance(question, str) or not question.strip():
            raise ValueError("question 값이 올바르지 않습니다.")
        if not isinstance(choices, list) or len(choices) != 4:
            raise ValueError("choices는 4개의 선택지여야 합니다.")
        if not all(isinstance(choice, str) and choice.strip() for choice in choices):
            raise ValueError("선택지 값이 올바르지 않습니다.")
        if type(answer) is not int or answer not in range(1, 5):
            raise ValueError("answer는 1~4 사이의 정수여야 합니다.")
        if not isinstance(hint, str):
            raise ValueError("hint는 문자열이어야 합니다.")
        return cls(question.strip(), [choice.strip() for choice in choices], answer, hint.strip())


def create_default_quizzes():
    return [
        Quiz("영화 '기생충'의 감독은 누구일까요?", ["박찬욱", "이창동", "봉준호", "최동훈"], 3, "아카데미 작품상을 받은 감독입니다."),
        Quiz("영화 '친절한 금자씨'에서 금자가 복수하려는 인물은 누구일까요?", ["최 반장", "백 선생", "장 선생", "박 사장"], 2, "이영애가 연기한 금자와 관련된 인물입니다."),
        Quiz("영화 '트루먼 쇼'에서 트루먼이 살고 있는 마을의 이름은 무엇일까요?", ["리버데일", "힐밸리", "스프링필드", "씨헤이븐"], 4, "영어로 바다를 뜻하는 단어가 이름에 들어갑니다."),
        Quiz("영화 '시네마 천국'에서 어린 토토에게 영화를 가르쳐주는 영사기사의 이름은 무엇일까요?", ["마르코", "살바토레", "알프레도", "로베르토"], 3, "토토에게 영화와 삶의 지혜를 전해주는 인물입니다."),
        Quiz("영화 '겨울왕국'에서 엘사의 동생 이름은 무엇일까요?", ["라푼젤", "안나", "모아나", "메리다"], 2, "빨간 머리의 아렌델 공주입니다."),
        Quiz("영화 '장화, 홍련'의 주요 사건이 벌어지는 장소는 어디일까요?", ["학교 기숙사", "병원", "호텔", "한적한 시골의 집"], 4, "두 자매가 아버지와 새어머니와 함께 지내는 곳입니다."),
        Quiz("영화 '늑대소년'에서 박보영이 연기한 인물의 이름은 무엇일까요?", ["순이", "수진", "지영", "은희"], 1, "송중기가 연기한 소년과 처음 만나는 소녀입니다."),
    ]


class QuizGame:
    HINT_PENALTY = 10

    def __init__(self):
        self.quizzes = []
        self.best_score = None
        self.best_correct = 0
        self.best_total = 0
        self.history = []
        self.load_state()

    def show_menu(self):
        print("\n========================================")
        print("        🎬 나만의 영화 퀴즈 🎬")
        print("========================================")
        print("1. 퀴즈 풀기")
        print("2. 퀴즈 추가")
        print("3. 퀴즈 목록")
        print("4. 최고 점수 확인")
        print("5. 퀴즈 삭제")
        print("6. 점수 기록 보기")
        print("7. 종료")
        print("========================================")

    def get_number_input(self, message, min_value, max_value):
        while True:
            value = input(message).strip()
            if not value:
                print(f"⚠️ 빈 입력입니다. {min_value}-{max_value} 사이의 숫자를 입력하세요.")
                continue
            try:
                number = int(value)
            except ValueError:
                print(f"⚠️ 숫자로 입력해 주세요. ({min_value}-{max_value})")
                continue
            if not min_value <= number <= max_value:
                print(f"⚠️ {min_value}-{max_value} 사이의 숫자를 입력하세요.")
                continue
            return number

    @staticmethod
    def get_non_empty_text(message):
        while True:
            value = input(message).strip()
            if value:
                return value
            print("⚠️ 빈 입력은 사용할 수 없습니다.")

    def play_quiz(self):
        if not self.quizzes:
            print("⚠️ 등록된 퀴즈가 없습니다.")
            return

        print(f"\n등록된 퀴즈는 {len(self.quizzes)}개입니다.")
        question_count = self.get_number_input("몇 문제를 풀까요?: ", 1, len(self.quizzes))
        selected_quizzes = random.sample(self.quizzes, question_count)
        correct_count = 0
        hints_used = 0

        print(f"\n📝 문제 순서를 섞어 {question_count}문제를 출제합니다.")
        for index, quiz in enumerate(selected_quizzes, start=1):
            print("\n----------------------------------------")
            print(f"[문제 {index}/{question_count}]")
            quiz.display()
            if quiz.hint:
                use_hint = self.get_number_input(
                    f"힌트를 볼까요? (예: 1 / 아니오: 0, 사용 시 {self.HINT_PENALTY}점 차감): ", 0, 1
                )
                if use_hint:
                    hints_used += 1
                    print(f"💡 힌트: {quiz.hint}")
            answer = self.get_number_input("정답 입력 (1-4): ", 1, 4)
            if quiz.check_answer(answer):
                correct_count += 1
                print("✅ 정답입니다!")
            else:
                print(f"❌ 오답입니다. 정답은 {quiz.answer}번입니다.")

        raw_score = int(correct_count / question_count * 100)
        score = max(0, raw_score - hints_used * self.HINT_PENALTY)
        record = {
            "played_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "question_count": question_count,
            "correct_count": correct_count,
            "hints_used": hints_used,
            "score": score,
        }
        self.history.append(record)
        print("\n========================================")
        print(f"🏆 결과: {question_count}문제 중 {correct_count}문제 정답")
        print(f"기본 점수 {raw_score}점 - 힌트 {hints_used}회 차감 = 최종 {score}점")
        if self.best_score is None or score > self.best_score:
            self.best_score = score
            self.best_correct = correct_count
            self.best_total = question_count
            print("🎉 새로운 최고 점수입니다!")
        print("========================================")
        self.save_state()

    def add_quiz(self):
        print("\n📌 새로운 퀴즈를 추가합니다.\n")
        question = self.get_non_empty_text("문제를 입력하세요: ")
        choices = [self.get_non_empty_text(f"선택지 {index}: ") for index in range(1, 5)]
        answer = self.get_number_input("정답 번호 (1-4): ", 1, 4)
        hint = input("힌트 (없으면 Enter): ").strip()
        self.quizzes.append(Quiz(question, choices, answer, hint))
        self.save_state()
        print("✅ 퀴즈가 추가되었습니다.")

    def list_quizzes(self):
        if not self.quizzes:
            print("⚠️ 등록된 퀴즈가 없습니다.")
            return
        print(f"\n📋 등록된 퀴즈 목록 (총 {len(self.quizzes)}개)")
        for index, quiz in enumerate(self.quizzes, start=1):
            print(f"[{index}] {quiz.question}")

    def show_score(self):
        if self.best_score is None:
            print("\n🏆 아직 퀴즈 기록이 없습니다.")
            return
        print(f"\n🏆 최고 점수: {self.best_score}점 ({self.best_total}문제 중 {self.best_correct}문제 정답)")

    def delete_quiz(self):
        if not self.quizzes:
            print("⚠️ 삭제할 퀴즈가 없습니다.")
            return
        self.list_quizzes()
        if len(self.quizzes) == 1:
            print("⚠️ 퀴즈는 최소 1개 이상 유지해야 합니다.")
            return
        index = self.get_number_input(f"삭제할 퀴즈 번호 (1-{len(self.quizzes)}): ", 1, len(self.quizzes))
        removed = self.quizzes.pop(index - 1)
        self.save_state()
        print(f"✅ 퀴즈를 삭제하고 state.json에 저장했습니다: {removed.question}")

    def show_history(self):
        if not self.history:
            print("\n아직 점수 기록이 없습니다.")
            return
        print(f"\n📚 점수 기록 (총 {len(self.history)}회)")
        for index, record in enumerate(reversed(self.history), start=1):
            print(
                f"[{index}] {record['played_at']} | "
                f"{record['correct_count']}/{record['question_count']} 정답 | "
                f"힌트 {record.get('hints_used', 0)}회 | {record['score']}점"
            )

    def save_state(self):
        data = {
            "quizzes": [quiz.to_dict() for quiz in self.quizzes],
            "best_score": self.best_score,
            "best_correct": self.best_correct,
            "best_total": self.best_total,
            "history": self.history,
        }
        try:
            with STATE_FILE.open("w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
        except OSError as error:
            print(f"⚠️ 데이터를 저장하지 못했습니다: {error}")

    def load_state(self):
        if not STATE_FILE.exists():
            self.quizzes = create_default_quizzes()
            self.save_state()
            print("📂 데이터 파일이 없어 기본 퀴즈를 사용합니다.")
            return
        try:
            with STATE_FILE.open("r", encoding="utf-8-sig") as file:
                data = json.load(file)
            if not isinstance(data, dict):
                raise ValueError("저장 데이터 형식이 올바르지 않습니다.")
            quiz_data = data.get("quizzes", [])
            if not isinstance(quiz_data, list):
                raise ValueError("quizzes 형식이 올바르지 않습니다.")
            self.quizzes = [Quiz.from_dict(item) for item in quiz_data]
            if not self.quizzes:
                self.quizzes = create_default_quizzes()
            self.best_score = data.get("best_score")
            self.best_correct = int(data.get("best_correct", 0))
            self.best_total = int(data.get("best_total", 0))
            history = data.get("history", [])
            if not isinstance(history, list):
                raise ValueError("history 형식이 올바르지 않습니다.")
            self.history = history
            print(f"📂 저장된 데이터를 불러왔습니다. (퀴즈 {len(self.quizzes)}개)")
        except (json.JSONDecodeError, OSError, KeyError, TypeError, ValueError) as error:
            print(f"⚠️ state.json을 읽을 수 없어 기본 데이터로 시작합니다: {error}")
            self.quizzes = create_default_quizzes()
            self.best_score = None
            self.best_correct = 0
            self.best_total = 0
            self.history = []
            self.save_state()

    def run(self):
        try:
            while True:
                self.show_menu()
                choice = self.get_number_input("선택: ", 1, 7)
                if choice == 1:
                    self.play_quiz()
                elif choice == 2:
                    self.add_quiz()
                elif choice == 3:
                    self.list_quizzes()
                elif choice == 4:
                    self.show_score()
                elif choice == 5:
                    self.delete_quiz()
                elif choice == 6:
                    self.show_history()
                else:
                    self.save_state()
                    print("프로그램을 종료합니다.")
                    break
        except (KeyboardInterrupt, EOFError):
            print("\n⚠️ 입력이 중단되었습니다. 데이터를 저장하고 종료합니다.")
            self.save_state()


if __name__ == "__main__":
    QuizGame().run()
