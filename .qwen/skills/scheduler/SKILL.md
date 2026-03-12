---
name: scheduler
description: |
  Schedule recurring AI Employee tasks using cron (Linux/Mac) or 
  Task Scheduler (Windows). Automate daily briefings, weekly audits,
  and periodic watcher operations.
---

# Scheduler

Schedule recurring tasks for AI Employee.

## Overview

This skill provides scripts and configurations for scheduling:

- Daily CEO Briefings (8 AM)
- Weekly Business Audits (Sunday night)
- Continuous watcher monitoring
- Periodic orchestrator runs

## Usage

### Windows Task Scheduler

#### 1. Daily Briefing at 8 AM

```powershell
# Create scheduled task
$action = New-ScheduledTaskAction -Execute "python" `
  -Argument "scripts\orchestrator.py --vault D:\AI_Employee_Vault"
$trigger = New-ScheduledTaskTrigger -Daily -At 8am
Register-ScheduledTask -TaskName "AI_Employee_Daily_Briefing" `
  -Action $action -Trigger $trigger -Description "Generate daily CEO briefing"
```

#### 2. Weekly Audit (Sunday 10 PM)

```powershell
$action = New-ScheduledTaskAction -Execute "python" `
  -Argument "scripts\orchestrator.py --vault D:\AI_Employee_Vault --weekly-audit"
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 10pm
Register-ScheduledTask -TaskName "AI_Employee_Weekly_Audit" `
  -Action $action -Trigger $trigger
```

#### 3. Continuous Watcher (Every 5 minutes)

```powershell
$action = New-ScheduledTaskAction -Execute "python" `
  -Argument "scripts\filesystem_watcher.py --vault D:\AI_Employee_Vault --continuous"
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) `
  -RepetitionInterval (New-TimeSpan -Minutes 5)
Register-ScheduledTask -TaskName "AI_Employee_Watcher" `
  -Action $action -Trigger $trigger
```

### Linux/Mac cron

#### 1. Daily Briefing at 8 AM

```bash
# Edit crontab
crontab -e

# Add line:
0 8 * * * cd /path/to/vault && python scripts/orchestrator.py --vault /path/to/vault
```

#### 2. Weekly Audit (Sunday 10 PM)

```bash
0 22 * * 0 cd /path/to/vault && python scripts/orchestrator.py --weekly-audit
```

#### 3. Continuous Watcher (Every 5 minutes)

```bash
*/5 * * * * cd /path/to/vault && python scripts/filesystem_watcher.py --continuous
```

## Scheduled Task Templates

### Daily CEO Briefing

Generates morning briefing with:
- Pending tasks summary
- Yesterday's completions
- Today's priorities

```bash
# Command
python scripts/orchestrator.py --vault /path/to/vault --daily-briefing
```

### Weekly Business Audit

Generates weekly report with:
- Revenue summary
- Task completion rate
- Bottleneck analysis
- Subscription audit

```bash
# Command
python scripts/orchestrator.py --vault /path/to/vault --weekly-audit
```

### Monthly Review

Generates monthly report with:
- MTD revenue vs goal
- Top accomplishments
- Areas for improvement
- Next month goals

```bash
# Command
python scripts/orchestrator.py --vault /path/to/vault --monthly-review
```

## Task Scheduler GUI (Windows)

1. Open **Task Scheduler** (search in Start menu)
2. Click **Create Basic Task**
3. Name: `AI Employee - Daily Briefing`
4. Trigger: `Daily` at `8:00 AM`
5. Action: `Start a program`
6. Program: `python.exe`
7. Arguments: `scripts\orchestrator.py --vault D:\AI_Employee_Vault`
8. Start in: `D:\AI_Employee_Vault`

## Verification

### Check Scheduled Tasks (Windows)

```powershell
# List all AI Employee tasks
Get-ScheduledTask -TaskName "AI_Employee_*"

# Check last run result
Get-ScheduledTask -TaskName "AI_Employee_Daily_Briefing" | 
  Get-ScheduledTaskInfo
```

### Check cron Jobs (Linux/Mac)

```bash
# List all cron jobs
crontab -l

# Check cron logs (Linux)
grep CRON /var/log/syslog
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Task doesn't run | Check user permissions |
| Python not found | Use full path to python.exe |
| Task fails silently | Check action logs |
| Wrong time zone | Verify system time zone |

## Best Practices

1. **Log everything** - Capture output to log files
2. **Set timeouts** - Prevent runaway tasks
3. **Error notifications** - Email on failure
4. **Regular review** - Check task history weekly
5. **Backup configs** - Export scheduled tasks

## Export/Import Tasks (Windows)

### Export

```powershell
Export-ScheduledTask -TaskName "AI_Employee_*" > ai_employee_tasks.xml
```

### Import

```powershell
Register-ScheduledTask -Xml (Get-Content ai_employee_tasks.xml | Out-String)
```

## Example: Complete Setup Script

```powershell
# setup_scheduled_tasks.ps1

$vault = "D:\AI_Employee_Vault"
$python = "C:\Python314\python.exe"

# Daily Briefing
$action = New-ScheduledTaskAction -Execute $python `
  -Argument "scripts\orchestrator.py --vault $vault --daily-briefing"
$trigger = New-ScheduledTaskTrigger -Daily -At 8am
Register-ScheduledTask -TaskName "AI_Employee_Daily_Briefing" `
  -Action $action -Trigger $trigger

# Weekly Audit
$action = New-ScheduledTaskAction -Execute $python `
  -Argument "scripts\orchestrator.py --vault $vault --weekly-audit"
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 10pm
Register-ScheduledTask -TaskName "AI_Employee_Weekly_Audit" `
  -Action $action -Trigger $trigger

Write-Host "Scheduled tasks created successfully!"
```
