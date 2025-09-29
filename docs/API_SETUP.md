# 🔑 API Keys & Provider Setup Guide

## Overview

The Smart Travel Optimizer supports multiple travel data providers:
- **Mock Provider** ✅ No setup required (works immediately)
- **Amadeus API** 🛫 Flight data (5 minutes setup)  
- **Omio API** 🚂 Train & bus data (requires business partnership)

## 🚀 Quick Start (0 minutes)

**Want to test immediately?** No problem! The Mock provider works out of the box:

```bash
# Test with sample data (no API keys needed)
python main.py --origin "Stuttgart" --destination "Vienna" --date "2025-10-01"

# Or use the web interface
streamlit run streamlit_app.py
```

The Mock provider includes realistic sample data for routes like:
- Stuttgart ↔ Vienna (flight, train, bus)
- Berlin ↔ Paris  
- London ↔ Rome
- And more...

## 🛫 Amadeus API Setup (5 minutes)

For **real flight data**, get free Amadeus API keys:

### Step 1: Register
1. Go to [developers.amadeus.com](https://developers.amadeus.com/)
2. Click "Get Started" → Sign up for free
3. Verify your email

### Step 2: Create App
1. Go to "My Apps" section
2. Click "Create New App"
3. Fill in details:
   - **App Name**: "Smart Travel Optimizer"  
   - **Description**: "AI travel route optimization"

### Step 3: Get Keys
1. Once approved, copy your:
   - **API Key** (Client ID)
   - **API Secret** (Client Secret)

### Step 4: Configure
Add to your `.env` file:
```bash
AMADEUS_API_KEY=your_api_key_here
AMADEUS_API_SECRET=your_secret_here
```

### Free Tier Benefits
- ✅ 2,000 API calls/month
- ✅ Test environment with mock data
- ✅ All API endpoints available
- ✅ No credit card required

## 🚂 Omio API Setup (Business Partnership)

Omio provides train and bus data but requires business partnership approval:

### Requirements
- Legitimate business use case
- Professional website/application  
- Expected booking volume
- European route focus preferred

### Steps
1. Apply at [omio.com/affiliate](https://www.omio.com/affiliate)
2. Fill out business application
3. Wait 1-2 weeks for approval
4. Receive API key and documentation

### Alternative: Affiliate Program
If you don't qualify for API access, consider the [Omio Affiliate Program](https://www.omio.com/affiliate):
- Easier approval process
- Commission-based model
- Booking referrals instead of direct API

## 📧 Email Setup (2 minutes)

For email notifications, configure SMTP:

### Gmail Setup (Recommended)
1. **Enable 2FA** on your Gmail account
2. **Generate App Password**:
   - Google Account → Security → 2-Step Verification → App Passwords
   - Create app password for "Smart Travel Optimizer"
3. **Add to .env**:
   ```bash
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your_email@gmail.com
   SMTP_PASSWORD=your_app_password_here  # Use App Password, not regular password!
   ```

### Other Email Providers
- **Outlook**: smtp-mail.outlook.com:587
- **Yahoo**: smtp.mail.yahoo.com:587  
- **Custom SMTP**: Configure according to your provider

## 🧪 Testing Your Setup

Run the test script to verify everything works:

```bash
python test_api_keys.py
```

This will check:
- ✅ Environment configuration
- ✅ Mock provider (should always work)
- ✅ Amadeus API keys (if configured)
- ✅ Omio API keys (if configured)
- ✅ Email SMTP settings (if configured)

## 🔧 Configuration Scenarios

### Scenario 1: Development & Testing
```bash
# .env file - minimal setup
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587  
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Leave API keys empty - Mock provider will be used
AMADEUS_API_KEY=
AMADEUS_API_SECRET=
OMIO_API_KEY=
```

### Scenario 2: Real Flight Data
```bash
# .env file - with Amadeus
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com  
SMTP_PASSWORD=your_app_password

# Real flight data
AMADEUS_API_KEY=your_amadeus_key
AMADEUS_API_SECRET=your_amadeus_secret

# Still using Mock for train/bus
OMIO_API_KEY=
```

### Scenario 3: Full Production
```bash
# .env file - all providers
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# All providers configured
AMADEUS_API_KEY=your_amadeus_key
AMADEUS_API_SECRET=your_amadeus_secret
OMIO_API_KEY=your_omio_key
```

## 🔍 How Provider Selection Works

The app automatically uses available providers:

1. **Mock Provider**: Always available as fallback
2. **Amadeus**: Used if API keys are configured
3. **Omio**: Used if API key is configured

If multiple providers are available, results are merged and optimized.

## 🚨 Troubleshooting

### Mock Provider Issues
```bash
# Problem: No routes found
# Solution: Check data/sample_routes.json exists

# Problem: Application won't start  
# Solution: Install requirements: pip install -r requirements.txt
```

### Amadeus Issues
```bash
# Problem: 401 Unauthorized
# Solution: Check API key and secret are correct

# Problem: 429 Too Many Requests
# Solution: You've exceeded free tier (2000/month)

# Problem: No flight data returned
# Solution: Use test.api.amadeus.com for free tier
```

### Email Issues
```bash
# Problem: Authentication failed
# Solution: Use App Password, not regular Gmail password

# Problem: Connection timeout
# Solution: Check SMTP host and port settings
```

## 💡 Pro Tips

### Development
- Start with Mock provider for instant testing
- Add Amadeus for real flight data
- Keep Omio for later (requires approval)

### Production
- Use production Amadeus endpoints for real data
- Implement proper error handling
- Monitor API usage and costs
- Cache responses to reduce API calls

### Security
- Never commit `.env` files to git
- Use strong, unique API keys
- Rotate credentials regularly
- Enable 2FA on all accounts
- Monitor for unusual API usage

## 📞 Support

Need help getting API keys?

- **Amadeus**: [developers.amadeus.com/support](https://developers.amadeus.com/support)
- **Omio**: Contact through their affiliate program
- **Application Issues**: Check our [troubleshooting guide](API_KEYS_SETUP.py)

## 🎯 Next Steps

1. **Start Testing**: Use Mock provider immediately
2. **Get Real Data**: Register for Amadeus (5 minutes)
3. **Add Email**: Configure SMTP for notifications
4. **Scale Up**: Apply for Omio when ready for train/bus data

The app is designed to work great with any combination of providers! 🚀
