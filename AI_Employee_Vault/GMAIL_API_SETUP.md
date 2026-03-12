# 🚨 Gmail API Setup - Quick Fix Required

**Issue:** Gmail API is not enabled in your Google Cloud project.

**Error:** `Gmail API has not been used in project 827151787194 before or it is disabled.`

---

## ✅ Quick Fix (5 Minutes)

### Step 1: Enable Gmail API

1. **Click this link:** https://console.developers.google.com/apis/api/gmail.googleapis.com/overview?project=827151787194

2. **Click "ENABLE" button**

3. **Wait 1-2 minutes** for the API to propagate

4. **Retry the watcher:**
   ```bash
   cd AI_Employee_Vault\scripts
   python gmail_watcher.py --vault .. --interval 60
   ```

---

## 📋 Full Setup (If You Need New Credentials)

### Option A: Use Existing Project (Recommended)

Your current project ID: **827151787194**

1. Go to: https://console.cloud.google.com/apis/dashboard?project=827151787194

2. Click **"ENABLE APIS AND SERVICES"**

3. Search for **"Gmail API"**

4. Click **"ENABLE"**

5. Wait 2-3 minutes

6. Test:
   ```bash
   python gmail_watcher.py --vault ..
   ```

### Option B: Create New Project

If the above doesn't work, create new credentials:

#### 1. Create New Project

1. Go to: https://console.cloud.google.com/

2. Click **"Select a project"** → **"NEW PROJECT"**

3. Name: `AI Employee Gmail`

4. Click **"CREATE"**

#### 2. Enable Gmail API

1. Go to: https://console.cloud.google.com/apis/library/gmail.googleapis.com

2. Select your project

3. Click **"ENABLE"**

#### 3. Create OAuth Credentials

1. Go to: https://console.cloud.google.com/apis/credentials

2. Click **"CREATE CREDENTIALS"** → **"OAuth client ID"**

3. **Configure consent screen** (if prompted):
   - User Type: **External**
   - App name: `AI Employee`
   - User support email: Your email
   - Developer contact: Your email
   - Click **"SAVE AND CONTINUE"**
   - Scopes: Skip (no need to add)
   - Test users: Click **"ADD USERS"** → Add your Gmail address
   - Click **"SAVE AND CONTINUE"**

4. **Create OAuth Client ID**:
   - Application type: **Web application**
   - Name: `AI Employee Gmail Watcher`
   - Authorized redirect URIs:
     - `http://localhost:8080`
     - `http://localhost:65329` (add multiple if needed)
   - Click **"CREATE"**

5. **Download JSON**:
   - Click **"DOWNLOAD JSON"**
   - Save as `credentials.json`
   - Copy to: `AI_Employee_Vault\scripts\credentials.json`

#### 4. Re-authenticate

```bash
cd AI_Employee_Vault\scripts

# Delete old token
del token.json

# Re-authenticate with new credentials
python gmail_watcher.py --authenticate --vault ..
```

---

## ✅ Verification

After enabling API, test:

```bash
cd AI_Employee_Vault\scripts

# Test connection
python gmail_watcher.py --vault ..

# Expected output:
# ============================================================
# Gmail Watcher - One-time Scan
# ============================================================
# Running scan...
# [OK] Found X email(s)
# [OK] Created: Needs_Action/GMAIL_xxx.md
```

---

## 🔧 Troubleshooting

### Problem: "accessNotConfigured"

**Solution:** Enable Gmail API (see Step 1 above)

### Problem: "credentials.json not found"

**Solution:** Download from Google Cloud Console → Credentials

### Problem: "Token expired"

**Solution:**
```bash
del token.json
python gmail_watcher.py --authenticate --vault ..
```

### Problem: "Quota exceeded"

**Solution:** Wait 24 hours or increase quota in Google Cloud Console

---

## 📞 Quick Links

| Purpose | Link |
|---------|------|
| Enable Gmail API | https://console.developers.google.com/apis/api/gmail.googleapis.com/overview?project=827151787194 |
| API Dashboard | https://console.cloud.google.com/apis/dashboard?project=827151787194 |
| Credentials | https://console.cloud.google.com/apis/credentials?project=827151787194 |
| Create New Project | https://console.cloud.google.com/ |

---

## ⏱️ Estimated Time

- **Enable API:** 2 minutes
- **Wait for propagation:** 2-5 minutes
- **Test:** 1 minute

**Total:** 5-10 minutes

---

*Gmail API Setup Guide*
*AI Employee Hackathon 0 - Silver Tier*
