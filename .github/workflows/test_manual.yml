name: Run Booking Bot

on:
  workflow_dispatch:
  schedule:
    - cron: "0 9 * * 1-5"   # Run at 9 AM Monday-Friday

jobs:
  booking:
    runs-on: ubuntu-latest

    env:
      EMAIL: ${{ secrets.EMAIL }}
      PASSWORD: ${{ secrets.PASSWORD }}

    steps:
      # --- STEP 1: Checkout Repository ---
      - name: Checkout repository
        uses: actions/checkout@v4

      # --- STEP 2: Set Up Python ---
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      # --- STEP 3: Install Dependencies ---
      - name: Install Python dependencies
        run: |
          python -m pip install --upgrade pip
          pip install selenium webdriver-manager chromedriver-autoinstaller

      # --- STEP 4: Install Chrome & ChromeDriver ---
      - name: Install Chrome and ChromeDriver
        run: |
          echo "[INFO] Installing Chrome..."
          sudo apt-get update
          sudo apt-get install -y wget unzip xvfb
          wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
          sudo apt install -y ./google-chrome-stable_current_amd64.deb || true

          echo "[INFO] Detecting Chrome version..."
          CHROME_VERSION=$(google-chrome --version | grep -oP '[0-9]+')
          echo "Detected Chrome major version: $CHROME_VERSION"

          echo "[INFO] Downloading matching ChromeDriver..."
          URL=$(curl -s https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json | \
                jq -r --arg v "$CHROME_VERSION" '.versions[] | select(.version | startswith($v+".")) | .downloads.chromedriver[] | select(.platform=="linux64") | .url' | head -n 1)
          if [ -z "$URL" ]; then
            echo "[ERROR] Failed to find ChromeDriver for version $CHROME_VERSION"
            exit 1
          fi
          wget -O chromedriver.zip "$URL"
          unzip chromedriver.zip
          sudo mv chromedriver-linux64/chromedriver /usr/local/bin/
          sudo chmod +x /usr/local/bin/chromedriver
          chromedriver --version

      # --- STEP 5: Debug Secrets (Mask Output) ---
      - name: Debug Secrets
        run: |
          if [ -z "$EMAIL" ]; then
            echo "::error::EMAIL is not set!"
            exit 1
          fi
          if [ -z "$PASSWORD" ]; then
            echo "::error::PASSWORD is not set!"
            exit 1
          fi
          echo "[DEBUG] EMAIL and PASSWORD are set (hidden)."

      # --- STEP 6: Run Booking Bot ---
      - name: Run booking bot
        run: |
          mkdir -p screenshots
          python booking_bot.py || echo "Booking bot failed."

      # --- STEP 7: Upload Screenshots ---
      - name: Upload screenshots
        uses: actions/upload-artifact@v4
        with:
          name: booking-screenshots
          path: screenshots/
          if-no-files-found: warn
