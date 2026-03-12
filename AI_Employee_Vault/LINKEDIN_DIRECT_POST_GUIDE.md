# LinkedIn Direct Post - Quick Guide

## 🚀 SINGLE COMMAND TO POST

```bash
python linkedin_auto_poster.py --vault .. --direct-post "Your post content here #hashtags"
```

### Example

```bash
python linkedin_auto_poster.py --vault .. --direct-post "My test auto post from AI Employee Hackathon! Local-first agents rock. #PanaversityHackathon #AI2026"
```

---

## 📋 What Happens

1. **Checks session** - Verifies you're logged in to LinkedIn
2. **Opens browser** - Launches Chromium with your saved session
3. **Navigates to LinkedIn** - Goes to your feed
4. **Clicks "Start a post"** - Opens the post composer
5. **Types your content** - With human-like delays (30-100ms per chunk)
6. **Clicks "Post"** - Submits the post
7. **Waits for confirmation** - Looks for "Posted" message
8. **Logs result** - Writes to `Logs/linkedin_posts.log`

**Total time:** ~30-45 seconds

---

## ✅ Success Output

```
======================================================================
DIRECT LINKEDIN POST (No Approval)
======================================================================

Content:
My test auto post from AI Employee Hackathon! Local-first agents rock. #PanaversityHackathon #AI2026

----------------------------------------------------------------------
Checking session...
✓ Session valid

Posting to LinkedIn...

======================================================================
✓ DIRECT POST SUCCESSFUL!
  Message: Post submitted

Check your LinkedIn: https://www.linkedin.com/feed/
Logs: Logs/linkedin_posts.log
======================================================================
```

---

## ❌ Error Handling

### Session Expired

```
✗ Session EXPIRED - Run --setup-session first
```

**Fix:**
```bash
python linkedin_auto_poster.py --setup-session --vault ..
```

### Post Failed

```
✗ DIRECT POST FAILED
  Error: Timeout during posting
```

**Troubleshooting:**
1. Check session: `python linkedin_auto_poster.py --check-session --vault ..`
2. Re-setup session: `python linkedin_auto_poster.py --setup-session --vault ..`
3. Check logs: `Logs/linkedin_*.log`

---

## 📝 Logging

All direct posts are logged to `Logs/linkedin_posts.log`:

```
[2026-03-01T14:30:00] ATTEMPT | Content: My test auto post from AI... | SUCCESS | Posted to LinkedIn
[2026-03-01T14:35:00] ATTEMPT | Content: Another test post... | FAILED | Session expired
```

---

## 🔧 Technical Details

### Selectors Used (2026 LinkedIn UI)

**Post Trigger:**
- `button:has-text("Start a post")`
- `button:has-text("Start")`
- `.share-box-feed-entry__trigger`
- `[data-testid="post-modal-trigger"]`
- `[aria-label="Create a post"]`
- Fallback: `page.get_by_role("button", name="Start a post")`

**Text Input:**
- `[contenteditable="true"][role="textbox"]`
- `div[aria-label="What do you want to talk about?"]`
- `[aria-label="What do you want to talk about?"]`
- Fallback: `page.get_by_role("textbox", name="What do you want to talk about?")`

**Post Button:**
- `button:has-text("Post")`
- `button:has-text("Post now")`
- `[data-control-name="compose-submit"]`
- Fallback: `page.get_by_role("button", name="Post")`

### Human-Like Delays

- Page load: 5 seconds
- After clicking post button: 3 seconds
- Typing delay: 30-100ms per 10 characters
- Between chunks: 50-200ms
- Before submitting: 2 seconds
- After submitting: 6 seconds

### Retry Logic

- Session check before posting
- Auto-recovery if session expired
- Multiple selector fallbacks
- Graceful error handling

---

## ⚠️ Safety Notes

1. **One post per run** - Limited to prevent spam
2. **Session required** - Must run `--setup-session` first
3. **Rate limits** - LinkedIn allows ~15 posts/day
4. **Human-like delays** - Avoids detection as bot
5. **Logs everything** - Full audit trail in `Logs/linkedin_posts.log`

---

## 🎯 Testing Workflow

```bash
# 1. Setup session (one-time)
python linkedin_auto_poster.py --setup-session --vault ..

# 2. Verify session
python linkedin_auto_poster.py --check-session --vault ..

# 3. Post test content
python linkedin_auto_poster.py --vault .. --direct-post "Test post from AI Employee! #Test #AI"

# 4. Check LinkedIn
# Open: https://www.linkedin.com/feed/

# 5. Check logs
type Logs\linkedin_posts.log
```

---

## 📚 Related Commands

| Command | Purpose |
|---------|---------|
| `--setup-session` | First-time LinkedIn login |
| `--check-session` | Verify session is valid |
| `--direct-post "text"` | **Post immediately** |
| `--create-draft "text"` | Create draft for approval |
| `--post-approved` | Post from Approved folder |
| `--clear-session` | Clear session data |

---

*Direct Post Feature - LinkedIn Auto Poster v0.3*
*AI Employee Hackathon 0 - Silver Tier*
