import pygame
import sys
import random

# Pygameの初期化
pygame.init()

# 画面設定
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("AWS クイズゲーム")

# 色の定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 200)
GREEN = (0, 150, 0)
RED = (200, 0, 0)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)

# フォント設定（日本語対応）
try:
    # macOSの日本語フォントを試す
    font_large = pygame.font.Font("/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc", 48)
    font_medium = pygame.font.Font("/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc", 36)
    font_small = pygame.font.Font("/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc", 24)
except:
    try:
        # 別のmacOSフォントを試す
        font_large = pygame.font.Font("/System/Library/Fonts/Arial Unicode MS.ttf", 48)
        font_medium = pygame.font.Font("/System/Library/Fonts/Arial Unicode MS.ttf", 36)
        font_small = pygame.font.Font("/System/Library/Fonts/Arial Unicode MS.ttf", 24)
    except:
        try:
            # システムデフォルトフォントを使用
            font_large = pygame.font.SysFont("hiraginosans", 48)
            font_medium = pygame.font.SysFont("hiraginosans", 36)
            font_small = pygame.font.SysFont("hiraginosans", 24)
        except:
            # 最後の手段として、利用可能な日本語フォントを探す
            japanese_fonts = ["hiraginokakugothicpro", "hiraginosans", "notosanscjk", "arial"]
            font_large = None
            for font_name in japanese_fonts:
                try:
                    font_large = pygame.font.SysFont(font_name, 48)
                    font_medium = pygame.font.SysFont(font_name, 36)
                    font_small = pygame.font.SysFont(font_name, 24)
                    break
                except:
                    continue
            
            # それでもダメな場合はデフォルトフォント
            if font_large is None:
                font_large = pygame.font.Font(None, 48)
                font_medium = pygame.font.Font(None, 36)
                font_small = pygame.font.Font(None, 24)

# AWSクイズ問題データ
quiz_questions = [
    {
        "question": "Amazon EC2の正式名称は何ですか？",
        "options": [
            "Elastic Compute Cloud",
            "Elastic Container Cloud",
            "Enhanced Computing Cloud",
            "Extended Compute Cloud"
        ],
        "correct": 0
    },
    {
        "question": "Amazon S3で提供されるストレージクラスはどれですか？",
        "options": [
            "Standard",
            "Glacier",
            "Intelligent-Tiering",
            "すべて正しい"
        ],
        "correct": 3
    },
    {
        "question": "AWS Lambdaの特徴として正しいものはどれですか？",
        "options": [
            "サーバーレスコンピューティング",
            "イベント駆動型実行",
            "従量課金制",
            "すべて正しい"
        ],
        "correct": 3
    },
    {
        "question": "Amazon RDSでサポートされていないデータベースエンジンはどれですか？",
        "options": [
            "MySQL",
            "PostgreSQL",
            "MongoDB",
            "Oracle"
        ],
        "correct": 2
    },
    {
        "question": "AWS CloudFormationの主な用途は何ですか？",
        "options": [
            "インフラストラクチャのコード化",
            "アプリケーションのデプロイ",
            "リソースの自動化",
            "すべて正しい"
        ],
        "correct": 3
    },
    {
        "question": "Amazon VPCの略称の意味は何ですか？",
        "options": [
            "Virtual Private Cloud",
            "Virtual Public Cloud",
            "Virtual Protected Cloud",
            "Virtual Premium Cloud"
        ],
        "correct": 0
    },
    {
        "question": "AWS IAMで管理できるものはどれですか？",
        "options": [
            "ユーザー",
            "ロール",
            "ポリシー",
            "すべて正しい"
        ],
        "correct": 3
    },
    {
        "question": "Amazon CloudWatchの主な機能は何ですか？",
        "options": [
            "モニタリング",
            "ログ管理",
            "アラート設定",
            "すべて正しい"
        ],
        "correct": 3
    }
]

