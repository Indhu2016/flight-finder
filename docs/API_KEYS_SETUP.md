# 🔑 API Keys Setup Guide

This guide explains how to obtain API keys for the Smart Travel Optimizer project.

## 📋 Overview

The Smart Travel Optimizer supports three providers:
1. **Amadeus** - Flight and travel data (Real API)
2. **Omio** - Train and bus booking (Real API)  
3. **Mock Provider** - Sample data for testing (No API key needed)

---

## 🛫 Amadeus Travel API

Amadeus provides comprehensive flight, hotel, and travel data APIs.

### Step 1: Create Developer Account
1. Go to [Amadeus for Developers](https://developers.amadeus.com/)
2. Click "Register" or "Sign Up"
3. Fill in your details:
   - Email address
   - Password
   - Company/Organization name
   - Country
   - Use case description

### Step 2: Verify Email
1. Check your email for verification link
2. Click the verification link
3. Complete profile setup

### Step 3: Create Application
1. Log into Amadeus Developer Portal
2. Go to "My Apps" or "Applications"
3. Click "Create New App"
4. Fill in application details:
   - **App Name**: "Smart Travel Optimizer"
   - **Description**: "AI-powered travel route optimization"
   - **Callback URL**: `http://localhost:8501` (for Streamlit)

### Step 4: Get API Credentials
1. After creating the app, you'll see:
   - **API Key** (Client ID)
   - **API Secret** (Client Secret)
2. Copy these values to your `.env` file:
   ```bash
   AMADEUS_API_KEY=your_api_key_here
   AMADEUS_API_SECRET=your_api_secret_here
   ```

### Step 5: API Endpoints Used
- **Flight Offers Search**: `/v2/shopping/flight-offers`
- **Flight Inspiration**: `/v1/shopping/flight-destinations`
- **Airport & City Search**: `/v1/reference-data`

### Rate Limits
- **Test Environment**: 10 transactions/second, 1000/month
- **Production**: Higher limits available with paid plans

---

## 🚂 Omio API

Omio provides train, bus, and multimodal transport data.

### Step 1: Developer Registration
1. Visit [Omio Partner Portal](https://www.omio.com/partners)
2. Look for "API Access" or "Developer Program"
3. Fill out the partnership application form:
   - Company details
   - Integration use case
   - Expected volume
   - Technical contact information

### Step 2: API Access Request
1. Omio typically requires business verification
2. Describe your use case:
   ```
   "Smart Travel Optimizer - AI-powered route optimization system
   that helps users find optimal travel routes combining multiple
   transport modes including trains and buses."
   ```
3. Wait for approval (can take 1-2 weeks)

### Step 3: Get API Key
1. Once approved, you'll receive:
   - **API Key**
   - **API Documentation**
   - **Base URL** (usually `https://api.omio.com`)
2. Add to your `.env` file:
   ```bash
   OMIO_API_KEY=your_omio_api_key_here
   ```

### Step 4: API Endpoints
- **Search Routes**: `/v1/search`
- **Route Details**: `/v1/routes/{id}`
- **Stations/Stops**: `/v1/stations`

### Rate Limits
- Varies by partnership agreement
- Typically 100-1000 requests per hour

---

## 🧪 Mock Provider (No API Key Needed)

The Mock Provider uses sample data for testing and development.

### Features
- **No Registration Required**
- **Instant Setup**
- **Sample Routes** from `data/sample_routes.json`
- **Perfect for Development**

### Sample Data Included
```json
{
  "origin": "Stuttgart",
  "destination": "Vienna", 
  "mode": "flight",
  "airline": "Austrian Airlines",
  "price_eur": 180,
  "total_hours": 1.25,
  "connections": 0,
  "baggage": {
    "checked_bags": 2,
    "per_bag_kg": 23
  }
}
```

---

## 🔧 Configuration Setup

### 1. Copy Environment Template
```bash
cp .env.example .env
```

### 2. Edit Your `.env` File
```bash
# Email (SMTP) - For Gmail, use App Password
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_gmail_app_password
SMTP_FROM_NAME=Smart Travel Optimizer

# Amadeus API (Optional)
AMADEUS_API_KEY=your_amadeus_api_key
AMADEUS_API_SECRET=your_amadeus_api_secret

# Omio API (Optional)
OMIO_API_KEY=your_omio_api_key

# Security Settings
RATE_LIMIT_REQUESTS_PER_MINUTE=60
MAX_EMAIL_SIZE_KB=1024
```

### 3. Gmail App Password Setup
1. Enable 2-Factor Authentication on Gmail
2. Go to Google Account Settings
3. Security → 2-Step Verification → App Passwords
4. Generate password for "Smart Travel Optimizer"
5. Use this password in `SMTP_PASSWORD`

---

## 🧪 Testing Your Setup

### 1. Test Mock Provider (Always Works)
```bash
python main.py --origin "Stuttgart" --destination "Vienna" --date "2025-10-01"
```

### 2. Test with API Keys
```bash
# Set environment variables
export AMADEUS_API_KEY="your_key"
export AMADEUS_API_SECRET="your_secret"

# Run application
python main.py --origin "Paris" --destination "London" --date "2025-12-01"
```

### 3. Check Configuration
```bash
python -c "
from src.config import USE_AMADEUS, USE_OMIO
print(f'Amadeus: {USE_AMADEUS}')
print(f'Omio: {USE_OMIO}')
"
```

---

## 🚨 Security Best Practices

### ✅ DO
- Keep API keys in `.env` file (never commit to git)
- Use environment variables in production
- Rotate keys regularly
- Monitor API usage
- Set up rate limiting
- Use HTTPS only

### ❌ DON'T
- Commit API keys to version control
- Share keys in plain text
- Use production keys in development
- Ignore rate limits
- Store keys in code files

---

## 📊 Cost Estimates

### Amadeus
- **Free Tier**: 1000 requests/month
- **Paid Plans**: $0.01-0.10 per request
- **Enterprise**: Custom pricing

### Omio
- **Partnership Based**: Negotiate rates
- **Typical Range**: $0.01-0.05 per search

### Development Recommendation
1. Start with **Mock Provider** (Free)
2. Add **Amadeus** for flight data (Free tier)
3. Contact **Omio** for train/bus data (Business partnership)

---

## 🐛 Troubleshooting

### Common Issues

#### 1. "Invalid API Key"
- Check key format (no extra spaces)
- Verify key is active in provider portal
- Ensure using correct environment (test vs production)

#### 2. "Rate Limit Exceeded"
- Implement exponential backoff
- Check your usage limits
- Consider caching responses

#### 3. "Authentication Failed"
- For Amadeus: Both API key AND secret required
- Check token generation logic
- Verify OAuth flow if required

#### 4. "No Results Returned"
- Check route availability for your dates
- Verify city/airport codes
- Try broader search parameters

### Debug Commands
```bash
# Check environment variables
env | grep -E "(AMADEUS|OMIO|SMTP)"

# Test API connectivity
curl -H "Authorization: Bearer $TOKEN" https://api.amadeus.com/v1/security/oauth2/token

# Check application logs
tail -f logs/app.log
```

---

## 📞 Support

### Amadeus Support
- **Documentation**: https://developers.amadeus.com/docs
- **Community**: https://developers.amadeus.com/community
- **Support**: developer-support@amadeus.com

### Omio Support
- **Partnership**: partners@omio.com
- **Technical**: api-support@omio.com

### Project Support
- **GitHub Issues**: https://github.com/Indhu2016/flight-finder/issues
- **Email**: your-email@domain.com

---

*Last Updated: September 26, 2025*
