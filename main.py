"""콘솔에서 실행하는 영화 퀴즈 게임."""

import json
import os
import shutil
import tempfile
from pathlib import Path

STATE_FILE = Path(__file__).resolve().parent / "state.json"
BACKUP_FILE = STATE_FILE.with_suffix(".json.bak")


class Quiz:
    """퀴즈 한 문제와 정답 판정을 표현합니다."""

    def __init__(self, question, choices, answer):
        self.question = question
        self.choices = choices
        self.answer = answer

    def display(self):
        print(self.question)
        print()
        for index, choice in enumerate(self.choices, start=1):
            print(f"{index}. {choice}")

    def check_answer(self, user_answer):
        return user_answer == self.answer

    def to_dict(self):
        return {"question": self.question, "choices": self.choices, "answer": self.answer}

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            raise ValueError("퀴즈 데이터는 객체여야 합니다.")
        question = data.get("question")
        choices = data.get("choices")
        answer = data.get("answer")
        if not isinstance(question, str) or not question.strip():
            raise ValueError("question 값이 올바르지 않습니다.")
        if not isinstance(choices, list) or len(choices) != 4:
            raise ValueError("choices는 4개의 선택지여야 합니다.")
        if not all(isinstance(choice, str) and choice.strip() for choice in choices):
            raise ValueError("선택지 값이 올바르지 않습니다.")
        if type(answer) is not int or answer not in range(1, 5):
            raise ValueError("answer는 1~4 사이의 정수여야 합니다.")
        return cls(question.strip(), [choice.strip() for choice in choices], answer)


def create_default_quizzes():
    return [
        Quiz("영화 '기생충'의 감독은 누구일까요?", ["박찬욱", "이창동", "봉준호", "최동훈"], 3),
        Quiz("영화 '친절한 금자씨'에서 금자가 복수하려는 인물은 누구일까요?", ["최 반장", "백 선생", "장 선생", "박 사장"], 2),
        Quiz("영화 '트루먼 쇼'에서 트루먼이 살고 있는 마을의 이름은 무엇일까요?", ["리버데일", "힐밸리", "스프링필드", "씨헤이븐"], 4),
        Quiz("영화 '시네마 천국'에서 어린 토토에게 영화를 가르쳐주는 영사기사의 이름은 무엇일까요?", ["마르코", "살바토레", "알프레도", "로베르토"], 3),
        Quiz("영화 '겨울왕국'에서 엘사의 동생 이름은 무엇일까요?", ["라푼젤", "안나", "모아나", "메리다"], 2),
        Quiz("영화 '장화, 홍련'의 주요 사건이 벌어지는 장소는 어디일까요?", ["학교 기숙사", "병원", "호텔", "한적한 시골의 집"], 4),
        Quiz("영화 '늑대소년'에서 박보영이 연기한 인물의 이름은 무엇일까요?", ["순이", "수진", "지영", "은희"], 1),
    ]


