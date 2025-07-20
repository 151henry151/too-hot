# Too Hot - Climate Awareness Campaign

A climate activism platform that notifies users when temperatures are 10°F hotter than the historical average for their location. When these climate anomalies occur, users are encouraged to wear "IT'S TOO HOT!" t-shirts to raise awareness about global warming and start conversations about climate action.

## Campaign Overview

This application is part of a climate awareness campaign designed to:
- **Detect Climate Anomalies**: Monitor when temperatures are 10°F+ hotter than historical averages
- **Mobilize Activists**: Notify subscribers when climate action is needed
- **Visual Impact**: Encourage wearing "IT'S TOO HOT!" t-shirts on anomaly days
- **Community Building**: Connect climate activists across different locations
- **Data-Driven Activism**: Use real climate data to drive awareness

## Current Features

### Web Interface
- **Modern Climate Activism Design**: Black and white theme matching the t-shirt design
- **Campaign Visuals**: Integration of flashmob protest images and t-shirt designs
- **Subscription System**: Easy email signup for climate alerts
- **Responsive Design**: Works on desktop and mobile devices
- **Subtle Unsubscribe**: Small grey link at bottom for easy opt-out

### Backend API
- **RESTful Climate API**: Ready for iPhone app integration
- **Email Notifications**: Automated climate alert system using Gmail SMTP
- **Location Support**: Auto-detection and manual location specification
- **Temperature Monitoring**: Real-time comparison with historical averages
- **Subscriber Management**: Track and manage climate activist community

### Automated Monitoring
- **Scheduled Checks**: Hourly temperature monitoring via scheduler
- **Climate Data Integration**: WeatherAPI.com for current and historical data
- **Smart Notifications**: Only alerts when 10°F+ anomaly detected
- **Action-Oriented Messaging**: Climate activism focused email content

## Architecture

```
too-hot/
├── app.py                    # Main Flask application with climate API
├── scheduler.py              # Automated temperature monitoring
├── templates/
│   └── index.html           # Climate activism web interface
├── static/
│   ├── img/
│   │   ├── climate_protest_flashmob.png  # Campaign flashmob image
│   │   └── tshirt.png                    # T-shirt design image
│   ├── css/                 # Styling for climate campaign
│   └── js/                  # Frontend interactions
├── requirements.txt          # Python dependencies
├── .env                     # Environment configuration
└── README.md               # This file
```

## Quick Start

### Prerequisites
- Python 3.8+
- Gmail account for sending climate alerts
- WeatherAPI.com account for temperature data

### Installation

1. **Clone and setup**
   ```bash
   git clone <repository-url>
   cd too-hot
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment**
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` with your configuration:
   ```env
   # Email Configuration (Gmail)
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password
   
   # Weather API Configuration
   WEATHER_API_KEY=your-weather-api-key
   
   # Flask Configuration
   SECRET_KEY=your-secret-key-here
   FLASK_ENV=development
   ```

3. **Setup Gmail App Password**
   - Enable 2-factor authentication in Google Account
   - Generate App Password for this application
   - Use in `MAIL_PASSWORD` field

