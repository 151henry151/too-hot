# Too Hot - Climate Awareness Campaign

> **When temperatures are 10°F hotter than normal, wear your "IT'S TOO HOT!" shirt and start conversations about climate change.**

## 🌍 Quick Overview

**Too Hot** is a climate activism platform that alerts you when your local temperature is significantly hotter than historical averages. When these climate anomalies occur, we encourage wearing "IT'S TOO HOT!" t-shirts to raise awareness and start important conversations about climate action.

### 🎯 What It Does

- **Temperature Monitoring**: Checks your local weather against historical averages
- **Smart Alerts**: Notifies you when temperatures are 10°F+ hotter than normal
- **Climate Activism**: Encourages wearing "IT'S TOO HOT!" shirts during extreme heat
- **Community Building**: Connects people through shared climate awareness

### 📱 iPhone App Plan

We're developing a mobile app to make climate activism even more accessible:

**Phase 1: Core Features**
- Location-based temperature monitoring
- Push notifications for extreme heat events
- "IT'S TOO HOT!" shirt ordering system
- Social sharing of climate data

**Phase 2: Additional Features**
- Community features and local climate groups
- Historical climate data visualization
- Integration with climate action organizations
- Advanced weather pattern analysis

### 🌐 Live Campaign

- **Website**: https://its2hot.org
- **Cloud Run URL**: https://too-hot-ao5zbahlha-uc.a.run.app
- **GitHub**: https://github.com/151henry151/too-hot

---

## 🛠️ Technical Information

### Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Frontend  │    │  Flask Backend  │    │  Weather API    │
│   (HTML/CSS/JS) │◄──►│   (Python)      │◄──►│   (WeatherAPI)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│  Email Service  │    │  Temperature    │
│   (Gmail SMTP)  │    │   Scheduler     │
└─────────────────┘    └─────────────────┘
```

### Key Components

- **Web UI**: Responsive Flask template with Tailwind CSS
- **Backend API**: RESTful Flask endpoints for subscriptions and temperature checks
- **Email System**: Automated notifications using Flask-Mail and Gmail
- **Weather Integration**: Real-time and historical data from WeatherAPI.com
- **Scheduler**: Automated temperature monitoring and alert system

### Technology Stack

- **Backend**: Python Flask with Gunicorn
- **Frontend**: HTML, Tailwind CSS, JavaScript
- **Email**: Flask-Mail with Gmail SMTP
- **Weather Data**: WeatherAPI.com integration
- **Deployment**: Docker containers on Google Cloud Run
- **Domain**: Custom domain (its2hot.org) with SSL

---

## 🚀 Quick Start (For Developers)

### Prerequisites
- Python 3.11+
- Git
- Google Cloud CLI (for deployment)

### Local Development

1. **Clone and Setup**:
   ```bash
   git clone https://github.com/151henry151/too-hot.git
   cd too-hot
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Environment Configuration**:
   ```bash
   cp env.example .env
   # Edit .env with your API keys and email settings
   ```

3. **Run Locally**:
   ```bash
   python app.py
   # Visit http://localhost:5000
   ```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main campaign page |
| `/api/subscribe` | POST | Subscribe to temperature alerts |
| `/api/unsubscribe` | POST | Unsubscribe from alerts |
| `/api/subscribers` | GET | List all subscribers |
| `/api/check-temperatures` | GET | Check current temperatures |

### Environment Variables

```bash
# Required
WEATHER_API_KEY=your_weather_api_key
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password

# Optional
FLASK_ENV=development
```

---

## 🐳 Deployment

### Docker Deployment

1. **Build and Run Locally**:
   ```bash
   docker-compose up --build
   ```

2. **Deploy to Google Cloud**:
   ```bash
   ./deploy.sh
   ```

### Google Cloud Platform Setup

1. **Enable APIs**:
   ```bash
   gcloud services enable cloudbuild.googleapis.com run.googleapis.com containerregistry.googleapis.com artifactregistry.googleapis.com
   ```

2. **Configure Domain** (Optional):
   ```bash
   gcloud beta run domain-mappings create --service=too-hot --domain=your-domain.com --region=us-central1
   ```

---

## 📄 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

We welcome contributions! Please feel free to submit issues and pull requests.

### Development Roadmap

- [ ] iPhone app development
- [ ] Enhanced weather pattern analysis
- [ ] Community features
- [ ] Integration with climate organizations
- [ ] Advanced notification system
