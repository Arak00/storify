# Storify

Storify is a web application that enables artists and content creators to automatically transform their social media feeds (Instagram, TikTok, Etsy) into a personalized, professional boutique website, with minimal technical expertise required.

## Features

- **Social Media Integration**: Connect your Instagram, TikTok, and Etsy accounts to automatically import your content.
- **Customizable Templates**: Choose from a variety of professionally designed templates for your boutique.
- **Easy Editing**: Drag-and-drop interface for customizing your site layout and content.
- **Product Management**: Showcase and sell your products/services directly from your boutique.
- **Analytics**: Track views, visitors, and engagement with your content (premium feature).
- **Custom Domain**: Use your own domain name for your boutique (premium feature).

## Plans

- **Free**: Get started with a basic boutique with up to 3 products, using a Storify subdomain.
- **Creator** (€9/month): Up to 15 products, custom domain, full customization, basic analytics.
- **Studio** (€19/month): Unlimited products, email integrations, advanced analytics, premium templates.
- **VIP Setup** (€79 one-time): Get a professionally configured boutique set up for you.

## Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL (for production)
- Redis (optional, for caching)

### Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/storify.git
cd storify
```

2. Create a virtual environment and activate it:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your configuration:

```
FLASK_APP=app.py
FLASK_ENV=development
FLASK_CONFIG=development
SECRET_KEY=your-secret-key

# Database
DEV_DATABASE_URL=sqlite:///dev.db
TEST_DATABASE_URL=sqlite:///test.db
# For production, use PostgreSQL:
# DATABASE_URL=postgresql://username:password@localhost/storify

# Instagram API
INSTAGRAM_CLIENT_ID=your-instagram-client-id
INSTAGRAM_CLIENT_SECRET=your-instagram-client-secret

# TikTok API
TIKTOK_CLIENT_KEY=your-tiktok-client-key
TIKTOK_CLIENT_SECRET=your-tiktok-client-secret

# Etsy API
ETSY_API_KEY=your-etsy-api-key
ETSY_API_SECRET=your-etsy-api-secret

# AWS S3 (for file storage)
AWS_ACCESS_KEY=your-aws-access-key
AWS_SECRET_KEY=your-aws-secret-key
AWS_BUCKET_NAME=storify-storage

# Redis (optional)
# REDIS_URL=redis://localhost:6379/0
```

5. Initialize the database:

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

6. Run the development server:

```bash
flask run
```

The application will be available at http://localhost:5000.

### Setting Up API Keys

To use the social media integration features, you need to register your application with each platform and obtain API keys:

- **Instagram**: Register at [Facebook for Developers](https://developers.facebook.com) and create an Instagram Graph API app.
- **TikTok**: Register at [TikTok for Developers](https://developers.tiktok.com) and create a TikTok Login Kit app.
- **Etsy**: Register at [Etsy Developer Portal](https://www.etsy.com/developers) and create an Etsy API app.

## Development

### Project Structure

```
storify/
├── app/                    # Application package
│   ├── models/             # Database models
│   ├── routes/             # Route blueprints
│   ├── services/           # External service integrations
│   ├── static/             # Static files (CSS, JS, images)
│   └── templates/          # HTML templates
├── migrations/             # Database migrations
├── tests/                  # Test suite
├── .env                    # Environment variables
├── app.py                  # Application entry point
├── config.py               # Configuration
└── requirements.txt        # Dependencies
```

### Running Tests

```bash
pytest
```

## Deployment

### Docker

A Dockerfile is provided for containerized deployment:

```bash
docker build -t storify .
docker run -p 5000:5000 storify
```

### Heroku

```bash
heroku create
git push heroku main
heroku run flask db upgrade
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Flask](https://flask.palletsprojects.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Instagram Graph API](https://developers.facebook.com/docs/instagram-api)
- [TikTok for Developers](https://developers.tiktok.com)
- [Etsy API](https://www.etsy.com/developers) 