# Barcode Maker with OTP Authentication 🔐

A secure Streamlit-based barcode generator application with email OTP (One-Time Password) authentication.

## Features

- **Email OTP Authentication**: Secure signup and login system
- **Barcode Generation**: Create various types of barcodes
- **User Management**: Secure user registration and verification
- **Email Verification**: 6-digit OTP sent to user's email

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/sabeya143111-arch/Barcode_maker.git
cd Barcode_maker/Barcode_maker
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Email Settings

**Important**: You need to set up Gmail App Password for OTP emails to work.

#### Step 1: Generate Gmail App Password

1. Go to your Google Account: https://myaccount.google.com/
2. Navigate to Security → 2-Step Verification (enable if not already)
3. Go to App Passwords: https://myaccount.google.com/apppasswords
4. Select "Mail" and "Other (Custom name)"
5. Enter "Streamlit Barcode App" as the name
6. Copy the 16-character password

#### Step 2: Create Secrets File

1. Copy the template file:
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```

2. Edit `.streamlit/secrets.toml` and add your credentials:
   ```toml
   [email]
   SMTP_EMAIL = "your-email@gmail.com"
   SMTP_PASSWORD = "your-16-character-app-password"
   SMTP_SERVER = "smtp.gmail.com"
   SMTP_PORT = 587
   ```

**Note**: The `.streamlit/secrets.toml` file is in `.gitignore` and will NOT be committed to GitHub.

### 4. Run the Application

```bash
streamlit run app.py
```

### 5. First Time Use

1. Click on "Signup" tab
2. Enter your name, email, and create a password
3. Check your email for the 6-digit OTP
4. Enter the OTP to verify your account
5. Login with your credentials
6. Start generating barcodes!

## Project Structure

```
Barcode_maker/
├── .streamlit/
│   └── secrets.toml.example    # Template for email configuration
├── .gitignore                   # Protects secrets from being committed
├── assets/                      # Images and resources
├── app.py                       # Main application file
├── requirements.txt             # Python dependencies
├── EMAIL_SETUP_GUIDE.md        # Detailed email setup guide
└── README.md                    # This file
```

## Security Features

- ✅ Email-based OTP verification
- ✅ Secure password storage
- ✅ Session management
- ✅ Protected secrets file (not in version control)
- ✅ Gmail App Password (not regular password)

## Troubleshooting

### OTP Not Received?

1. Check spam/junk folder
2. Verify Gmail App Password is correct
3. Ensure 2-Step Verification is enabled on your Google Account
4. Check that SMTP settings in `secrets.toml` are correct

### Authentication Errors?

1. Make sure you're using App Password, not regular Gmail password
2. Regenerate App Password if needed
3. Check that email address matches the one in `secrets.toml`

For detailed troubleshooting, see [`EMAIL_SETUP_GUIDE.md`](Barcode_maker/EMAIL_SETUP_GUIDE.md)

## Support

For issues or questions, please open an issue on GitHub.

---

**Note**: Never commit your `secrets.toml` file to version control!