class AWSQuizGame:
    def __init__(self):
        self.current_question = 0
        self.score = 0
        self.questions = random.sample(quiz_questions, len(quiz_questions))
        self.game_state = "menu"  # menu, playing, result
        self.selected_option = -1
        self.show_answer = False
        self.answer_timer = 0
        
    def draw_menu(self):
        screen.fill(WHITE)
        
        # タイトル
        title_text = font_large.render("AWS クイズゲーム", True, BLUE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 150))
        screen.blit(title_text, title_rect)
        
        # 説明
        desc_text = font_medium.render("AWSの知識をテストしよう！", True, BLACK)
        desc_rect = desc_text.get_rect(center=(SCREEN_WIDTH//2, 250))
        screen.blit(desc_text, desc_rect)
        
        # スタートボタン
        start_button = pygame.Rect(SCREEN_WIDTH//2 - 100, 350, 200, 60)
        pygame.draw.rect(screen, BLUE, start_button)
        pygame.draw.rect(screen, BLACK, start_button, 3)
        
        start_text = font_medium.render("スタート", True, WHITE)
        start_text_rect = start_text.get_rect(center=start_button.center)
        screen.blit(start_text, start_text_rect)
        
        # 問題数表示
        count_text = font_small.render(f"問題数: {len(self.questions)}問", True, BLACK)
        count_rect = count_text.get_rect(center=(SCREEN_WIDTH//2, 450))
        screen.blit(count_text, count_rect)
        
        return start_button
    
    def draw_question(self):
        screen.fill(WHITE)
        
        if self.current_question >= len(self.questions):
            return
            
        question_data = self.questions[self.current_question]
        
        # 進捗表示
        progress_text = font_small.render(f"問題 {self.current_question + 1} / {len(self.questions)}", True, BLACK)
        screen.blit(progress_text, (20, 20))
        
        # スコア表示
        score_text = font_small.render(f"スコア: {self.score}", True, BLACK)
        score_rect = score_text.get_rect(topright=(SCREEN_WIDTH - 20, 20))
        screen.blit(score_text, score_rect)
        
        # 問題文
        question_lines = self.wrap_text(question_data["question"], font_medium, SCREEN_WIDTH - 100)
        y_offset = 100
        for line in question_lines:
            question_surface = font_medium.render(line, True, BLACK)
            question_rect = question_surface.get_rect(center=(SCREEN_WIDTH//2, y_offset))
            screen.blit(question_surface, question_rect)
            y_offset += 40
        
        # 選択肢
        option_buttons = []
        start_y = y_offset + 50
        
        for i, option in enumerate(question_data["options"]):
            button_rect = pygame.Rect(100, start_y + i * 80, SCREEN_WIDTH - 200, 60)
            
            # ボタンの色を決定
            if self.show_answer:
                if i == question_data["correct"]:
                    color = GREEN
                elif i == self.selected_option and i != question_data["correct"]:
                    color = RED
                else:
                    color = GRAY
            elif i == self.selected_option:
                color = ORANGE
            else:
                color = WHITE
            
            pygame.draw.rect(screen, color, button_rect)
            pygame.draw.rect(screen, BLACK, button_rect, 2)
            
            # 選択肢テキスト
            option_lines = self.wrap_text(f"{chr(65+i)}. {option}", font_small, SCREEN_WIDTH - 240)
            text_y = button_rect.centery - (len(option_lines) * 12)
            
            for line in option_lines:
                option_surface = font_small.render(line, True, BLACK)
                option_rect = option_surface.get_rect(center=(button_rect.centerx, text_y))
                screen.blit(option_surface, option_rect)
                text_y += 24
            
            option_buttons.append(button_rect)
        
        # 次の問題ボタン（答えを表示している時のみ）
        next_button = None
        if self.show_answer:
            next_button = pygame.Rect(SCREEN_WIDTH//2 - 100, start_y + len(question_data["options"]) * 80 + 20, 200, 50)
            pygame.draw.rect(screen, BLUE, next_button)
            pygame.draw.rect(screen, BLACK, next_button, 2)
            
            next_text = font_medium.render("次へ", True, WHITE)
            next_text_rect = next_text.get_rect(center=next_button.center)
            screen.blit(next_text, next_text_rect)
        
        return option_buttons, next_button
    
    def draw_result(self):
        screen.fill(WHITE)
        
        # 結果タイトル
        result_text = font_large.render("クイズ終了！", True, BLUE)
        result_rect = result_text.get_rect(center=(SCREEN_WIDTH//2, 150))
        screen.blit(result_text, result_rect)
        
        # スコア表示
        score_text = font_medium.render(f"最終スコア: {self.score} / {len(self.questions)}", True, BLACK)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, 250))
        screen.blit(score_text, score_rect)
        
        # 正答率
        percentage = (self.score / len(self.questions)) * 100
        percentage_text = font_medium.render(f"正答率: {percentage:.1f}%", True, BLACK)
        percentage_rect = percentage_text.get_rect(center=(SCREEN_WIDTH//2, 300))
        screen.blit(percentage_text, percentage_rect)
        
        # 評価
        if percentage >= 80:
            evaluation = "素晴らしい！AWSエキスパートですね！"
            eval_color = GREEN
        elif percentage >= 60:
            evaluation = "良い成績です！もう少し頑張りましょう。"
            eval_color = BLUE
        else:
            evaluation = "もっと勉強が必要ですね。頑張って！"
            eval_color = RED
        
        eval_text = font_small.render(evaluation, True, eval_color)
        eval_rect = eval_text.get_rect(center=(SCREEN_WIDTH//2, 380))
        screen.blit(eval_text, eval_rect)
        
        # リスタートボタン
        restart_button = pygame.Rect(SCREEN_WIDTH//2 - 100, 450, 200, 60)
        pygame.draw.rect(screen, GREEN, restart_button)
        pygame.draw.rect(screen, BLACK, restart_button, 3)
        
        restart_text = font_medium.render("もう一度", True, WHITE)
        restart_text_rect = restart_text.get_rect(center=restart_button.center)
        screen.blit(restart_text, restart_text_rect)
        
        # 終了ボタン
        quit_button = pygame.Rect(SCREEN_WIDTH//2 - 100, 530, 200, 60)
        pygame.draw.rect(screen, RED, quit_button)
        pygame.draw.rect(screen, BLACK, quit_button, 3)
        
        quit_text = font_medium.render("終了", True, WHITE)
        quit_text_rect = quit_text.get_rect(center=quit_button.center)
        screen.blit(quit_text, quit_text_rect)
        
        return restart_button, quit_button
    
    def wrap_text(self, text, font, max_width):
        """テキストを指定幅で折り返す"""
        words = text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " "
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        
        if current_line:
            lines.append(current_line.strip())
        
        return lines
    
    def restart_game(self):
        self.current_question = 0
        self.score = 0
        self.questions = random.sample(quiz_questions, len(quiz_questions))
        self.game_state = "menu"
        self.selected_option = -1
        self.show_answer = False
        self.answer_timer = 0

def main():
    clock = pygame.time.Clock()
    game = AWSQuizGame()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                if game.game_state == "menu":
                    start_button = game.draw_menu()
                    if start_button.collidepoint(mouse_pos):
                        game.game_state = "playing"
                
                elif game.game_state == "playing":
                    if not game.show_answer:
                        option_buttons, _ = game.draw_question()
                        for i, button in enumerate(option_buttons):
                            if button.collidepoint(mouse_pos):
                                game.selected_option = i
                                if i == game.questions[game.current_question]["correct"]:
                                    game.score += 1
                                game.show_answer = True
                                game.answer_timer = pygame.time.get_ticks()
                    else:
                        _, next_button = game.draw_question()
                        if next_button and next_button.collidepoint(mouse_pos):
                            game.current_question += 1
                            game.selected_option = -1
                            game.show_answer = False
                            
                            if game.current_question >= len(game.questions):
                                game.game_state = "result"
                
                elif game.game_state == "result":
                    restart_button, quit_button = game.draw_result()
                    if restart_button.collidepoint(mouse_pos):
                        game.restart_game()
                    elif quit_button.collidepoint(mouse_pos):
                        running = False
        
        # 画面描画
        if game.game_state == "menu":
            game.draw_menu()
        elif game.game_state == "playing":
            game.draw_question()
        elif game.game_state == "result":
            game.draw_result()
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
