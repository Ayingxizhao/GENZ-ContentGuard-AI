# API Usage Tracking Feature

## Overview

The API Usage Tracking feature provides users with **fine-grained, real-time visibility** into their API usage across both AI models (ContentGuard/HuggingFace and Gemini). This feature addresses the need for transparency in rate limiting and helps users manage their API consumption effectively.

## What It Does

### For Authenticated Users
- **Separate tracking** for HuggingFace (200 calls/day) and Gemini (10 calls/day) models
- **Real-time updates** via periodic polling (every 30 seconds)
- **Visual progress bars** with color-coded warnings (green → yellow → red)
- **Reset countdown timer** showing when daily limits will refresh
- **Lifetime usage statistics** showing total API calls across all time
- **Percentage-based indicators** for quick assessment of remaining quota

### For Anonymous Users
- **Visible usage banner** showing real-time IP-based limits
- **IP-based rate limiting** (100 calls/day for HuggingFace)
- **Cooldown tracking** for Gemini API requests with countdown
- **Progress bars** with color-coded warnings
- **Upgrade prompts** encouraging sign-up for higher limits
- **Dismissible banner** with localStorage persistence

## How It Works

### Backend Architecture

1. **Database Models** (`models.py`)
   - `User` model tracks separate counters for each model
   - Daily counters reset automatically at midnight UTC
   - Methods: `get_detailed_usage_stats()`, `get_usage_percentage()`, `get_seconds_until_reset()`

2. **API Endpoints** (`routes/usage.py`)
   - `GET /api/usage` - Returns comprehensive usage statistics
   - `GET /api/usage/summary` - Quick summary for UI headers
   - `GET /api/usage/history` - Lifetime usage data

3. **Middleware** (`middleware/rate_limit.py`, `middleware/gemini_rate_limit.py`)
   - Enforces rate limits before API calls
   - Increments usage counters after successful requests
   - Uses `db.session.refresh()` to ensure accurate counter reads

### Frontend Architecture

1. **UI Components** (`templates/index.html`)
   - **Authenticated Users**: Detailed usage panel in user dropdown menu
     - Separate sections for each model with progress bars
     - Reset timer with countdown display
     - Total lifetime usage badge
   - **Anonymous Users**: Usage banner above main content
     - HuggingFace usage with progress bar (0-100 calls)
     - Gemini cooldown status indicator
     - Prominent sign-up CTA buttons
     - Dismissible with close button

2. **JavaScript Logic** (`static/js/script.js`)
   - **Authenticated Functions**:
     - `fetchAndUpdateUsageStats()` - Fetches latest stats from API
     - `updateDetailedUsageDisplay()` - Updates UI with fresh data
     - `startUsageStatsPolling()` - Begins 30-second polling interval
     - `stopUsageStatsPolling()` - Stops polling on logout
   - **Anonymous Functions**:
     - `fetchAndUpdateAnonymousUsage()` - Fetches IP-based stats
     - `updateAnonymousUsageDisplay()` - Updates banner with stats
     - `showAnonymousUsageBanner()` - Shows banner (checks localStorage)
     - `hideAnonymousUsageBanner()` - Hides and remembers preference
   - Automatic refresh after each API call for both user types

3. **CSS Styling** (`static/css/style.css`)
   - Responsive design for mobile and desktop
   - Color-coded progress bars (green/yellow/red)
   - Dark mode support for both authenticated and anonymous UI
   - Smooth animations and transitions
   - Gradient backgrounds for anonymous banner
   - Hover effects on CTA buttons

## Usage

### For Users

#### Authenticated Users

1. **View Usage Stats**
   - Click on your profile avatar in the top-right corner
   - Usage panel displays automatically with:
     - ContentGuard Model usage (0-200 calls)
     - Gemini Model usage (0-10 calls)
     - Time until reset
     - Total lifetime calls

2. **Monitor Limits**
   - Progress bars change color as you approach limits:
     - **Green**: 0-70% used
     - **Yellow**: 70-90% used
     - **Red**: 90-100% used

3. **Reset Time**
   - Daily limits reset at midnight UTC
   - Countdown timer shows exact time remaining

#### Anonymous Users

1. **View Usage Banner**
   - Banner appears automatically above the analysis form
   - Shows your IP-based usage:
     - ContentGuard Model: X/100 calls used
     - Gemini Model: Cooldown status
   - Progress bar indicates remaining quota

2. **Dismiss Banner**
   - Click the X button to close the banner
   - Preference is saved in browser localStorage
   - Banner won't show again until you clear browser data

3. **Upgrade to Higher Limits**
   - Click "Sign Up Free" for 200 HF + 10 Gemini calls/day
   - Or "Sign In" if you already have an account

### For Developers

#### Fetch Usage Stats Programmatically

```javascript
// Fetch current user's usage stats
const response = await fetch('/api/usage');
const data = await response.json();

if (data.authenticated) {
    console.log('HuggingFace:', data.stats.huggingface);
    console.log('Gemini:', data.stats.gemini);
    console.log('Reset in:', data.stats.seconds_until_reset, 'seconds');
}
```

