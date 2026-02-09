from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from django.db import transaction

from accounts.models import Role
from accounts.perms import role_required
from .models import WorkSession, TimeEntry, Project, EntrySource, EntryStatus
from .forms import ManualEntryForm

def _today():
    return timezone.localdate()

@login_required
def my_entries(request):
    entries = TimeEntry.objects.filter(user=request.user).order_by("-date")
    return render(request, "time_tracking/my_entries.html", {"entries": entries})

@login_required
def today(request):
    t = _today()
    session = WorkSession.objects.filter(user=request.user).first()
    entry = TimeEntry.objects.filter(user=request.user, date=t).first()
    projects = Project.objects.filter(active=True).order_by("name")
    return render(request, "time_tracking/today.html", {"today": t, "session": session, "entry": entry, "projects": projects})

@login_required
@transaction.atomic
def rcp_start(request):
    if request.method != "POST":
        return redirect("today")
    if WorkSession.objects.filter(user=request.user).exists():
        messages.info(request, "Sesja już trwa.")
        return redirect("today")
    comment = (request.POST.get("comment") or "").strip()
    if len(comment) < 10:
        messages.error(request, "Komentarz jest wymagany (min. 10 znaków).")
        return redirect("today")
    project_id = request.POST.get("project") or None
    project = Project.objects.filter(id=project_id).first() if project_id else None
    WorkSession.objects.create(user=request.user, date=_today(), start_dt=timezone.now(), project=project, comment=comment)
    messages.success(request, "START zapisany.")
    return redirect("today")

@login_required
@transaction.atomic
def rcp_break_toggle(request):
    if request.method != "POST":
        return redirect("today")
    s = WorkSession.objects.filter(user=request.user).select_for_update().first()
    if not s:
        messages.error(request, "Brak aktywnej sesji.")
        return redirect("today")
    now = timezone.now()
    if s.break_start_dt is None:
        s.break_start_dt = now
        s.save(update_fields=["break_start_dt"])
        messages.success(request, "Przerwa rozpoczęta.")
    else:
        minutes = int((now - s.break_start_dt).total_seconds() // 60)
        s.break_minutes += max(0, minutes)
        s.break_start_dt = None
        s.save(update_fields=["break_minutes","break_start_dt"])
        messages.success(request, f"Przerwa zakończona (+{minutes} min).")
    return redirect("today")

@login_required
@transaction.atomic
def rcp_stop(request):
    if request.method != "POST":
        return redirect("today")
    s = WorkSession.objects.filter(user=request.user).select_for_update().first()
    if not s:
        messages.error(request, "Brak aktywnej sesji.")
        return redirect("today")
    now = timezone.now()
    if s.break_start_dt is not None:
        minutes = int((now - s.break_start_dt).total_seconds() // 60)
        s.break_minutes += max(0, minutes)
    start_local = timezone.localtime(s.start_dt).time().replace(second=0, microsecond=0)
    end_local = timezone.localtime(now).time().replace(second=0, microsecond=0)

    entry, _ = TimeEntry.objects.get_or_create(user=request.user, date=s.date, defaults={
        "source": EntrySource.RCP, "comment": s.comment, "project": s.project, "break_minutes": s.break_minutes, "status": EntryStatus.DRAFT
    })
    entry.start_time = start_local
    entry.end_time = end_local
    entry.break_minutes = s.break_minutes
    entry.comment = s.comment
    entry.project = s.project
    entry.source = EntrySource.RCP
    entry.save()
    s.delete()
    messages.success(request, "STOP zapisany. Wpis jest w szkicu — wyślij do akceptacji.")
    return redirect("today")

@login_required
def manual_entry(request):
    if request.method == "POST":
        form = ManualEntryForm(request.POST)
        if form.is_valid():
            e = form.save(commit=False)
            e.user = request.user
            e.source = EntrySource.MANUAL
            e.status = EntryStatus.DRAFT
            e.save()
            messages.success(request, "Wpis ręczny zapisany jako szkic.")
            return redirect("my_entries")
    else:
        form = ManualEntryForm()
    return render(request, "time_tracking/manual_entry.html", {"form": form})

@login_required
@transaction.atomic
def submit_entry(request, entry_id: int):
    e = get_object_or_404(TimeEntry, id=entry_id, user=request.user)
    if request.method != "POST":
        return redirect("my_entries")
    if e.status not in (EntryStatus.DRAFT, EntryStatus.REJECTED):
        messages.info(request, "Ten wpis nie może być ponownie wysłany.")
        return redirect("my_entries")
    if not e.comment or len(e.comment.strip()) < 10:
        messages.error(request, "Komentarz (nad czym pracowałeś/aś) jest wymagany.")
        return redirect("my_entries")
    e.status = EntryStatus.SUBMITTED
    e.submitted_at = timezone.now()
    e.manager_note = ""
    e.save(update_fields=["status","submitted_at","manager_note"])
    messages.success(request, "Wysłano do akceptacji.")
    return redirect("my_entries")

@login_required
@transaction.atomic
def delete_draft(request, entry_id: int):
    e = get_object_or_404(TimeEntry, id=entry_id, user=request.user)
    if request.method != "POST":
        return redirect("my_entries")
    if e.status != EntryStatus.DRAFT:
        messages.error(request, "Można usuwać tylko szkice.")
        return redirect("my_entries")
    e.delete()
    messages.success(request, "Szkic usunięty.")
    return redirect("my_entries")

@login_required
@role_required(Role.PRZELOZONY, Role.ADMIN)
def to_approve(request):
    qs = TimeEntry.objects.filter(status=EntryStatus.SUBMITTED).select_related("user","project")
    if request.user.profile.role == Role.PRZELOZONY:
        qs = qs.filter(user__profile__supervisor=request.user)
    return render(request, "time_tracking/to_approve.html", {"entries": qs.order_by("-date")})

@login_required
@role_required(Role.PRZELOZONY, Role.ADMIN)
@transaction.atomic
def approve_entry(request, entry_id: int):
    e = get_object_or_404(TimeEntry, id=entry_id)
    if request.method != "POST":
        return redirect("to_approve")
    if request.user.profile.role == Role.PRZELOZONY and e.user.profile.supervisor_id != request.user.id:
        messages.error(request, "Brak uprawnień do tego wpisu.")
        return redirect("to_approve")
    e.status = EntryStatus.APPROVED
    e.approved_at = timezone.now()
    e.approved_by = request.user
    e.manager_note = (request.POST.get("note") or "").strip()
    e.save(update_fields=["status","approved_at","approved_by","manager_note"])
    messages.success(request, "Wpis zaakceptowany.")
    return redirect("to_approve")

@login_required
@role_required(Role.PRZELOZONY, Role.ADMIN)
@transaction.atomic
def reject_entry(request, entry_id: int):
    e = get_object_or_404(TimeEntry, id=entry_id)
    if request.method != "POST":
        return redirect("to_approve")
    if request.user.profile.role == Role.PRZELOZONY and e.user.profile.supervisor_id != request.user.id:
        messages.error(request, "Brak uprawnień do tego wpisu.")
        return redirect("to_approve")
    note = (request.POST.get("note") or "").strip()
    if not note:
        messages.error(request, "Podaj powód odrzucenia.")
        return redirect("to_approve")
    e.status = EntryStatus.REJECTED
    e.manager_note = note
    e.approved_at = None
    e.approved_by = None
    e.save(update_fields=["status","manager_note","approved_at","approved_by"])
    messages.success(request, "Wpis odrzucony.")
    return redirect("to_approve")
