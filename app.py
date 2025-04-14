import os
from dotenv import load_dotenv
from app import create_app, db
from app.models import User, Site, Product, Analytics

# Load environment variables
load_dotenv()

# Create the application with the specified config
app = create_app(os.getenv('FLASK_CONFIG', 'development'))

# Define shell context
@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Site': Site,
        'Product': Product,
        'Analytics': Analytics
    }

# Run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000))) 