4. **Get Weather API Key**
   - Sign up at [WeatherAPI.com](https://www.weatherapi.com/)
   - Get free API key (1M requests/month)
   - Add to `WEATHER_API_KEY` field

### Running the Application

1. **Start the climate activism web interface**
   ```bash
   python app.py
   ```
   Visit `http://localhost:5000` to see the campaign

2. **Start automated climate monitoring** (separate terminal)
   ```bash
   python scheduler.py
   ```

## Web Interface Features

### Campaign Visual Design
- **Header**: "TOO HOT" in all caps with Arial Black font and letter spacing
- **Campaign Image**: Flashmob protest scene showing activists wearing t-shirts
- **T-Shirt Showcase**: Actual t-shirt design image with campaign messaging
- **Climate Focus**: All text emphasizes climate activism and data-driven action

### User Experience
- **Subscription Form**: Clean, prominent signup for climate alerts
- **Location Support**: Optional location field with auto-detection fallback
- **Visual Feedback**: Success/error messages for all interactions
- **Mobile Responsive**: Optimized for climate activists on the go

### Content Sections
1. **Hero Section**: "Climate Action Starts Here" with campaign explanation
2. **Features Grid**: Climate data tracking, action alerts, mobile activism
3. **T-Shirt Design**: Showcase of the "IT'S TOO HOT!" shirt with benefits
4. **Why This Matters**: Data-driven explanation of climate anomalies
5. **Subtle Unsubscribe**: Small grey link at bottom for easy opt-out

## API Endpoints

### Climate Activism API
- `GET /` - Main climate campaign web interface
- `POST /api/subscribe` - Join the climate movement
- `POST /api/unsubscribe` - Leave the movement
- `GET /api/check-temperatures` - Manual climate anomaly check
- `GET /api/subscribers` - List climate activists (admin)

### Example API Usage
```bash
# Join the climate movement
curl -X POST http://localhost:5000/api/subscribe \
  -H "Content-Type: application/json" \
  -d '{"email": "activist@example.com", "location": "New York, NY"}'

# Check for climate anomalies
curl http://localhost:5000/api/check-temperatures

# List climate activists
curl http://localhost:5000/api/subscribers
```

## Climate Alert System

### How It Works
1. **Data Collection**: Fetches current temperature from WeatherAPI.com
2. **Historical Comparison**: Compares with average temperature for that date
3. **Anomaly Detection**: Identifies when temperature is 10°F+ hotter than average
4. **Activist Notification**: Sends climate action emails to subscribers
5. **Campaign Messaging**: Encourages wearing "IT'S TOO HOT!" shirts

### Email Notifications
- **Subject**: "Climate Action Alert: It's Too Hot!"
- **Content**: Temperature data, anomaly explanation, action suggestions
- **Call-to-Action**: Wear t-shirt, share on social media, start conversations
- **Climate Focus**: Emphasizes data-driven activism and community impact

## iPhone App Roadmap

### Phase 1: Core Mobile App
**Objective**: Create native iOS app with basic climate alert functionality

#### Technical Stack
- **Framework**: SwiftUI for modern iOS development
- **Backend Integration**: RESTful API calls to existing Flask backend
- **Push Notifications**: Apple Push Notification Service (APNs)
- **Data Storage**: Core Data for local subscriber management

#### Core Features
1. **User Onboarding**
   - Email registration with location auto-detection
   - Permission requests for notifications and location
   - Campaign introduction and t-shirt showcase

2. **Climate Alert System**
   - Push notifications for temperature anomalies
   - In-app climate data dashboard
   - Historical anomaly tracking

3. **Location Services**
   - GPS-based location detection
   - Manual location override
   - Multiple location support for activists

4. **Campaign Integration**
   - T-shirt design showcase
   - Social media sharing tools
   - Climate action suggestions

#### Development Tasks
- [ ] Set up iOS project with SwiftUI
- [ ] Implement API client for Flask backend
- [ ] Design app icon and launch screen
- [ ] Create user registration flow
- [ ] Implement push notification system
- [ ] Build climate data dashboard
- [ ] Add location services integration
- [ ] Design campaign visual elements

### Phase 2: Production & Launch
**Objective**: Prepare for App Store launch and public release

#### Launch Preparation
1. **App Store Optimization**
   - App Store listing and screenshots
   - Privacy policy and terms of service
   - App review preparation

2. **Backend Scaling**
   - Database migration from in-memory to persistent storage
   - API rate limiting and security
   - Production deployment setup

3. **Testing & Quality Assurance**
   - Comprehensive testing across iOS devices
   - Beta testing with climate activists
   - Performance optimization

4. **Marketing & Launch**
   - Climate activist community outreach
   - Social media campaign coordination
   - Press release and media outreach

#### Development Tasks
- [ ] Complete App Store submission
- [ ] Implement production backend
- [ ] Conduct comprehensive testing
- [ ] Prepare launch marketing materials
- [ ] Coordinate with climate activist communities

### Additional Feature Ideas

These features could be considered for future development after the core app is launched:

#### Enhanced Activism Features
1. **Community Features**
   - Local climate activist groups
   - Event coordination for t-shirt days
   - Climate action photo sharing

2. **Advanced Notifications**
   - Customizable alert preferences
   - Multiple notification types (immediate, daily digest, periodic summaries)
   - Weather forecast integration

3. **Climate Education**
   - Educational content about climate change
   - Historical temperature data visualization
   - Climate science explanations

4. **Social Integration**
   - Direct social media posting
   - Campaign hashtag tracking
   - Activist network building

#### Advanced Features
1. **Climate Analytics**
   - Personal climate impact tracking
   - Local climate trend analysis
   - Anomaly frequency statistics

2. **Activism Tools**
   - Climate action planning
   - Event organization tools
   - Campaign coordination features

3. **Data Visualization**
   - Interactive climate charts
   - Historical temperature graphs
   - Anomaly pattern analysis

4. **Offline Capabilities**
   - Offline climate data access
   - Local notification scheduling
   - Data synchronization when online

### Technical Architecture for iPhone App

#### Frontend (iOS)
```
ClimateApp/
├── Views/
│   ├── OnboardingView.swift
│   ├── DashboardView.swift
│   ├── AlertDetailView.swift
│   ├── SettingsView.swift
│   └── CampaignView.swift
├── Models/
│   ├── ClimateData.swift
│   ├── UserProfile.swift
│   └── NotificationSettings.swift
├── Services/
│   ├── APIClient.swift
│   ├── NotificationService.swift
│   └── LocationService.swift
└── Utilities/
    ├── Constants.swift
    └── Extensions.swift
```

#### Backend Integration
- **API Endpoints**: Extend existing Flask API for mobile features
- **Push Notifications**: Implement APNs integration
- **Data Synchronization**: Real-time updates between app and backend
- **Security**: JWT authentication for mobile users

#### Data Flow
1. **User Registration**: App → Flask API → Email verification
2. **Location Detection**: GPS → API → Climate data retrieval
3. **Alert System**: Backend scheduler → Push notification → App
4. **Data Sync**: App ↔ API ↔ Database

## Testing

### Web Interface Testing
```bash
# Run comprehensive tests
python test_app.py

# Test individual endpoints
curl -X POST http://localhost:5000/api/subscribe \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "location": "New York"}'

curl http://localhost:5000/api/check-temperatures
```

### iPhone App Testing Strategy
- **Unit Tests**: Core functionality and API integration
- **Integration Tests**: End-to-end user flows
- **UI Tests**: Automated interface testing
- **Beta Testing**: Climate activist community feedback

## Deployment

### Web Application
```bash
# Production deployment
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Automated climate monitoring
0 * * * * cd /path/to/too-hot && python scheduler.py
```

### iPhone App Deployment
- **Development**: TestFlight for beta testing
- **Production**: App Store submission and review
- **Backend**: Cloud deployment (AWS/Google Cloud)
- **Monitoring**: Analytics and crash reporting

## Contributing

1. Fork the repository
2. Create a feature branch for climate activism improvements
3. Make your changes with climate focus
4. Add tests for new functionality
5. Submit a pull request with detailed description

## License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0).

## Support

For issues and questions:
- Create an issue in the repository
- Check the logs in `temperature_alerts.log`
- Verify your environment configuration
- Contact the climate activist community

---

**Climate Action Note**: This application is designed to raise awareness about climate change through data-driven activism. The "IT'S TOO HOT!" campaign encourages wearing t-shirts on days when temperatures are 10°F+ hotter than historical averages to start conversations about climate action and global warming.
