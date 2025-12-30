# PowerShell script to push to GitHub
# Usage: .\push_to_github.ps1

Write-Host "========================================" -ForegroundColor Green
Write-Host "Push to GitHub - Fog AI Anomaly Detection" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Check if git is installed
try {
    $gitVersion = git --version
    Write-Host "Git found: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Git is not installed!" -ForegroundColor Red
    exit 1
}

# Check if we're in a git repository
if (-not (Test-Path .git)) {
    Write-Host "Error: Not a git repository. Run 'git init' first." -ForegroundColor Red
    exit 1
}

# Check if remote exists
$remoteExists = git remote get-url origin 2>$null
if ($remoteExists) {
    Write-Host "Remote 'origin' already exists: $remoteExists" -ForegroundColor Yellow
    $useExisting = Read-Host "Use existing remote? (y/n)"
    if ($useExisting -ne "y") {
        git remote remove origin
        $remoteExists = $null
    }
}

# If no remote, ask for GitHub URL
if (-not $remoteExists) {
    Write-Host ""
    Write-Host "Please provide your GitHub repository URL:" -ForegroundColor Cyan
    Write-Host "Example: https://github.com/USERNAME/fog-ai-anomaly-detection.git" -ForegroundColor Gray
    $githubUrl = Read-Host "GitHub URL"
    
    if ($githubUrl) {
        git remote add origin $githubUrl
        Write-Host "Remote 'origin' added: $githubUrl" -ForegroundColor Green
    } else {
        Write-Host "No URL provided. Exiting." -ForegroundColor Red
        exit 1
    }
}

# Check current branch
$currentBranch = git branch --show-current
Write-Host ""
Write-Host "Current branch: $currentBranch" -ForegroundColor Cyan

# Ask to rename to main if needed
if ($currentBranch -ne "main") {
    $rename = Read-Host "Rename branch to 'main'? (y/n)"
    if ($rename -eq "y") {
        git branch -M main
        Write-Host "Branch renamed to 'main'" -ForegroundColor Green
    }
}

# Push to GitHub
Write-Host ""
Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
Write-Host ""

try {
    git push -u origin main
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Success! Code pushed to GitHub" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "On Kali Linux, clone with:" -ForegroundColor Cyan
    Write-Host "  git clone $githubUrl" -ForegroundColor White
} catch {
    Write-Host ""
    Write-Host "Error pushing to GitHub!" -ForegroundColor Red
    Write-Host "Make sure:" -ForegroundColor Yellow
    Write-Host "  1. The repository exists on GitHub" -ForegroundColor Yellow
    Write-Host "  2. You have push permissions" -ForegroundColor Yellow
    Write-Host "  3. You're authenticated (use GitHub CLI or token)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "See GIT_SETUP.md for detailed instructions" -ForegroundColor Cyan
}

