# InternGenius Setup Script for Windows PowerShell
# Run this script to automatically set up your development environment

Write-Host "🚀 InternGenius Setup Script for Windows" -ForegroundColor Green
Write-Host "=" * 50
Write-Host "This script will set up your InternGenius development environment" -ForegroundColor Yellow
Write-Host ""

# Function to print colored output
function Write-Step {
    param($Message)
    Write-Host "`n🔧 $Message" -ForegroundColor Cyan
    Write-Host ("-" * 50) -ForegroundColor Gray
}

function Write-Success {
    param($Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Error {
    param($Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Info {
    param($Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Yellow
}

# Check if running in correct directory
if (-not (Test-Path "app.py")) {
    Write-Error "app.py not found. Please run this script from the InternGenius root directory"
    exit 1
}

# Step 1: Check Python version
Write-Step "Checking Python version"
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python 3\.([8-9]|\d{2,})") {
        Write-Success "Python $($pythonVersion) detected"
    } else {
        Write-Error "Python 3.8+ required. Current version: $pythonVersion"
        Write-Info "Please install Python 3.8+ from https://python.org"
        exit 1
    }
} catch {
    Write-Error "Python not found. Please install Python 3.8+ from https://python.org"
    exit 1
}

# Step 2: Create virtual environment
Write-Step "Creating virtual environment"
try {
    python -m venv venv
    Write-Success "Virtual environment created successfully"
} catch {
    Write-Error "Failed to create virtual environment"
    exit 1
}

# Step 3: Activate virtual environment and install requirements
Write-Step "Activating virtual environment and installing packages"
try {
    & "venv\Scripts\Activate.ps1"
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    Write-Success "All packages installed successfully"
} catch {
    Write-Error "Failed to install requirements"
    Write-Info "Make sure requirements.txt exists and contains valid package names"
    exit 1
}

# Step 4: Setup environment file
Write-Step "Setting up environment configuration"
if (Test-Path ".env") {
    Write-Info ".env file already exists, skipping..."
} elseif (Test-Path ".env.example") {
    Copy-Item ".env.example" ".env"
    Write-Success "Environment file created from template"
    Write-Info "⚠️  Please edit .env file with your configuration:"
    Write-Info "   - MongoDB connection string"
    Write-Info "   - Secret keys"
    Write-Info "   - Email settings (optional)"
} else {
    Write-Error ".env.example template not found"
    exit 1
}

# Step 5: Generate secret key and update .env
Write-Step "Generating secure secret keys"
try {
    $secretKey = [System.Web.Security.Membership]::GeneratePassword(32, 8)
    $envContent = Get-Content ".env" -Raw
    $envContent = $envContent -replace "interngenius-super-secret-key-change-in-production", $secretKey
    Set-Content ".env" $envContent
    Write-Success "Secret keys generated and updated"
} catch {
    Write-Info "Could not auto-generate secret key. Please update SECRET_KEY in .env manually"
}

# Step 6: Create necessary directories
Write-Step "Creating application directories"
$directories = @(
    "logs",
    "static\uploads", 
    "ml_module\models",
    "data\temp"
)

foreach ($dir in $directories) {
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
}
Write-Success "All directories created"

# Step 7: Check MongoDB
Write-Step "Checking MongoDB connection"
try {
    # Try to check if MongoDB service is running
    $mongoService = Get-Service -Name "MongoDB" -ErrorAction SilentlyContinue
    if ($mongoService -and $mongoService.Status -eq "Running") {
        Write-Success "MongoDB service is running"
    } else {
        Write-Info "MongoDB service not detected or not running"
        Write-Info "Options:"
        Write-Info "1. Install MongoDB Community Server"
        Write-Info "2. Use MongoDB Atlas (cloud) - recommended"
        Write-Info "3. Start MongoDB service if already installed"
    }
} catch {
    Write-Info "Could not check MongoDB status"
    Write-Info "Please ensure MongoDB is installed and running"
}

# Setup completion
Write-Host "`n" + ("=" * 50)
Write-Success "🎉 Setup completed successfully!"
Write-Info "Next steps:"
Write-Info "1. Edit .env file with your MongoDB connection string"
Write-Info "2. Ensure MongoDB is running (or use MongoDB Atlas)"
Write-Info "3. Run the application with: python run.py"
Write-Host ""

# Ask if user wants to start the application
$startApp = Read-Host "Would you like to start the application now? (y/n)"
if ($startApp -eq "y" -or $startApp -eq "yes") {
    Write-Step "Starting Flask application"
    Write-Info "Starting InternGenius application..."
    Write-Info "Access the application at: http://127.0.0.1:5000"
    Write-Info "Press Ctrl+C to stop the application"
    
    try {
        python run.py
    } catch {
        Write-Error "Failed to start application"
        Write-Info "Please check your configuration and try running 'python run.py' manually"
    }
} else {
    Write-Info "Setup complete. Run 'python run.py' when ready to start the application."
}

Write-Host "`nThank you for using InternGenius! 🎓💼" -ForegroundColor Green
