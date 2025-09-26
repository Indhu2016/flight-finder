# 🚀 Smart Travel Optimizer - Windows Setup Script
# PowerShell script to help you set up API keys and test the application

param(
    [switch]$Force = $false
)

# Colors for output
$Red = "Red"
$Green = "Green"  
$Yellow = "Yellow"
$Blue = "Cyan"

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Get-SecureInput {
    param(
        [string]$Prompt,
        [string]$Default = "",
        [switch]$AsSecureString = $false
    )
    
    if ($AsSecureString) {
        $input = Read-Host -Prompt $Prompt -AsSecureString
        return [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($input))
    } else {
        if ($Default) {
            $input = Read-Host -Prompt "$Prompt (default: $Default)"
        } else {
            $input = Read-Host -Prompt $Prompt
        }
        if ([string]::IsNullOrEmpty($input) -and $Default) {
            return $Default
        }
        return $input
    }
}

Clear-Host
Write-ColorOutput "🛫 Smart Travel Optimizer - API Keys Setup" $Blue
Write-ColorOutput "==========================================" $Blue
Write-Host ""

# Check if .env exists
if (Test-Path ".env") {
    if ($Force) {
        Write-ColorOutput "⚠️  Overwriting existing .env file..." $Yellow
        Copy-Item ".env" ".env.backup" -Force
    } else {
        Write-ColorOutput "⚠️  .env file already exists. Use -Force to overwrite." $Yellow
        Write-ColorOutput "   Backing up to .env.backup" $Yellow
        Copy-Item ".env" ".env.backup" -Force
    }
} else {
    Write-ColorOutput "✅ Creating new .env file from template" $Green
    Copy-Item ".env.example" ".env" -Force
}

Write-Host ""
Write-ColorOutput "📋 Let's set up your API keys step by step..." $Blue
Write-Host ""

# 1. SMTP Configuration
Write-ColorOutput "1. 📧 Email Configuration (for sending results)" $Yellow
Write-ColorOutput "   You can skip this if you don't want email functionality" $Blue
Write-Host ""

$smtpHost = Get-SecureInput "SMTP Host" "smtp.gmail.com"
$smtpPort = Get-SecureInput "SMTP Port" "587"
$smtpUsername = Get-SecureInput "SMTP Username (your email)"
$smtpPassword = Get-SecureInput "SMTP Password (Gmail App Password)" -AsSecureString
$smtpFromName = Get-SecureInput "From Name" "Smart Travel Optimizer"

# 2. Amadeus Configuration
Write-Host ""
Write-ColorOutput "2. 🛫 Amadeus API (Flight Data)" $Yellow
Write-ColorOutput "   Visit: https://developers.amadeus.com/" $Blue
Write-ColorOutput "   Create account → Create App → Get API Key & Secret" $Blue
Write-Host ""

$hasAmadeus = Read-Host "Do you have Amadeus API credentials? (y/N)"
if ($hasAmadeus -match "^[Yy]") {
    $amadeusKey = Get-SecureInput "Amadeus API Key"
    $amadeusSecret = Get-SecureInput "Amadeus API Secret" -AsSecureString
} else {
    Write-ColorOutput "ℹ️  Skipping Amadeus - you can add this later" $Blue
    $amadeusKey = ""
    $amadeusSecret = ""
}

# 3. Omio Configuration
Write-Host ""
Write-ColorOutput "3. 🚂 Omio API (Train/Bus Data)" $Yellow
Write-ColorOutput "   Visit: https://www.omio.com/partners" $Blue
Write-ColorOutput "   Apply for partnership → Get API Key" $Blue
Write-Host ""

$hasOmio = Read-Host "Do you have Omio API credentials? (y/N)"
if ($hasOmio -match "^[Yy]") {
    $omioKey = Get-SecureInput "Omio API Key"
} else {
    Write-ColorOutput "ℹ️  Skipping Omio - you can add this later" $Blue
    $omioKey = ""
}

# 4. Write to .env file
Write-Host ""
Write-ColorOutput "💾 Writing configuration to .env file..." $Green

$envContent = @"
# ============================================================================
# Smart Travel Optimizer - Environment Configuration
# Generated on $(Get-Date)
# ============================================================================

# Email (SMTP) Configuration
SMTP_HOST=$smtpHost
SMTP_PORT=$smtpPort
SMTP_USERNAME=$smtpUsername
SMTP_PASSWORD=$smtpPassword
SMTP_FROM_NAME=$smtpFromName

