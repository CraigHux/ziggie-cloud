# Quick Fix Guide: 403 Forbidden on /api/auth/me

## TL;DR

Your tokens are valid, but you're sending them with the wrong header format.

## The Fix (JavaScript/TypeScript)

### BEFORE (Wrong) ❌
```javascript
// Mistake 1: Storing "Bearer " with token
localStorage.setItem('token', 'Bearer eyJhbG...')

// Mistake 2: Sending token without "Bearer "
headers: { Authorization: token }

// Mistake 3: Using wrong header name
headers: { 'X-Auth-Token': token }
```

### AFTER (Correct) ✅
```javascript
// Step 1: Store token WITHOUT "Bearer " prefix
localStorage.setItem('token', response.data.access_token)

// Step 2: Add "Bearer " when making request
headers: {
  Authorization: `Bearer ${localStorage.getItem('token')}`
}
```

## Complete Working Example

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:54112'
});

// Add interceptor to automatically add Bearer token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Login
const response = await api.post('/api/auth/login', {
  username: 'admin',
  password: 'admin123'
});

// Store token (NO "Bearer " here!)
localStorage.setItem('token', response.data.access_token);

// Get user info (interceptor adds "Bearer " automatically)
const user = await api.get('/api/auth/me');
console.log(user.data);
```

## Test It

Run this in your browser console:

```javascript
// Check what's stored
console.log('Stored token:', localStorage.getItem('token'));

// If it starts with "Bearer ", you found the problem!
const token = localStorage.getItem('token');
if (token && token.startsWith('Bearer ')) {
  console.error('❌ Problem: Token stored with "Bearer " prefix');
  console.log('Fix: Remove "Bearer " from stored token');
  localStorage.setItem('token', token.replace('Bearer ', ''));
}

// Check what headers are being sent
// Look in DevTools → Network → Request Headers
```

## Verify in DevTools

1. Open DevTools (F12)
2. Go to Network tab
3. Make request to `/api/auth/me`
4. Click on request
5. Check Headers tab
6. Look for: `Authorization: Bearer eyJhbG...`

**Must have:**
- Header name: `Authorization` (not Authentication, not X-Auth-Token)
- Value format: `Bearer <token>` (with space after Bearer)
- Token should NOT start with "Bearer " itself

## Still Not Working?

Run these checks:

```javascript
// 1. Is token stored?
const token = localStorage.getItem('token');
console.log('Token exists:', !!token);

// 2. Is it valid format? (should be ~200 chars)
console.log('Token length:', token?.length);

// 3. Does it have 3 parts? (header.payload.signature)
console.log('Token parts:', token?.split('.').length); // Should be 3

// 4. Is it expired?
const payload = JSON.parse(atob(token.split('.')[1]));
const expiry = new Date(payload.exp * 1000);
console.log('Expires:', expiry);
console.log('Is expired:', expiry < new Date());

// 5. What user?
console.log('Username:', payload.sub);
console.log('User ID:', payload.user_id);
console.log('Role:', payload.role);
```

## Backend is Fine

The backend implementation is correct. No changes needed there.

## Questions?

Check the full investigation report: `JWT_AUTH_INVESTIGATION_REPORT.md`
