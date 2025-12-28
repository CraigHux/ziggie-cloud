# Authentication User Guide
## Ziggie Control Center

**Version:** 1.0.0
**Last Updated:** 2025-11-10
**Target Audience:** End Users, System Administrators

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Logging In](#logging-in)
3. [Managing Your Account](#managing-your-account)
4. [Password Management](#password-management)
5. [User Roles and Permissions](#user-roles-and-permissions)
6. [Troubleshooting](#troubleshooting)
7. [Security Best Practices](#security-best-practices)
8. [FAQ](#faq)

---

## Getting Started

### What is Authentication?

Authentication is the process of verifying your identity to access the Ziggie Control Center. It ensures that only authorized users can access the system and protects sensitive operations from unauthorized access.

### Default Credentials

When the system is first initialized, an admin account is automatically created:

| Field | Value |
|-------|-------|
| **Username** | `admin` |
| **Password** | `admin123` |

**IMPORTANT:** The default password must be changed immediately upon first login for security reasons.

### System Requirements

- Modern web browser (Chrome, Firefox, Safari, Edge)
- JavaScript enabled
- Stable internet connection
- Access to http://localhost:3001 (local development) or your deployment URL

---

## Logging In

### Step 1: Access the Login Page

1. Open your web browser
2. Navigate to the Control Center URL:
   - **Local Development:** http://localhost:3001
   - **Production:** https://your-domain.com/control-center

### Step 2: Enter Your Credentials

![Login Page](login-page.png)

The login page displays:
- **Username field** - Enter your assigned username
- **Password field** - Enter your password
- **Show Password toggle** - Click the eye icon to reveal/hide your password
- **Sign In button** - Click to authenticate

### Step 3: Submit Login Form

1. Type your username in the Username field
2. Type your password in the Password field
3. (Optional) Click the eye icon to verify your password is correct
4. Click the **Sign In** button
5. Wait for the system to authenticate your credentials

### Step 4: Successful Login

Upon successful authentication:
- You will be redirected to the Control Center dashboard
- A JWT token will be generated and stored locally
- Your user profile will be loaded

### What If Login Fails?

If login fails, you will see an error message:

| Error Message | Meaning | Solution |
|---------------|---------|----------|
| "Incorrect username or password" | Either username or password is wrong | Check your credentials and try again |
| "User account is inactive" | Your account has been deactivated by admin | Contact your system administrator |
| "Not authenticated" | Session has expired | Login again with your credentials |

---

## Managing Your Account

### Accessing Your Profile

Once logged in, click the **user avatar** in the top-right corner of the Navbar:

![User Menu](user-menu.png)

From the user menu you can:
- View your current user information
- Update your profile settings
- Change your password
- Log out

### Viewing Current User Information

1. Click the user avatar (top-right corner)
2. Select "View Profile" or "My Account"
3. Review your current information:
   - Username
   - Email address
   - Full name
   - User role
   - Account status (Active/Inactive)
   - Last login time

### Updating Your Profile

1. Click the user avatar → "Edit Profile"
2. Update the following fields (if available):
   - **Email:** Your email address for notifications
   - **Full Name:** Your display name in the system
3. Click **Save Changes**
4. Confirmation message will appear

---

## Password Management

### Changing Your Password

To change your password as a logged-in user:

1. Click the user avatar (top-right corner)
2. Select **"Change Password"**
3. Enter the required information:
   - **Current Password:** Your existing password
   - **New Password:** Your new password (minimum 6 characters)
   - **Confirm New Password:** Re-enter the new password to confirm
4. Click **Change Password**
5. You will see a confirmation message

### Password Requirements

- **Minimum Length:** 6 characters (3 recommended for security)
- **Characters:** Can include letters, numbers, and special characters
- **Uniqueness:** Cannot be the same as previous password
- **Recommendations:**
  - Use a mix of uppercase and lowercase letters
  - Include numbers and special characters (!@#$%^&*)
  - Avoid personal information (birthdays, names)
  - Avoid dictionary words

### Resetting a Forgotten Password

If you forget your password, contact your system administrator:

**For Administrators:** To reset a user's password:
```bash
# Use the password reset utility script
python reset_admin_password.py
```

**For End Users:** Contact your administrator with:
- Your username
- Your email address
- A form of ID verification

The administrator will:
1. Verify your identity
2. Reset your password to a temporary value
3. Provide you the temporary password via secure channel
4. You must change this password on first login

---

## User Roles and Permissions

### Role Overview

The Control Center uses three role levels:

#### Admin Role
- **Full system access**
- **User management capabilities**
- **System configuration**
- **Can:**
  - Create, update, and delete users
  - View system statistics and logs
  - Configure system settings
  - Access all features
  - Assign roles to other users
- **Use Case:** System administrators, DevOps engineers

#### User Role
- **Standard access to Control Center features**
- **Read/write permissions on resources**
- **Cannot:**
  - Create or delete other users
  - Modify system configuration
  - Access admin-only features
- **Use Case:** Operators, developers, team members

#### Readonly Role
- **Read-only access to resources**
- **Monitoring and auditing**
- **Cannot:**
  - Make any modifications
  - Create or update resources
  - Delete any content
- **Use Case:** Auditors, managers, observers

### Understanding Your Permissions

When you attempt to access a feature:

1. **Feature Available:** You have the required role
2. **Feature Grayed Out:** Your role lacks permissions
3. **Access Denied Error:** You attempted to access a restricted feature

To request additional permissions:
- Contact your system administrator
- Provide a business justification
- Administrator will update your role

---

## Troubleshooting

### Common Login Issues

#### Issue: "Incorrect username or password"

**Possible Causes:**
- Typo in username
- Wrong password
- Caps Lock is on
- Username/password changed by administrator

**Solutions:**
1. Verify Caps Lock is off
2. Double-check username spelling
3. Reset your password (contact admin)
4. Verify you're using the correct login URL

#### Issue: "User account is inactive"

**Cause:** Your account has been disabled by an administrator

**Solutions:**
1. Contact your system administrator
2. Provide your username
3. Request account reactivation
4. Administrator will enable your account

#### Issue: "Not authenticated" or "Session Expired"

**Cause:** Your authentication token has expired (24-hour expiration)

**Solutions:**
1. Log out and log back in
2. Or: Refresh the page and re-enter credentials
3. Close browser tab and navigate to login URL again

#### Issue: "Invalid authentication token"

**Cause:** Token is malformed or corrupted

**Solutions:**
1. Clear browser cache and localStorage:
   - Press F12 to open Developer Tools
   - Go to "Application" or "Storage" tab
   - Clear "Local Storage"
2. Log out and log in again
3. Try a different browser

### Recovering from Session Loss

**If you lose your session (get logged out):**

1. You will be automatically redirected to the login page
2. You will see the message: "Your session has expired"
3. Log in again with your credentials
4. Your previous work state may not be saved

**Prevention Tips:**
- Keep your session active by using the system regularly
- Log in again if you see the login page unexpectedly
- Don't share your login credentials

### Browser Compatibility Issues

| Browser | Support | Notes |
|---------|---------|-------|
| **Chrome/Chromium** | Full | Recommended, fully tested |
| **Firefox** | Full | Fully tested |
| **Safari** | Full | Fully tested |
| **Edge** | Full | Fully tested |
| **IE 11** | Not Supported | Use modern browser instead |

---

## Security Best Practices

### Personal Account Security

#### 1. Protect Your Credentials
- Never share your username or password
- Never use the same password as other systems
- Never write down your password
- Never type your password in front of others

#### 2. Logout When Done
- Always log out when leaving the computer
- Click the user avatar → **Logout**
- Close the browser tab
- Don't rely on session timeout

#### 3. Secure Password Management
- Use a password manager (Bitwarden, 1Password, KeePass)
- Generate strong, unique passwords
- Change password immediately if you suspect compromise
- Update password at least annually

#### 4. Recognize Phishing Attempts
- Never click suspicious links in emails
- Verify sender email addresses
- Control Center will never ask for your password via email
- Type the URL directly instead of clicking links

#### 5. Secure Your Device
- Keep your operating system updated
- Use antivirus software
- Enable disk encryption
- Lock your computer when away

### During Your Session

- **Monitor activities:** Review what you're accessing
- **Verify URLs:** Ensure you're on the correct domain
- **Use HTTPS:** Always use secure connections (https://)
- **Avoid public WiFi:** Don't access Control Center on public networks
- **Enable browser warnings:** Allow your browser to warn about suspicious sites

### Reporting Security Issues

If you suspect a security issue:

1. **Do not ignore it**
2. **Contact your system administrator immediately**
3. **Change your password**
4. **Provide details:**
   - What happened
   - When it occurred
   - What you were doing
   - Any unusual activity

---

## FAQ

### Q: How long does my login session last?

**A:** Your authentication token expires after 24 hours. You will need to log in again. Sessions are automatically invalidated when:
- Token expires (24 hours)
- You explicitly log out
- You close the browser
- You clear browser data/cookies

### Q: What if I forget my username?

**A:** Contact your system administrator with:
- Your email address
- Any previous usernames you remember
- Your full name

Your administrator can look up your username or create a new account.

### Q: Can I use the same password for multiple accounts?

**A:** No, not recommended. Each system should have a unique password. If your Ziggie password is compromised, other systems remain secure.

### Q: How often should I change my password?

**A:** Best practices recommend:
- **Immediately:** When you suspect compromise
- **Upon initial login:** Change the default password
- **Annually:** At minimum
- **Never:** Has password requirements enforcement

### Q: What if my device is lost or stolen?

**A:** Immediately:
1. Contact your system administrator
2. Request your account be deactivated
3. Administrator will log you out of all sessions
4. Request a new device setup

### Q: Can I have multiple login sessions?

**A:** Yes, you can log in from multiple devices/browsers simultaneously. However:
- Each session has independent tokens
- Logging out on one device doesn't log you out on others
- Each token can be used independently

### Q: Why does my password need to be at least 6 characters?

**A:** Minimum 6 characters is the standard. Recommended password practices:
- Use longer passwords (12+ characters)
- Use special characters
- Mix uppercase, lowercase, and numbers
- Avoid dictionary words

### Q: How does the "Show Password" toggle work?

**A:** The eye icon in the password field allows you to:
- Click once to **reveal password** (eye with slash disappears)
- Click again to **hide password** (eye with slash appears)
- Useful for verifying correct password entry
- Not recommended on public/shared devices

### Q: Can the administrator see my password?

**A:** No, passwords are hashed with bcrypt and cannot be retrieved. Administrators can:
- Reset your password to a temporary value
- Require you to change it on next login
- Cannot view your current password

### Q: What if I'm locked out?

**A:** Contact your system administrator and provide:
- Your username
- The error message you received
- Your email address for verification
- When you last successfully logged in

Administrator can:
- Reset your password
- Verify and reactivate your account
- Check logs for suspicious activity

---

## Additional Resources

### Documentation
- **Developer Guide:** See `AUTH_DEVELOPER_GUIDE.md` for technical details
- **API Documentation:** Available at `/api/docs` (admin access)
- **Swagger UI:** Available at `/api/swagger` for endpoint testing

### Support
- **Email:** support@example.com
- **Tickets:** Create an issue in the support system
- **Admin Contact:** [Your Admin Name/Email]

### Related Guides
- Password Reset Procedure
- Account Recovery Guide
- Multi-Device Login Guide
- Session Management Guide

---

## Document Information

**File:** `AUTH_USER_GUIDE.md`
**Location:** `C:\Ziggie\control-center\docs\`
**Version:** 1.0.0
**Last Updated:** 2025-11-10
**Status:** Published
**Maintainer:** L2 Documentation Agent

---

**Disclaimer:** This guide is for the Ziggie Control Center authentication system. Always follow your organization's security policies and procedures.
