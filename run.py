from src import create_app
from config import Config

app = create_app()

if __name__ == "__main__":
    print("http://127.0.0.1:5001/admin")
    print("http://127.0.0.1:5001/test")
    print("http://127.0.0.1:5001/admin/review")
    print("http://127.0.0.1:5001/admin/history")
    
    app.run(port=int(Config.PORT), debug=True)