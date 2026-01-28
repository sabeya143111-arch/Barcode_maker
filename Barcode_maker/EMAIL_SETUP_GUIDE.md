# 📧 Email OTP Setup Guide - Swag Barcode Maker

## Quick Setup (5 Minutes)

### ✅ What You Need
- Gmail account (recommended)
- 5 minutes
- Access to Google Account settings

---

## 🚀 Step-by-Step Setup

### Step 1: Enable Gmail App Password

**Important:** Gmail requires "App Passwords" for third-party applications. Your regular Gmail password won't work.

1. **Go to Google Account Security**
   - Visit: https://myaccount.google.com/security
   - Login with your Gmail account

2. **Enable 2-Step Verification** (if not already enabled)
   - Click on "2-Step Verification"
   - Follow the setup wizard
   - This is required for App Passwords

3. **Generate App Password**
   - Visit: https://myaccount.google.com/apppasswords
   - Or search for "App Passwords" in your Google Account settings
   - Select:
     - **App**: Mail
     - **Device**: Other (Custom name) → Type: "Streamlit Barcode App"
   - Click **Generate**

4. **Copy the App Password**
   - You'll see a 16-character password like: `abcd efgh ijkl mnop`
   - **Copy this password** (you won't see it again)
   - Spaces don't matter - you can copy with or without them

---

### Step 2: Create Secrets File

**For Local Development:**

1. Navigate to your project folder:
   ```
   cd Barcode_maker/Barcode_maker/
   ```

2. Create `.streamlit` folder (if it doesn't exist):
   ```bash
   mkdir .streamlit
   ```

3. Create `secrets.toml` file inside `.streamlit/`:
   ```bash
   touch .streamlit/secrets.toml
   ```

4. Edit `secrets.toml` and add:
   ```toml
   # Email Configuration
   EMAIL_SENDER = "your-email@gmail.com"
   EMAIL_PASSWORD = "abcd efgh ijkl mnop"  # Your 16-char App Password
   
   # Optional (defaults already set in code)
   SMTP_SERVER = "smtp.gmail.com"
   SMTP_PORT = "587"
   ```

5. **Replace** `your-email@gmail.com` with your actual Gmail
6. **Replace** `abcd efgh ijkl mnop` with your actual App Password

---

### Step 3: Test the System

1. **Run the app:**
   ```bash
   streamlit run app.py
   ```

2. **Create Test Account:**
   - Go to "Signup" tab
   - Enter name, email, password
   - Click "Create Account"

3. **Test Login & OTP:**
   - Go to "Login" tab
   - Enter your credentials
   - Click "Send OTP"
   - Check your email (inbox and spam folder)
   - Enter the 6-digit OTP
   - Click "Verify OTP"

4. **Success Indicators:**
   - ✅ "OTP sent to your email!"
   - ✅ Email received within 5-30 seconds
   - ✅ "Login successful! Redirecting..."

---

## 🌐 Streamlit Cloud Deployment

If deploying to Streamlit Cloud:

1. Go to your app dashboard on Streamlit Cloud
2. Click on your app → **Settings**
3. Go to **Secrets** section
4. Paste your secrets (same format as `secrets.toml`):
   ```toml
   EMAIL_SENDER = "your-email@gmail.com"
   EMAIL_PASSWORD = "your-app-password"
   ```
5. Click **Save**
6. Restart your app

---

## ❌ Troubleshooting

### Error: "Email authentication failed"

**Causes:**
- Using regular Gmail password instead of App Password
- App Password copied incorrectly
- 2-Step Verification not enabled
- `secrets.toml` file not in correct location

**Solutions:**
1. Verify 2-Step Verification is ON
2. Generate a NEW App Password
3. Copy password carefully (ignore spaces)
4. Check file location: `Barcode_maker/Barcode_maker/.streamlit/secrets.toml`
5. Restart Streamlit app after adding secrets

### Email Not Received

**Check:**
- ✅ Spam/Junk folder
- ✅ Wait 30-60 seconds (sometimes delayed)
- ✅ Correct email address in secrets
- ✅ Gmail account has not hit sending limits

**Note:** If email fails, the app shows OTP in the UI as fallback (development mode)

### "SMTP Error: Connection refused"

**Solutions:**
- Check internet connection
- Verify SMTP_SERVER = "smtp.gmail.com"
- Verify SMTP_PORT = "587"
- Check if firewall is blocking port 587

---

## 🔒 Security Best Practices

1. **Never Commit Secrets**
   - Add `.streamlit/` to `.gitignore`
   - Never push `secrets.toml` to GitHub

2. **Use App Passwords**
   - Never use your actual Gmail password
   - App Passwords can be revoked anytime

3. **Rotate Credentials**
   - Change App Password every 3-6 months
   - Revoke old App Passwords from Google Account

4. **Limit Access**
   - Only share secrets with authorized team members
   - Use different secrets for dev/staging/production

---

## 📱 Alternative Email Providers

### Microsoft Outlook/Hotmail

```toml
EMAIL_SENDER = "your-email@outlook.com"
EMAIL_PASSWORD = "your-password"
SMTP_SERVER = "smtp.outlook.com"
SMTP_PORT = "587"
```

### SendGrid (Professional)

```toml
EMAIL_SENDER = "noreply@yourdomain.com"
EMAIL_PASSWORD = "your-sendgrid-api-key"
SMTP_SERVER = "smtp.sendgrid.net"
SMTP_PORT = "587"
```

**Benefits:**
- Higher sending limits
- Better deliverability
- Analytics & tracking
- Free tier: 100 emails/day

---

## 📊 Email Limits

**Gmail Free Account:**
- 500 emails/day
- 100 emails per batch
- Rate limit: ~1 email/second

**For High Volume:**
- Use SendGrid, Mailgun, or AWS SES
- Setup custom domain email
- Implement rate limiting in code

---

## ✅ Final Checklist

- [ ] 2-Step Verification enabled on Gmail
- [ ] App Password generated (16 characters)
- [ ] `.streamlit` folder created
- [ ] `secrets.toml` file created with correct values
- [ ] Secrets not committed to Git
- [ ] App tested with real email
- [ ] OTP received successfully
- [ ] Login works end-to-end

---

## 🆘 Still Need Help?

**Common Issues:**
1. Check file path: `Barcode_maker/Barcode_maker/.streamlit/secrets.toml`
2. Restart Streamlit after adding secrets
3. Check spam folder for OTP emails
4. Verify App Password (not regular password)
5. Try generating new App Password

**Contact:**
- GitHub Issues: https://github.com/sabeya143111-arch/Barcode_maker/issues
- Email: Tarjque143111@gmail.com

---

**Last Updated:** January 2026  
**Version:** 1.0  
**Tested with:** Python 3.8+, Streamlit 1.30+
