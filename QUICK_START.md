# 🚀 Quick Start Guide - API Keys

## TL;DR - Get Started in 5 Minutes

### Option 1: Use Mock Data (No API Keys Needed) ⚡
```bash
# 1. Copy environment template
cp .env.example .env

# 2. Install dependencies  
pip install -r requirements.txt

# 3. Run the application
python main.py --origin "Stuttgart" --destination "Vienna" --date "2025-10-01"
```

That's it! The Mock Provider will show you sample routes instantly.

---

### Option 2: Get Real Flight Data (15 minutes) ✈️

#### Step 1: Get Amadeus API Key (Free)
1. 🌐 Go to **https://developers.amadeus.com/**
2. 📝 Click **"Register"** 
3. ✅ Verify your email
4. ➕ Create new app: **"Smart Travel Optimizer"**
5. 📋 Copy your **API Key** and **API Secret**

#### Step 2: Configure Application
1. 📄 Copy `.env.example` to `.env`
2. ✏️ Edit `.env` file and add your keys:
   ```bash
   AMADEUS_API_KEY=your_api_key_here
   AMADEUS_API_SECRET=your_api_secret_here
   ```

#### Step 3: Test It
```bash
python main.py --origin "Paris" --destination "London" --date "2025-12-01"
```

---

### Option 3: Automated Setup (Windows) 🪟
```powershell
# Run the setup wizard
.\setup-api-keys.ps1
```

### Option 3: Automated Setup (Linux/Mac) 🐧🍎
```bash
# Run the setup wizard
./setup-api-keys.sh
```

---

## 🔑 API Key Sources

| Provider | Type | Cost | Setup Time | Link |
|----------|------|------|------------|------|
| **Mock** | Test Data | Free | 0 min | Built-in |
| **Amadeus** | Flights | Free tier | 5 min | [developers.amadeus.com](https://developers.amadeus.com/) |
| **Omio** | Trains/Bus | Partnership | 1-2 weeks | [omio.com/partners](https://www.omio.com/partners) |

---

## 🧪 Testing Your Setup

### Check Configuration
```bash
python -c "from src.config import USE_AMADEUS, USE_OMIO; print(f'Amadeus: {USE_AMADEUS}, Omio: {USE_OMIO}')"
```

### Test Providers
```bash
# Mock Provider (always works)
python main.py --origin "Stuttgart" --destination "Vienna" --date "2025-10-01"

# With real APIs (if configured)
python main.py --origin "New York" --destination "Los Angeles" --date "2025-11-15"
```

### Web Interface
```bash
streamlit run streamlit_app.py
```

Then open **http://localhost:8501** in your browser.

---

## 🆘 Need Help?

### Common Issues
- **"No API key"**: Use Mock Provider first, then add real APIs
- **"Rate limit"**: Wait a few minutes or check your API quota
- **"No results"**: Try different cities or dates

### Get Support
- 📖 **Full Guide**: `docs/API_KEYS_SETUP.md`
- 🐛 **Issues**: https://github.com/Indhu2016/flight-finder/issues
- 📧 **Email**: your-support-email@domain.com

---

**Happy travels!** ✈️🚂🚌
