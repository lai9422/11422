from flask import Flask
from src.controller import webhook_blueprint
from src.admin import admin_blueprint
from src.test_chat import test_chat_blueprint  # <--- New: 匯入測試模組
from src.admin import admin_blueprint

def create_app():
    app = Flask(__name__, template_folder='../templates') 
    
    # 註冊 Blueprints
    app.register_blueprint(webhook_blueprint)
    app.register_blueprint(admin_blueprint)
    app.register_blueprint(test_chat_blueprint)  # <--- New: 註冊測試路由
    
    return app