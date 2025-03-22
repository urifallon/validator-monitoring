from api import create_app
from models import db
import os

app = create_app(os.getenv('FLASK_ENV', 'development'))

@app.route('/')
def index():
    return "Validator Monitoring API"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', debug=True) 