class QuizGame:
    """메뉴 흐름, 게임 상태, 입력과 저장을 관리합니다."""

    def __init__(self):
        self.quizzes = []
        self.best_score = None
        self.best_correct = 0
        self.best_total = 0
        self.load_state()

    def show_menu(self):
        print("\n========================================")
        print("        🎬 나만의 영화 퀴즈 🎬")
        print("========================================")
        print("1. 퀴즈 풀기")
        print("2. 퀴즈 추가")
        print("3. 퀴즈 목록")
        print("4. 점수 확인")
        print("5. 종료")
        print("========================================")

    def get_number_input(self, message, min_value, max_value):
        while True:
            value = input(message).strip()
            if not value:
                print(f"⚠️ 빈 입력입니다. {min_value}-{max_value} 사이의 숫자를 입력하세요. 다시 입력해 주세요.")
                continue
            try:
                number = int(value)
            except ValueError:
                print(f"⚠️ 숫자만 입력할 수 있습니다. {min_value}-{max_value} 사이로 다시 입력해 주세요.")
                continue
            if not min_value <= number <= max_value:
                print(f"⚠️ 범위를 벗어났습니다. {min_value}-{max_value} 사이로 다시 입력해 주세요.")
                continue
            return number

    def get_non_empty_text(self, message):
        while True:
            value = input(message).strip()
            if value:
                return value
            print("⚠️ 빈 입력은 사용할 수 없습니다. 다시 입력해 주세요.")

    def play_quiz(self):
        if not self.quizzes:
            print("⚠️ 등록된 퀴즈가 없습니다.")
            return
        correct_count = 0
        total = len(self.quizzes)
        print(f"\n📝 퀴즈를 시작합니다! (총 {total}문제)")
        for index, quiz in enumerate(self.quizzes, start=1):
            print("\n----------------------------------------")
            print(f"[문제 {index}]")
            quiz.display()
            answer = self.get_number_input("\n정답 입력 (1-4): ", 1, 4)
            if quiz.check_answer(answer):
                correct_count += 1
                print("✅ 정답입니다!")
            else:
                print(f"❌ 오답입니다. 정답은 {quiz.answer}번입니다.")
        score = int(correct_count / total * 100)
        print("\n========================================")
        print(f"🏆 결과: {total}문제 중 {correct_count}문제 정답! ({score}점)")
        if self.best_score is None or score > self.best_score:
            self.best_score, self.best_correct, self.best_total = score, correct_count, total
            print("🎉 새로운 최고 점수입니다!")
        print("========================================")
        self.save_state()

    def add_quiz(self):
        print("\n📌 새로운 퀴즈를 추가합니다.\n")
        question = self.get_non_empty_text("문제를 입력하세요: ")
        choices = [self.get_non_empty_text(f"선택지 {index}: ") for index in range(1, 5)]
        answer = self.get_number_input("정답 번호 (1-4): ", 1, 4)
        self.quizzes.append(Quiz(question, choices, answer))
        if self.save_state():
            print("\n✅ 퀴즈가 추가되었습니다.")
        else:
            self.quizzes.pop()
            print("\n⚠️ 저장에 실패해 퀴즈를 추가하지 않았습니다.")

    def list_quizzes(self):
        if not self.quizzes:
            print("⚠️ 등록된 퀴즈가 없습니다.")
            return
        print(f"\n📋 등록된 퀴즈 목록 (총 {len(self.quizzes)}개)")
        print("----------------------------------------")
        for index, quiz in enumerate(self.quizzes, start=1):
            print(f"[{index}] {quiz.question}")
        print("----------------------------------------")

    def show_score(self):
        if self.best_score is None:
            print("\n🏆 아직 퀴즈를 풀지 않았습니다.")
            return
        print(f"\n🏆 최고 점수: {self.best_score}점 ({self.best_total}문제 중 {self.best_correct}문제 정답)")

    def _state_data(self):
        return {
            "quizzes": [quiz.to_dict() for quiz in self.quizzes],
            "best_score": self.best_score,
            "best_correct": self.best_correct,
            "best_total": self.best_total,
        }

    def save_state(self):
        """임시 파일을 완성한 뒤 교체하고, 직전 정상 파일을 .bak에 보관합니다."""
        temporary_path = None
        try:
            STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=STATE_FILE.parent,
                                             delete=False, suffix=".tmp") as file:
                temporary_path = Path(file.name)
                json.dump(self._state_data(), file, ensure_ascii=False, indent=4)
                file.flush()
                os.fsync(file.fileno())
            if STATE_FILE.exists():
                shutil.copy2(STATE_FILE, BACKUP_FILE)
            os.replace(temporary_path, STATE_FILE)
            return True
        except OSError as error:
            print(f"⚠️ 데이터를 저장하지 못했습니다: {error}")
            return False
        finally:
            if temporary_path and temporary_path.exists():
                try:
                    temporary_path.unlink()
                except OSError:
                    pass

    @staticmethod
    def _read_state(path):
        with path.open("r", encoding="utf-8-sig") as file:
            data = json.load(file)
        if not isinstance(data, dict):
            raise ValueError("저장 데이터는 JSON 객체여야 합니다.")
        quiz_data = data.get("quizzes", [])
        if not isinstance(quiz_data, list):
            raise ValueError("quizzes 형식이 올바르지 않습니다.")
        quizzes = [Quiz.from_dict(item) for item in quiz_data]
        best_score = data.get("best_score")
        best_correct = data.get("best_correct", 0)
        best_total = data.get("best_total", 0)
        if best_score is not None and (type(best_score) is not int or not 0 <= best_score <= 100):
            raise ValueError("best_score 형식이 올바르지 않습니다.")
        if type(best_correct) is not int or best_correct < 0:
            raise ValueError("best_correct 형식이 올바르지 않습니다.")
        if type(best_total) is not int or best_total < 0 or best_correct > best_total:
            raise ValueError("best_total 형식이 올바르지 않습니다.")
        return quizzes or create_default_quizzes(), best_score, best_correct, best_total

    def _apply_state(self, state):
        self.quizzes, self.best_score, self.best_correct, self.best_total = state

    def load_state(self):
        if not STATE_FILE.exists():
            self._apply_state((create_default_quizzes(), None, 0, 0))
            print("📂 데이터 파일이 없어 기본 퀴즈를 사용합니다.")
            self.save_state()
            return
        try:
            self._apply_state(self._read_state(STATE_FILE))
            score_text = "기록 없음" if self.best_score is None else f"{self.best_score}점"
            print(f"📂 저장된 데이터를 불러왔습니다. (퀴즈 {len(self.quizzes)}개, 최고점수 {score_text})")
            return
        except (json.JSONDecodeError, OSError, KeyError, TypeError, ValueError) as error:
            print(f"⚠️ state.json을 읽을 수 없습니다: {error}")
            try:
                damaged_copy = STATE_FILE.with_suffix(".json.corrupt")
                shutil.copy2(STATE_FILE, damaged_copy)
                print(f"📦 손상된 원본은 {damaged_copy.name}으로 보관했습니다.")
            except OSError as backup_error:
                print(f"⚠️ 손상된 원본을 별도 보관하지 못했습니다: {backup_error}")
        try:
            self._apply_state(self._read_state(BACKUP_FILE))
            print("✅ state.json.bak 백업에서 데이터를 복구했습니다.")
            self.save_state()
            return
        except (json.JSONDecodeError, OSError, KeyError, TypeError, ValueError):
            print("⚠️ 사용 가능한 백업이 없어 기본 데이터로 시작합니다.")
        self._apply_state((create_default_quizzes(), None, 0, 0))
        self.save_state()

    def run(self):
        try:
            while True:
                self.show_menu()
                choice = self.get_number_input("선택: ", 1, 5)
                if choice == 1:
                    self.play_quiz()
                elif choice == 2:
                    self.add_quiz()
                elif choice == 3:
                    self.list_quizzes()
                elif choice == 4:
                    self.show_score()
                else:
                    self.save_state()
                    print("프로그램을 종료합니다.")
                    break
        except (KeyboardInterrupt, EOFError):
            print("\n⚠️ 입력이 중단되었습니다. 현재 게임 데이터를 저장하고 종료합니다.")
            self.save_state()


if __name__ == "__main__":
    QuizGame().run()