#### Response Format

```json
{
  "authenticated": true,
  "stats": {
    "user_id": 123,
    "email": "user@example.com",
    "huggingface": {
      "calls_today": 45,
      "daily_limit": 200,
      "remaining": 155,
      "total_calls": 1234,
      "percentage_used": 22.5,
      "last_call": "2025-10-25T14:30:00Z"
    },
    "gemini": {
      "calls_today": 3,
      "daily_limit": 10,
      "remaining": 7,
      "total_calls": 89,
      "percentage_used": 30.0,
      "last_call": "2025-10-25T13:15:00Z"
    },
    "reset_time": "2025-10-26T00:00:00Z",
    "seconds_until_reset": 34200,
    "has_exceeded_hf_limit": false,
    "has_exceeded_gemini_limit": false
  }
}
```

## Technical Implementation Details

### Database Schema Updates

No schema changes required - uses existing columns:
- `api_calls_today`, `api_calls_count`, `last_api_call`, `daily_limit`
- `gemini_calls_today`, `gemini_calls_count`, `last_gemini_call`, `gemini_daily_limit`

### Key Design Decisions

1. **Polling vs WebSockets**: Chose polling (30s interval) for simplicity and reliability
2. **Client-side timer**: Reset countdown calculated on client to reduce server load
3. **Separate endpoints**: `/api/usage` for detailed stats, `/auth/usage` for backward compatibility
4. **Refresh after commit**: Added `db.session.refresh(user)` to fix stale counter bug
5. **Color-coded warnings**: Visual feedback at 70% and 90% thresholds

### Performance Considerations

- Polling interval: 30 seconds (balance between freshness and server load)
- Lightweight API responses (~500 bytes)
- Client-side caching of user object
- Automatic cleanup of expired anonymous user entries

## Troubleshooting

### Usage Counter Not Updating

**Problem**: Counter shows old values after API call

**Solution**: 
- Ensure `db.session.refresh(user)` is called after `db.session.commit()`
- Check browser console for JavaScript errors
- Verify polling is active (should see requests every 30s in Network tab)

### Reset Timer Shows Wrong Time

**Problem**: Timer doesn't match expected reset time

**Solution**:
- Server uses UTC time - ensure timezone conversion if needed
- Check `get_reset_time()` method returns correct datetime
- Verify `seconds_until_reset` calculation in backend

### Progress Bar Not Changing Color

**Problem**: Bar stays green even at high usage

**Solution**:
- Check CSS classes `.warning` and `.danger` are applied
- Verify `percentage_used` calculation is correct
- Inspect element to confirm class names

## Future Enhancements

Potential improvements for future iterations:
- Historical usage graphs (daily/weekly/monthly trends)
- Email notifications when approaching limits
- Custom limit tiers for premium users
- Export usage data as CSV
- Usage analytics dashboard
- WebSocket support for instant updates

## Related Files

- `/Users/yingxizhao/Desktop/Research/genzLang/routes/usage.py` - API endpoints
- `/Users/yingxizhao/Desktop/Research/genzLang/models.py` - Database models
- `/Users/yingxizhao/Desktop/Research/genzLang/templates/index.html` - UI components
- `/Users/yingxizhao/Desktop/Research/genzLang/static/js/script.js` - Frontend logic
- `/Users/yingxizhao/Desktop/Research/genzLang/static/css/style.css` - Styling
- `/Users/yingxizhao/Desktop/Research/genzLang/middleware/rate_limit.py` - HF rate limiting
- `/Users/yingxizhao/Desktop/Research/genzLang/middleware/gemini_rate_limit.py` - Gemini rate limiting

## Testing

### Manual Testing Steps

1. **Test authenticated user flow**:
   - Sign in to the application
   - Open user dropdown to view usage panel
   - Make an API call (analyze content)
   - Verify counters increment immediately
   - Wait 30 seconds and verify polling updates

2. **Test progress bar colors**:
   - Use 70% of daily limit → should show yellow
   - Use 90% of daily limit → should show red

3. **Test reset timer**:
   - Verify countdown decreases every second
   - Check format is HH:MM:SS

4. **Test anonymous users**:
   - Log out
   - Make API calls
   - Verify IP-based limits are enforced

### Automated Testing

```python
# Example unit test for usage stats
def test_get_detailed_usage_stats(client, auth_user):
    response = client.get('/api/usage')
    data = response.get_json()
    
    assert response.status_code == 200
    assert data['authenticated'] == True
    assert 'huggingface' in data['stats']
    assert 'gemini' in data['stats']
    assert 'seconds_until_reset' in data['stats']
```

## Support

For issues or questions about the usage tracking feature:
1. Check this documentation first
2. Review browser console for errors
3. Check server logs for backend issues
4. File a bug report with reproduction steps
