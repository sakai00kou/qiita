#!/usr/bin/env python3
"""
ネットワークルーティングゲーム実行スクリプト
"""

import sys
import os

# 必要なライブラリのインストールチェック
try:
    import pygame
    print("PyGameが見つかりました。")
except ImportError:
    print("PyGameがインストールされていません。")
    print("以下のコマンドでインストールしてください:")
    print("pip install pygame")
    sys.exit(1)

# ゲームを実行
if __name__ == "__main__":
    print("ネットワークルーティングゲームを開始します...")
    print("操作方法:")
    print("1. メニューで難易度を選択")
    print("2. ネットワーク構成のノードをクリックして選択")
    print("3. IP/ルーティングボタンで表示を切り替え")
    print("4. ルーティング表の最下行に必要な設定を入力")
    print("5. 回答終了ボタンで結果を確認")
    print()
    
    # ゲームを実行
    from routing_game import RoutingGame
    game = RoutingGame()
    game.run()