# Travel API Providers
AMADEUS_API_KEY=$amadeusKey
AMADEUS_API_SECRET=$amadeusSecret
OMIO_API_KEY=$omioKey

# Security Settings
RATE_LIMIT_REQUESTS_PER_MINUTE=60
MAX_EMAIL_SIZE_KB=1024

# Application Settings
LOG_LEVEL=INFO
DEBUG=false
"@

$envContent | Out-File -FilePath ".env" -Encoding UTF8
Write-ColorOutput "✅ Configuration saved to .env" $Green

# 5. Test configuration
Write-Host ""
Write-ColorOutput "🧪 Testing configuration..." $Yellow

# Check Python
try {
    $pythonVersion = python --version 2>$null
    Write-ColorOutput "✅ Python found: $pythonVersion" $Green
} catch {
    Write-ColorOutput "❌ Python not found. Please install Python 3.8+" $Red
    exit 1
}

# Check virtual environment
if (!(Test-Path ".venv")) {
    Write-ColorOutput "📦 Creating Python virtual environment..." $Blue
    python -m venv .venv
}

# Activate virtual environment
Write-ColorOutput "🔧 Activating virtual environment..." $Blue
if (Test-Path ".venv\Scripts\Activate.ps1") {
    & .venv\Scripts\Activate.ps1
} else {
    Write-ColorOutput "⚠️  Virtual environment activation script not found" $Yellow
}

# Install dependencies
Write-ColorOutput "📦 Installing dependencies..." $Blue
pip install -q -r requirements.txt

# Test configuration
Write-ColorOutput "🔍 Testing application configuration..." $Blue
$testResult = python -c @"
try:
    from src.config import USE_AMADEUS, USE_OMIO
    print(f'✅ Configuration loaded successfully')
    print(f'   - Amadeus: {"Enabled" if USE_AMADEUS else "Disabled"}')
    print(f'   - Omio: {"Enabled" if USE_OMIO else "Disabled"}')
    print(f'   - Mock Provider: Always Available')
except Exception as e:
    print(f'❌ Configuration error: {e}')
    import sys
    sys.exit(1)
"@

if ($LASTEXITCODE -eq 0) {
    Write-Host $testResult
} else {
    Write-ColorOutput "❌ Configuration test failed" $Red
}

# Test mock provider
Write-ColorOutput "🧪 Running test query with Mock Provider..." $Blue
$mockTest = python -c @"
try:
    from src.agents.route_agent import plan_best_routes
    results = plan_best_routes('Stuttgart', 'Vienna', '2025-10-01')
    if results:
        print(f'✅ Mock Provider test successful - Found {len(results)} routes')
        carrier = results[0].get('airline', results[0].get('carrier', 'Unknown'))
        print(f'   Best option: {results[0]["mode"].title()} via {carrier} - €{results[0]["price_eur"]}')
    else:
        print('⚠️  Mock Provider returned no results - check sample data')
except Exception as e:
    print(f'❌ Test failed: {e}')
"@

Write-Host $mockTest

Write-Host ""
Write-ColorOutput "🎉 Setup Complete!" $Green
Write-Host ""
Write-ColorOutput "📋 Next Steps:" $Blue
Write-Host ""
Write-Host "1. 🧪 Test the CLI application:"
Write-Host "   python main.py --origin `"Stuttgart`" --destination `"Vienna`" --date `"2025-10-01`""
Write-Host ""
Write-Host "2. 🌐 Start the web interface:"
Write-Host "   streamlit run streamlit_app.py"
Write-Host ""
Write-Host "3. 📖 Read the documentation:"
Write-Host "   - API Keys: docs\API_KEYS_SETUP.md"
Write-Host "   - README: README.md"
Write-Host ""
Write-Host "4. 🔑 To add more API keys later:"
Write-Host "   - Edit .env file directly"
Write-Host "   - Or run this script again with -Force"
Write-Host ""

if ($amadeusKey -or $omioKey) {
    Write-ColorOutput "🔐 Security Reminder:" $Yellow
    Write-Host "   - Never commit your .env file to version control"
    Write-Host "   - Keep your API keys secure and rotate them regularly"
    Write-Host "   - Monitor your API usage to avoid unexpected charges"
    Write-Host ""
}

Write-ColorOutput "Happy travels! ✈️🚂🚌" $Green

# Keep window open
Write-Host ""
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
