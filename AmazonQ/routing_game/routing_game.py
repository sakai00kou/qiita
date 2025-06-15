import pygame
import sys
import json
import random
from typing import Dict, List, Tuple, Optional

# 初期化
pygame.init()

# 画面設定
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("ネットワークルーティングゲーム")

# 色定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 200)
LIGHT_BLUE = (173, 216, 230)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (220, 220, 220)
YELLOW = (255, 255, 0)

# フォント設定（日本語対応）
try:
    font_large = pygame.font.Font("/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc", 22)
    font_medium = pygame.font.Font("/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc", 16)
    font_small = pygame.font.Font("/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc", 12)
    font_bold = pygame.font.Font("/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc", 12)  # 太文字フォント
except:
    # フォントが見つからない場合のフォールバック
    font_large = pygame.font.Font(None, 22)
    font_medium = pygame.font.Font(None, 16)
    font_small = pygame.font.Font(None, 12)
    font_bold = pygame.font.Font(None, 12)  # 太文字フォント（フォールバック）

class NetworkNode:
    def __init__(self, name: str, ip: str, x: int, y: int):
        self.name = name
        self.ip = ip
        self.x = x
        self.y = y
        self.routing_table = []
        self.connections = []
        self.selected = False
        self.interfaces = []  # インターフェース情報を追加
        
    def add_interface(self, interface: str, ip: str, netmask: str):
        """インターフェース情報を追加"""
        self.interfaces.append({
            'interface': interface,
            'ip': ip,
            'netmask': netmask
        })
        
    def add_route(self, destination: str, gateway: str, interface: str):
        self.routing_table.append({
            'destination': destination,
            'gateway': gateway,
            'interface': interface
        })
    
    def draw(self, surface):
        # ノードアイコンのサイズを計算（インターフェース数に応じて高さを調整）
        interface_count = len(self.interfaces) if self.interfaces else 1
        width = 120
        height = max(60, 30 + interface_count * 12)
        
        # 長方形のノードアイコンを描画
        rect = pygame.Rect(self.x - width//2, self.y - height//2, width, height)
        color = YELLOW if self.selected else LIGHT_BLUE
        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, BLACK, rect, 2)
        
        # ノード名を太文字で描画
        name_text = font_bold.render(self.name, True, BLACK)
        name_rect = name_text.get_rect(center=(self.x, self.y - height//2 + 15))
        surface.blit(name_text, name_rect)
        
        # 全インターフェースのIPアドレスを表示
        if self.interfaces:
            # 複数のIPアドレスを縦に並べて表示
            start_y = self.y - height//2 + 35
            for i, interface in enumerate(self.interfaces):
                ip_text = font_small.render(interface['ip'], True, BLACK)
                ip_rect = ip_text.get_rect(center=(self.x, start_y + i * 12))
                surface.blit(ip_text, ip_rect)
        else:
            # インターフェース情報がない場合は代表IPを表示
            ip_text = font_small.render(self.ip, True, BLACK)
            ip_rect = ip_text.get_rect(center=(self.x, self.y + 10))
            surface.blit(ip_text, ip_rect)
    
    def get_bounds(self):
        """ノードの境界を取得（接続線計算用）"""
        interface_count = len(self.interfaces) if self.interfaces else 1
        width = 120
        height = max(60, 30 + interface_count * 12)
        return {
            'left': self.x - width//2,
            'right': self.x + width//2,
            'top': self.y - height//2,
            'bottom': self.y + height//2,
            'width': width,
            'height': height
        }

class RoutingGame:
    def __init__(self):
        self.state = "menu"  # menu, game, result
        self.difficulty = None
        self.nodes = []
        self.selected_node = None
        self.show_ip_table = True  # True: IP表示, False: ルーティング表示
        self.input_text = ""
        self.input_active = False
        self.input_field = None  # (node_index, field_name)
        self.start_time = None
        self.end_time = None
        self.problems = []
        self.current_problem = None
        self.user_answers = {}
        
    def create_problem(self, difficulty: str):
        """難易度に応じた問題を生成"""
        if difficulty == "初級編":
            return self.create_beginner_problem()
        elif difficulty == "中級編":
            return self.create_intermediate_problem()
        else:
            return self.create_advanced_problem()
    
    def create_beginner_problem(self):
        """初級問題（3ノード、1つの誤り）"""
        nodes = [
            NetworkNode("Router1", "192.168.1.1", 180, 250),
            NetworkNode("Router2", "192.168.2.1", 380, 250),
            NetworkNode("PC1", "192.168.1.100", 180, 380)
        ]
        
        # インターフェース情報を設定
        nodes[0].add_interface("eth0", "192.168.1.1", "255.255.255.0")
        nodes[0].add_interface("eth1", "192.168.12.1", "255.255.255.0")
        
        nodes[1].add_interface("eth0", "192.168.2.1", "255.255.255.0")
        nodes[1].add_interface("eth1", "192.168.12.2", "255.255.255.0")
        
        nodes[2].add_interface("eth0", "192.168.1.100", "255.255.255.0")
        
        # Router1の既存ルーティング設定（完全）
        nodes[0].add_route("192.168.1.0/24", "0.0.0.0", "eth0")  # 直接接続
        nodes[0].add_route("192.168.12.0/24", "0.0.0.0", "eth1")  # 直接接続
        nodes[0].add_route("192.168.2.0/24", "192.168.12.2", "eth1")  # Router2のLANへの経路
        
        # Router2の既存ルーティング設定（不完全）
        nodes[1].add_route("192.168.2.0/24", "0.0.0.0", "eth0")  # 直接接続
        nodes[1].add_route("192.168.12.0/24", "0.0.0.0", "eth1")  # 直接接続
        # 意図的に欠落: Router1のLANセグメント(192.168.1.0/24)への戻りの経路
        
        # PC1の設定
        nodes[2].add_route("0.0.0.0/0", "192.168.1.1", "eth0")
        
        problem_text = "PC1から192.168.2.100への通信で、往路は成功するが復路が失敗します。必要なルーティング設定を追加してください。"
        correct_answers = [
            {"node": "Router2", "destination": "192.168.1.0/24", "gateway": "192.168.12.1"}
        ]
        
        return {
            "nodes": nodes,
            "problem_text": problem_text,
            "correct_answers": correct_answers
        }
    
    def create_intermediate_problem(self):
        """中級問題（5ノード、2つの誤り）"""
        nodes = [
            NetworkNode("Router1", "10.0.1.1", 120, 250),
            NetworkNode("Router2", "10.0.2.1", 300, 220),
            NetworkNode("Router3", "10.0.3.1", 480, 250),
            NetworkNode("PC1", "10.0.1.100", 120, 380),
            NetworkNode("Server1", "10.0.3.100", 480, 380)
        ]
        
        # インターフェース情報を設定
        nodes[0].add_interface("eth0", "10.0.1.1", "255.255.255.0")
        nodes[0].add_interface("eth1", "10.0.12.1", "255.255.255.0")
        
        nodes[1].add_interface("eth0", "10.0.2.1", "255.255.255.0")
        nodes[1].add_interface("eth1", "10.0.12.2", "255.255.255.0")
        nodes[1].add_interface("eth2", "10.0.23.1", "255.255.255.0")
        
        nodes[2].add_interface("eth0", "10.0.3.1", "255.255.255.0")
        nodes[2].add_interface("eth1", "10.0.23.2", "255.255.255.0")
        
        nodes[3].add_interface("eth0", "10.0.1.100", "255.255.255.0")
        nodes[4].add_interface("eth0", "10.0.3.100", "255.255.255.0")
        
        # Router1の既存ルーティング設定
        nodes[0].add_route("10.0.1.0/24", "0.0.0.0", "eth0")  # 直接接続
        nodes[0].add_route("10.0.12.0/24", "0.0.0.0", "eth1")  # 直接接続
        nodes[0].add_route("10.0.2.0/24", "10.0.12.2", "eth1")
        # 意図的に欠落: 10.0.3.0/24への経路
        
        # Router2の既存ルーティング設定
        nodes[1].add_route("10.0.2.0/24", "0.0.0.0", "eth0")  # 直接接続
        nodes[1].add_route("10.0.12.0/24", "0.0.0.0", "eth1")  # 直接接続
        nodes[1].add_route("10.0.23.0/24", "0.0.0.0", "eth2")  # 直接接続
        nodes[1].add_route("10.0.1.0/24", "10.0.12.1", "eth1")
        nodes[1].add_route("10.0.3.0/24", "10.0.23.2", "eth2")
        
        # Router3の既存ルーティング設定
        nodes[2].add_route("10.0.3.0/24", "0.0.0.0", "eth0")  # 直接接続
        nodes[2].add_route("10.0.23.0/24", "0.0.0.0", "eth1")  # 直接接続
        nodes[2].add_route("10.0.2.0/24", "10.0.23.1", "eth1")
        # 意図的に欠落: 10.0.1.0/24への経路
        
        # エンドデバイスの設定
        nodes[3].add_route("0.0.0.0/0", "10.0.1.1", "eth0")
        nodes[4].add_route("0.0.0.0/0", "10.0.3.1", "eth0")
        
        problem_text = "PC1からServer1への通信ができません。必要なルーティング設定を追加してください。"
        correct_answers = [
            {"node": "Router1", "destination": "10.0.3.0/24", "gateway": "10.0.12.2"},
            {"node": "Router3", "destination": "10.0.1.0/24", "gateway": "10.0.23.1"}
        ]
        
        return {
            "nodes": nodes,
            "problem_text": problem_text,
            "correct_answers": correct_answers
        }
    
    def create_advanced_problem(self):
        """上級問題（6ノード、3つの誤り）"""
        nodes = [
            NetworkNode("Router1", "172.16.1.1", 100, 200),
            NetworkNode("Router2", "172.16.2.1", 280, 180),
            NetworkNode("Router3", "172.16.3.1", 460, 200),
            NetworkNode("PC1", "172.16.1.100", 100, 350),
            NetworkNode("PC2", "172.16.2.100", 280, 350),
            NetworkNode("Server1", "172.16.3.100", 460, 350)
        ]
        
        # インターフェース情報を設定
        nodes[0].add_interface("eth0", "172.16.1.1", "255.255.255.0")
        nodes[0].add_interface("eth1", "172.16.12.1", "255.255.255.0")
        nodes[0].add_interface("eth2", "172.16.13.1", "255.255.255.0")
        
        nodes[1].add_interface("eth0", "172.16.2.1", "255.255.255.0")
        nodes[1].add_interface("eth1", "172.16.12.2", "255.255.255.0")
        nodes[1].add_interface("eth2", "172.16.23.1", "255.255.255.0")
        
        nodes[2].add_interface("eth0", "172.16.3.1", "255.255.255.0")
        nodes[2].add_interface("eth1", "172.16.23.2", "255.255.255.0")
        nodes[2].add_interface("eth2", "172.16.13.2", "255.255.255.0")
        
        nodes[3].add_interface("eth0", "172.16.1.100", "255.255.255.0")
        nodes[4].add_interface("eth0", "172.16.2.100", "255.255.255.0")
        nodes[5].add_interface("eth0", "172.16.3.100", "255.255.255.0")
        
        # Router1の既存ルーティング設定
        nodes[0].add_route("172.16.1.0/24", "0.0.0.0", "eth0")  # 直接接続
        nodes[0].add_route("172.16.12.0/24", "0.0.0.0", "eth1")  # 直接接続
        nodes[0].add_route("172.16.13.0/24", "0.0.0.0", "eth2")  # 直接接続
        nodes[0].add_route("172.16.2.0/24", "172.16.12.2", "eth1")
        # 意図的に欠落: 172.16.3.0/24への経路
        
        # Router2の既存ルーティング設定
        nodes[1].add_route("172.16.2.0/24", "0.0.0.0", "eth0")  # 直接接続
        nodes[1].add_route("172.16.12.0/24", "0.0.0.0", "eth1")  # 直接接続
        nodes[1].add_route("172.16.23.0/24", "0.0.0.0", "eth2")  # 直接接続
        nodes[1].add_route("172.16.1.0/24", "172.16.12.1", "eth1")
        # 意図的に欠落: 172.16.3.0/24への経路
        
        # Router3の既存ルーティング設定
        nodes[2].add_route("172.16.3.0/24", "0.0.0.0", "eth0")  # 直接接続
        nodes[2].add_route("172.16.23.0/24", "0.0.0.0", "eth1")  # 直接接続
        nodes[2].add_route("172.16.13.0/24", "0.0.0.0", "eth2")  # 直接接続
        nodes[2].add_route("172.16.2.0/24", "172.16.23.1", "eth1")
        # 意図的に欠落: 172.16.1.0/24への経路
        
        # エンドデバイスの設定
        nodes[3].add_route("0.0.0.0/0", "172.16.1.1", "eth0")
        nodes[4].add_route("0.0.0.0/0", "172.16.2.1", "eth0")
        nodes[5].add_route("0.0.0.0/0", "172.16.3.1", "eth0")
        
        problem_text = "全てのPCとサーバー間で相互通信ができません。必要なルーティング設定を追加してください。"
        correct_answers = [
            {"node": "Router1", "destination": "172.16.3.0/24", "gateway": "172.16.13.2"},
            {"node": "Router2", "destination": "172.16.3.0/24", "gateway": "172.16.23.2"},
            {"node": "Router3", "destination": "172.16.1.0/24", "gateway": "172.16.13.1"}
        ]
        
        return {
            "nodes": nodes,
            "problem_text": problem_text,
            "correct_answers": correct_answers
        }
    
    def draw_menu(self):
        """メニュー画面を描画"""
        screen.fill(WHITE)
        
        # タイトル
        title = font_large.render("ネットワークルーティングゲーム", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 150))
        screen.blit(title, title_rect)
        
        # 難易度選択ボタン
        buttons = [
            ("初級編", 300),
            ("中級編", 400),
            ("上級編", 500)
        ]
        
        for text, y in buttons:
            button_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, y, 200, 50)
            pygame.draw.rect(screen, LIGHT_BLUE, button_rect)
            pygame.draw.rect(screen, BLACK, button_rect, 2)
            
            button_text = font_medium.render(text, True, BLACK)
            text_rect = button_text.get_rect(center=button_rect.center)
            screen.blit(button_text, text_rect)
    
    def draw_game(self):
        """ゲーム画面を描画"""
        screen.fill(WHITE)
        
        # 問題部分
        problem_rect = pygame.Rect(10, 10, SCREEN_WIDTH - 20, 100)
        pygame.draw.rect(screen, LIGHT_GRAY, problem_rect)
        pygame.draw.rect(screen, BLACK, problem_rect, 2)
        
        problem_title = font_medium.render("問題", True, BLACK)
        screen.blit(problem_title, (20, 20))
        
        if self.current_problem:
            problem_text = font_small.render(self.current_problem["problem_text"], True, BLACK)
            screen.blit(problem_text, (20, 50))
        
        # 回答終了ボタン
        answer_button = pygame.Rect(SCREEN_WIDTH - 120, 70, 100, 30)
        pygame.draw.rect(screen, GREEN, answer_button)
        pygame.draw.rect(screen, BLACK, answer_button, 2)
        answer_text = font_small.render("回答終了", True, BLACK)
        answer_text_rect = answer_text.get_rect(center=answer_button.center)
        screen.blit(answer_text, answer_text_rect)
        
        # ネットワーク構成部分
        network_rect = pygame.Rect(10, 120, SCREEN_WIDTH//2 - 15, 400)
        pygame.draw.rect(screen, WHITE, network_rect)
        pygame.draw.rect(screen, BLACK, network_rect, 2)
        
        network_title = font_medium.render("ネットワーク構成", True, BLACK)
        screen.blit(network_title, (20, 130))
        
        # ノードを描画
        for node in self.nodes:
            node.draw(screen)
        
        # ノード間の接続線を描画
        self.draw_connections()
        
        # IP/ルーティング表示部分
        table_rect = pygame.Rect(SCREEN_WIDTH//2 + 5, 120, SCREEN_WIDTH//2 - 15, 400)
        pygame.draw.rect(screen, WHITE, table_rect)
        pygame.draw.rect(screen, BLACK, table_rect, 2)
        
        # IP/ルーティング切り替えボタン
        ip_button = pygame.Rect(SCREEN_WIDTH//2 + 15, 130, 60, 25)
        routing_button = pygame.Rect(SCREEN_WIDTH//2 + 85, 130, 100, 25)
        
        ip_color = YELLOW if self.show_ip_table else LIGHT_GRAY
        routing_color = YELLOW if not self.show_ip_table else LIGHT_GRAY
        
        pygame.draw.rect(screen, ip_color, ip_button)
        pygame.draw.rect(screen, BLACK, ip_button, 2)
        pygame.draw.rect(screen, routing_color, routing_button)
        pygame.draw.rect(screen, BLACK, routing_button, 2)
        
        ip_text = font_small.render("IP", True, BLACK)
        routing_text = font_small.render("ルーティング", True, BLACK)
        
        ip_text_rect = ip_text.get_rect(center=ip_button.center)
        routing_text_rect = routing_text.get_rect(center=routing_button.center)
        
        screen.blit(ip_text, ip_text_rect)
        screen.blit(routing_text, routing_text_rect)
        
        # 選択されたノードの情報を表示
        if self.selected_node:
            self.draw_node_info(table_rect)
    
    def calculate_line_endpoints(self, node1, node2):
        """2つのノード間の接続線の端点を計算（長方形の境界まで）"""
        import math
        
        bounds1 = node1.get_bounds()
        bounds2 = node2.get_bounds()
        
        # ノード中心間の方向ベクトル
        dx = node2.x - node1.x
        dy = node2.y - node1.y
        
        if dx == 0 and dy == 0:
            return (node1.x, node1.y), (node2.x, node2.y)
        
        # node1から見たnode2の方向で長方形の境界点を計算
        def get_rect_intersection(center_x, center_y, bounds, target_x, target_y):
            # 中心から目標点への方向
            dx = target_x - center_x
            dy = target_y - center_y
            
            if dx == 0 and dy == 0:
                return center_x, center_y
            
            # 長方形の境界との交点を計算
            half_width = bounds['width'] // 2
            half_height = bounds['height'] // 2
            
            # 各辺との交点を計算
            intersections = []
            
            # 右辺
            if dx > 0:
                t = half_width / dx
                y = dy * t
                if abs(y) <= half_height:
                    intersections.append((center_x + half_width, center_y + y))
            
            # 左辺
            if dx < 0:
                t = -half_width / dx
                y = dy * t
                if abs(y) <= half_height:
                    intersections.append((center_x - half_width, center_y + y))
            
            # 下辺
            if dy > 0:
                t = half_height / dy
                x = dx * t
                if abs(x) <= half_width:
                    intersections.append((center_x + x, center_y + half_height))
            
            # 上辺
            if dy < 0:
                t = -half_height / dy
                x = dx * t
                if abs(x) <= half_width:
                    intersections.append((center_x + x, center_y - half_height))
            
            # 最も近い交点を選択
            if intersections:
                min_dist = float('inf')
                best_point = intersections[0]
                for point in intersections:
                    dist = (point[0] - target_x) ** 2 + (point[1] - target_y) ** 2
                    if dist < min_dist:
                        min_dist = dist
                        best_point = point
                return best_point
            
            return center_x, center_y
        
        start_point = get_rect_intersection(node1.x, node1.y, bounds1, node2.x, node2.y)
        end_point = get_rect_intersection(node2.x, node2.y, bounds2, node1.x, node1.y)
        
        return (int(start_point[0]), int(start_point[1])), (int(end_point[0]), int(end_point[1]))
    
    def draw_connections(self):
        """ノード間の接続線を描画"""
        if self.difficulty == "初級編" and len(self.nodes) >= 3:
            # 初級編: Router1-Router2, Router1-PC1
            start_pos, end_pos = self.calculate_line_endpoints(self.nodes[0], self.nodes[1])
            pygame.draw.line(screen, BLACK, start_pos, end_pos, 2)
            
            start_pos, end_pos = self.calculate_line_endpoints(self.nodes[0], self.nodes[2])
            pygame.draw.line(screen, BLACK, start_pos, end_pos, 2)
            
        elif self.difficulty == "中級編" and len(self.nodes) >= 5:
            # 中級編: Router1-Router2-Router3, Router1-PC1, Router3-Server1
            start_pos, end_pos = self.calculate_line_endpoints(self.nodes[0], self.nodes[1])
            pygame.draw.line(screen, BLACK, start_pos, end_pos, 2)
            
            start_pos, end_pos = self.calculate_line_endpoints(self.nodes[1], self.nodes[2])
            pygame.draw.line(screen, BLACK, start_pos, end_pos, 2)
            
            start_pos, end_pos = self.calculate_line_endpoints(self.nodes[0], self.nodes[3])
            pygame.draw.line(screen, BLACK, start_pos, end_pos, 2)
            
            start_pos, end_pos = self.calculate_line_endpoints(self.nodes[2], self.nodes[4])
            pygame.draw.line(screen, BLACK, start_pos, end_pos, 2)
            
        elif self.difficulty == "上級編" and len(self.nodes) >= 6:
            # 上級編: より複雑な接続パターン
            connections = [
                (0, 1), (1, 2), (0, 3), (1, 4), (2, 5),  # 基本接続
                (0, 2)  # 追加接続
            ]
            for start_idx, end_idx in connections:
                if start_idx < len(self.nodes) and end_idx < len(self.nodes):
                    start_pos, end_pos = self.calculate_line_endpoints(self.nodes[start_idx], self.nodes[end_idx])
                    pygame.draw.line(screen, BLACK, start_pos, end_pos, 2)
    
    def draw_node_info(self, rect):
        """選択されたノードの情報を表示"""
        y_offset = rect.y + 170
        
        if self.show_ip_table:
            # IP情報を表形式で表示（IF、IP、ネットマスクの3列）
            table_title = font_small.render(f"{self.selected_node.name} - IP情報", True, BLACK)
            screen.blit(table_title, (rect.x + 10, y_offset))
            
            # IP情報テーブル
            ip_headers = ["IF", "IP", "ネットマスク"]
            header_y = y_offset + 30
            col_widths = [80, 140, 140]
            
            # ヘッダー背景
            header_rect = pygame.Rect(rect.x + 10, header_y, sum(col_widths), 20)
            pygame.draw.rect(screen, LIGHT_GRAY, header_rect)
            pygame.draw.rect(screen, BLACK, header_rect, 1)
            
            # ヘッダーテキスト
            col_x = rect.x + 10
            for i, header in enumerate(ip_headers):
                header_text = font_small.render(header, True, BLACK)
                screen.blit(header_text, (col_x + 5, header_y + 3))
                # 列の境界線
                if i < len(ip_headers) - 1:
                    pygame.draw.line(screen, BLACK, (col_x + col_widths[i], header_y), 
                                   (col_x + col_widths[i], header_y + 20), 1)
                col_x += col_widths[i]
            
            # インターフェース情報の行
            row_y = header_y + 20
            for interface_info in self.selected_node.interfaces:
                # 行の背景
                row_rect = pygame.Rect(rect.x + 10, row_y, sum(col_widths), 20)
                pygame.draw.rect(screen, WHITE, row_rect)
                pygame.draw.rect(screen, BLACK, row_rect, 1)
                
                # 行のデータ
                col_x = rect.x + 10
                row_data = [
                    interface_info['interface'],
                    interface_info['ip'],
                    interface_info['netmask']
                ]
                
                for i, value in enumerate(row_data):
                    value_text = font_small.render(str(value), True, BLACK)
                    screen.blit(value_text, (col_x + 5, row_y + 3))
                    # 列の境界線
                    if i < len(row_data) - 1:
                        pygame.draw.line(screen, BLACK, (col_x + col_widths[i], row_y), 
                                       (col_x + col_widths[i], row_y + 20), 1)
                    col_x += col_widths[i]
                row_y += 20
                
        else:
            # ルーティングテーブルを表形式で表示
            table_title = font_small.render(f"{self.selected_node.name} - ルーティングテーブル", True, BLACK)
            screen.blit(table_title, (rect.x + 10, y_offset))
            
            # テーブルヘッダー（インターフェース列を削除）
            headers = ["宛先", "ゲートウェイ"]
            header_y = y_offset + 30
            col_widths = [180, 180]  # 2列に拡張
            
            # ヘッダー背景
            header_rect = pygame.Rect(rect.x + 10, header_y, sum(col_widths), 20)
            pygame.draw.rect(screen, LIGHT_GRAY, header_rect)
            pygame.draw.rect(screen, BLACK, header_rect, 1)
            
            # ヘッダーテキスト
            col_x = rect.x + 10
            for i, header in enumerate(headers):
                header_text = font_small.render(header, True, BLACK)
                screen.blit(header_text, (col_x + 5, header_y + 3))
                # 列の境界線
                if i < len(headers) - 1:
                    pygame.draw.line(screen, BLACK, (col_x + col_widths[i], header_y), 
                                   (col_x + col_widths[i], header_y + 20), 1)
                col_x += col_widths[i]
            
            # 既存のルーティングエントリ
            row_y = header_y + 20
            for route in self.selected_node.routing_table:
                # 行の背景
                row_rect = pygame.Rect(rect.x + 10, row_y, sum(col_widths), 20)
                pygame.draw.rect(screen, WHITE, row_rect)
                pygame.draw.rect(screen, BLACK, row_rect, 1)
                
                # 行のデータ（インターフェース列を削除）
                col_x = rect.x + 10
                values = [route['destination'], route['gateway']]
                for i, value in enumerate(values):
                    value_text = font_small.render(value, True, BLACK)
                    screen.blit(value_text, (col_x + 5, row_y + 3))
                    # 列の境界線
                    if i < len(values) - 1:
                        pygame.draw.line(screen, BLACK, (col_x + col_widths[i], row_y), 
                                       (col_x + col_widths[i], row_y + 20), 1)
                    col_x += col_widths[i]
                row_y += 20
            
            # 新規エントリ入力欄
            self.draw_input_row(rect.x + 10, row_y, col_widths)
    
    def draw_input_row(self, x, y, col_widths):
        """新規ルーティングエントリの入力欄を描画"""
        fields = ["destination", "gateway"]  # インターフェース列を削除
        
        # 入力行の背景（薄い黄色で強調）
        input_row_rect = pygame.Rect(x, y, sum(col_widths), 25)
        pygame.draw.rect(screen, (255, 255, 200), input_row_rect)
        pygame.draw.rect(screen, BLACK, input_row_rect, 1)
        
        # 「新規追加」ラベルを右側に表示
        label_text = font_small.render("新規追加:", True, BLACK)
        label_x = x + sum(col_widths) + 10  # 表の右側に配置
        screen.blit(label_text, (label_x, y + 5))
        
        col_x = x
        for i, field in enumerate(fields):
            input_rect = pygame.Rect(col_x, y + 2, col_widths[i] - 2, 21)
            
            # 入力フィールドの背景色
            if self.input_field and self.input_field[1] == field:
                pygame.draw.rect(screen, YELLOW, input_rect)
            else:
                pygame.draw.rect(screen, WHITE, input_rect)
            
            pygame.draw.rect(screen, BLACK, input_rect, 1)
            
            # 入力テキストを表示
            node_key = f"{self.selected_node.name}_{field}"
            text_value = self.user_answers.get(node_key, "")
            
            if self.input_field and self.input_field[1] == field and self.input_active:
                text_value = self.input_text
            
            if text_value:
                input_text = font_small.render(text_value, True, BLACK)
                screen.blit(input_text, (col_x + 3, y + 5))
            else:
                # プレースホルダーテキスト
                placeholder_texts = {
                    "destination": "例: 0.0.0.0/0",
                    "gateway": "例: 192.168.1.1"
                }
                placeholder = font_small.render(placeholder_texts[field], True, GRAY)
                screen.blit(placeholder, (col_x + 3, y + 5))
            
            # 列の境界線
            if i < len(fields) - 1:
                pygame.draw.line(screen, BLACK, (col_x + col_widths[i], y), 
                               (col_x + col_widths[i], y + 25), 1)
            
            col_x += col_widths[i]
    
    def draw_result(self):
        """結果画面を描画"""
        screen.fill(WHITE)
        
        # 結果タイトル
        is_correct = self.check_answer()
        if is_correct:
            result_text = "正解！"
            color = GREEN
        else:
            result_text = "不正解"
            color = RED
        
        title = font_large.render(result_text, True, color)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 100))
        screen.blit(title, title_rect)
        
        # 時間表示
        if self.start_time and self.end_time:
            elapsed_time = self.end_time - self.start_time
            time_text = font_medium.render(f"経過時間: {elapsed_time:.1f}秒", True, BLACK)
            time_rect = time_text.get_rect(center=(SCREEN_WIDTH//2, 150))
            screen.blit(time_text, time_rect)
        
        # 不正解の場合、詳細理由を表示
        if not is_correct:
            reasons = self.get_incorrect_reason()
            y_pos = 200
            
            for reason in reasons:
                if reason.startswith("【"):
                    # セクションヘッダー（太字風に）
                    reason_text = font_medium.render(reason, True, RED)
                    reason_rect = reason_text.get_rect(center=(SCREEN_WIDTH//2, y_pos))
                    screen.blit(reason_text, reason_rect)
                    y_pos += 30
                elif reason.startswith("•"):
                    # メインエラー項目
                    reason_text = font_small.render(reason, True, BLACK)
                    screen.blit(reason_text, (50, y_pos))
                    y_pos += 20
                elif reason.startswith("  -") or reason.startswith("  入力値:") or reason.startswith("  正解値:"):
                    # 詳細エラー情報（インデント）
                    reason_text = font_small.render(reason, True, GRAY)
                    screen.blit(reason_text, (80, y_pos))
                    y_pos += 18
                else:
                    # 一般的なメッセージ
                    reason_text = font_small.render(reason, True, BLACK)
                    reason_rect = reason_text.get_rect(center=(SCREEN_WIDTH//2, y_pos))
                    screen.blit(reason_text, reason_rect)
                    y_pos += 25
                
                # 画面下部に近づいたら改ページまたは省略
                if y_pos > SCREEN_HEIGHT - 150:
                    if len(reasons) > reasons.index(reason) + 1:
                        more_text = font_small.render("... (他にもエラーがあります)", True, GRAY)
                        more_rect = more_text.get_rect(center=(SCREEN_WIDTH//2, y_pos))
                        screen.blit(more_text, more_rect)
                    break
        
        # 正解の場合の追加メッセージ
        if is_correct:
            congrats_text = font_medium.render("おめでとうございます！", True, GREEN)
            congrats_rect = congrats_text.get_rect(center=(SCREEN_WIDTH//2, 200))
            screen.blit(congrats_text, congrats_rect)
            
            if self.difficulty:
                difficulty_text = font_small.render(f"{self.difficulty}をクリアしました", True, BLACK)
                difficulty_rect = difficulty_text.get_rect(center=(SCREEN_WIDTH//2, 230))
                screen.blit(difficulty_text, difficulty_rect)
        
        # メニューに戻るボタン
        menu_button = pygame.Rect(SCREEN_WIDTH//2 - 75, SCREEN_HEIGHT - 100, 150, 50)
        pygame.draw.rect(screen, LIGHT_BLUE, menu_button)
        pygame.draw.rect(screen, BLACK, menu_button, 2)
        
        menu_text = font_medium.render("メニューに戻る", True, BLACK)
        menu_text_rect = menu_text.get_rect(center=menu_button.center)
        screen.blit(menu_text, menu_text_rect)
    
    def check_answer(self):
        """回答をチェック"""
        if not self.current_problem:
            return False
        
        # 空欄を削除してから回答をチェック
        self.clean_user_answers()
        
        correct_answers = self.current_problem["correct_answers"]
        self.missing_routes = []  # 不足しているルートを記録
        self.incorrect_routes = []  # 間違っているルートを記録
        
        for answer in correct_answers:
            node_name = answer["node"]
            required_dest = answer["destination"]
            required_gw = answer["gateway"]
            
            # ユーザーの入力をチェック（インターフェース列を削除）
            dest_key = f"{node_name}_destination"
            gw_key = f"{node_name}_gateway"
            
            user_dest = self.user_answers.get(dest_key, "").strip()
            user_gw = self.user_answers.get(gw_key, "").strip()
            
            # 入力が完全に空の場合
            if not user_dest and not user_gw:
                self.missing_routes.append({
                    'node': node_name,
                    'required_dest': required_dest,
                    'required_gw': required_gw,
                    'reason': '設定が未入力'
                })
                continue
            
            # 部分的に入力されている場合の詳細チェック
            route_correct = True
            errors = []
            
            if not self.route_matches(user_dest, required_dest):
                route_correct = False
                if not user_dest:
                    errors.append(f"宛先が未入力（正解: {required_dest}）")
                else:
                    errors.append(f"宛先が間違い（入力: {user_dest}, 正解: {required_dest}）")
            
            if user_gw != required_gw:
                route_correct = False
                if not user_gw:
                    errors.append(f"ゲートウェイが未入力（正解: {required_gw}）")
                else:
                    errors.append(f"ゲートウェイが間違い（入力: {user_gw}, 正解: {required_gw}）")
            
            if not route_correct:
                self.incorrect_routes.append({
                    'node': node_name,
                    'errors': errors,
                    'user_input': f"{user_dest} -> {user_gw}",
                    'correct_input': f"{required_dest} -> {required_gw}"
                })
        
        return len(self.missing_routes) == 0 and len(self.incorrect_routes) == 0
    
    def clean_user_answers(self):
        """ユーザー回答から空欄を削除"""
        keys_to_remove = []
        for key, value in self.user_answers.items():
            cleaned_value = value.strip() if isinstance(value, str) else value
            if not cleaned_value:
                keys_to_remove.append(key)
            else:
                self.user_answers[key] = cleaned_value
        
        # 空欄のキーを削除
        for key in keys_to_remove:
            del self.user_answers[key]
    
    def route_matches(self, user_route, required_route):
        """ルートの表記が一致するかチェック（デフォルトルートの代替表記も考慮）"""
        if user_route == required_route:
            return True
        
        # デフォルトルートの代替表記
        default_routes = ["0.0.0.0/0", "default", "0.0.0.0"]
        if user_route in default_routes and required_route in default_routes:
            return True
        
        return False
    
    def get_incorrect_reason(self):
        """不正解の詳細理由を取得"""
        reasons = []
        
        if hasattr(self, 'missing_routes') and self.missing_routes:
            reasons.append("【未入力の設定】")
            for missing in self.missing_routes:
                reasons.append(f"• {missing['node']}: {missing['required_dest']} -> {missing['required_gw']}")
        
        if hasattr(self, 'incorrect_routes') and self.incorrect_routes:
            reasons.append("【間違った設定】")
            for incorrect in self.incorrect_routes:
                reasons.append(f"• {incorrect['node']}:")
                for error in incorrect['errors']:
                    reasons.append(f"  - {error}")
                reasons.append(f"  入力値: {incorrect['user_input']}")
                reasons.append(f"  正解値: {incorrect['correct_input']}")
        
        if not reasons:
            reasons.append("設定に問題があります。正解と比較してください。")
        
        return reasons
    
    def handle_click(self, pos):
        """クリックイベントを処理"""
        if self.state == "menu":
            self.handle_menu_click(pos)
        elif self.state == "game":
            self.handle_game_click(pos)
        elif self.state == "result":
            self.handle_result_click(pos)
    
    def handle_menu_click(self, pos):
        """メニューでのクリック処理"""
        buttons = [
            ("初級編", pygame.Rect(SCREEN_WIDTH//2 - 100, 300, 200, 50)),
            ("中級編", pygame.Rect(SCREEN_WIDTH//2 - 100, 400, 200, 50)),
            ("上級編", pygame.Rect(SCREEN_WIDTH//2 - 100, 500, 200, 50))
        ]
        
        for difficulty, rect in buttons:
            if rect.collidepoint(pos):
                self.difficulty = difficulty
                self.start_game()
                break
    
    def handle_game_click(self, pos):
        """ゲームでのクリック処理"""
        # 回答終了ボタン
        answer_button = pygame.Rect(SCREEN_WIDTH - 120, 70, 100, 30)
        if answer_button.collidepoint(pos):
            self.end_time = pygame.time.get_ticks() / 1000.0
            self.state = "result"
            return
        
        # IP/ルーティング切り替えボタン
        ip_button = pygame.Rect(SCREEN_WIDTH//2 + 15, 130, 60, 25)
        routing_button = pygame.Rect(SCREEN_WIDTH//2 + 85, 130, 100, 25)
        
        if ip_button.collidepoint(pos):
            self.show_ip_table = True
            return
        elif routing_button.collidepoint(pos):
            self.show_ip_table = False
            return
        
        # ノード選択
        for node in self.nodes:
            bounds = node.get_bounds()
            node_rect = pygame.Rect(bounds['left'], bounds['top'], bounds['width'], bounds['height'])
            if node_rect.collidepoint(pos):
                # 全ノードの選択状態をリセット
                for n in self.nodes:
                    n.selected = False
                node.selected = True
                self.selected_node = node
                self.show_ip_table = False  # ノード選択時はルーティング表示
                return
        
        # 入力フィールドのクリック処理
        if self.selected_node and not self.show_ip_table:
            self.handle_input_field_click(pos)
    
    def handle_input_field_click(self, pos):
        """入力フィールドのクリック処理"""
        table_rect = pygame.Rect(SCREEN_WIDTH//2 + 5, 120, SCREEN_WIDTH//2 - 15, 400)
        y_offset = table_rect.y + 170 + 30 + 20 + len(self.selected_node.routing_table) * 20
        
        fields = ["destination", "gateway"]  # インターフェース列を削除
        col_widths = [180, 180]
        col_x = table_rect.x + 10
        
        for i, field in enumerate(fields):
            input_rect = pygame.Rect(col_x, y_offset + 2, col_widths[i] - 2, 21)
            if input_rect.collidepoint(pos):
                self.input_field = (self.selected_node.name, field)
                self.input_active = True
                node_key = f"{self.selected_node.name}_{field}"
                self.input_text = self.user_answers.get(node_key, "")
                return
            col_x += col_widths[i]
        
        # フィールド外をクリックした場合
        self.input_active = False
        self.input_field = None
    
    def handle_result_click(self, pos):
        """結果画面でのクリック処理"""
        menu_button = pygame.Rect(SCREEN_WIDTH//2 - 75, SCREEN_HEIGHT - 100, 150, 50)
        if menu_button.collidepoint(pos):
            self.state = "menu"
            self.reset_game()
    
    def handle_keydown(self, event):
        """キー入力処理"""
        if self.input_active and self.input_field:
            if event.key == pygame.K_RETURN:
                # Enterキーで入力確定（空白文字を除去）
                cleaned_input = self.input_text.strip()
                if cleaned_input:  # 空文字列でない場合のみ保存
                    node_key = f"{self.input_field[0]}_{self.input_field[1]}"
                    self.user_answers[node_key] = cleaned_input
                self.input_active = False
                self.input_field = None
                self.input_text = ""
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            elif event.key == pygame.K_ESCAPE:
                # Escapeキーで入力キャンセル
                self.input_active = False
                self.input_field = None
                self.input_text = ""
            else:
                # 通常の文字入力（制御文字は除外）
                if event.unicode.isprintable():
                    self.input_text += event.unicode
    
    def start_game(self):
        """ゲーム開始"""
        self.state = "game"
        self.current_problem = self.create_problem(self.difficulty)
        self.nodes = self.current_problem["nodes"]
        self.selected_node = None
        self.user_answers = {}
        self.start_time = pygame.time.get_ticks() / 1000.0
    
    def reset_game(self):
        """ゲームリセット"""
        self.difficulty = None
        self.nodes = []
        self.selected_node = None
        self.current_problem = None
        self.user_answers = {}
        self.start_time = None
        self.end_time = None
        self.input_active = False
        self.input_field = None
        self.input_text = ""
        self.missing_routes = []
        self.incorrect_routes = []
    
    def run(self):
        """メインゲームループ"""
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    self.handle_keydown(event)
            
            # 画面描画
            if self.state == "menu":
                self.draw_menu()
            elif self.state == "game":
                self.draw_game()
            elif self.state == "result":
                self.draw_result()
            
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = RoutingGame()
    game.run()
