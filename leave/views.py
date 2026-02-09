from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db import transaction

from accounts.models import Role
from accounts.perms import role_required
from .models import LeaveRequest, LeaveStatus
from .forms import LeaveRequestForm

@login_required
def my_leaves(request):
    leaves = LeaveRequest.objects.filter(user=request.user)
    return render(request, "leave/my_leaves.html", {"leaves": leaves})

@login_required
def new_leave(request):
    if request.method=="POST":
        form=LeaveRequestForm(request.POST, request.FILES)
        if form.is_valid():
            lr=form.save(commit=False)
            lr.user=request.user
            lr.status=LeaveStatus.SUBMITTED
            lr.save()
            messages.success(request,"Wniosek urlopowy wysłany.")
            return redirect("my_leaves")
    else:
        form=LeaveRequestForm()
    return render(request,"leave/new_leave.html",{"form":form})

@login_required
@role_required(Role.PRZELOZONY, Role.ADMIN)
def leaves_to_approve(request):
    qs=LeaveRequest.objects.filter(status=LeaveStatus.SUBMITTED).select_related("user")
    if request.user.profile.role==Role.PRZELOZONY:
        qs=qs.filter(user__profile__supervisor=request.user)
    return render(request,"leave/to_approve.html",{"leaves":qs})

@login_required
@role_required(Role.PRZELOZONY, Role.ADMIN)
@transaction.atomic
def approve_leave(request, leave_id:int):
    l=get_object_or_404(LeaveRequest,id=leave_id)
    if request.method!="POST":
        return redirect("leaves_to_approve")
    if request.user.profile.role==Role.PRZELOZONY and l.user.profile.supervisor_id!=request.user.id:
        messages.error(request,"Brak uprawnień.")
        return redirect("leaves_to_approve")
    l.status=LeaveStatus.APPROVED
    l.decided_at=timezone.now()
    l.decided_by=request.user
    l.manager_note=(request.POST.get("note") or "").strip()
    l.save()
    messages.success(request,"Wniosek zaakceptowany.")
    return redirect("leaves_to_approve")

@login_required
@role_required(Role.PRZELOZONY, Role.ADMIN)
@transaction.atomic
def reject_leave(request, leave_id:int):
    l=get_object_or_404(LeaveRequest,id=leave_id)
    if request.method!="POST":
        return redirect("leaves_to_approve")
    if request.user.profile.role==Role.PRZELOZONY and l.user.profile.supervisor_id!=request.user.id:
        messages.error(request,"Brak uprawnień.")
        return redirect("leaves_to_approve")
    note=(request.POST.get("note") or "").strip()
    if not note:
        messages.error(request,"Podaj powód odrzucenia.")
        return redirect("leaves_to_approve")
    l.status=LeaveStatus.REJECTED
    l.decided_at=timezone.now()
    l.decided_by=request.user
    l.manager_note=note
    l.save()
    messages.success(request,"Wniosek odrzucony.")
    return redirect("leaves_to_approve")
