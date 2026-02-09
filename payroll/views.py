from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from datetime import date
import calendar
from decimal import Decimal

from accounts.models import Role
from accounts.perms import role_required
from django.contrib.auth.models import User
from time_tracking.models import TimeEntry, EntryStatus

def _month_range(year:int, month:int):
    last = calendar.monthrange(year, month)[1]
    return date(year, month, 1), date(year, month, last)

def _hours(entry: TimeEntry) -> Decimal:
    if not entry.start_time or not entry.end_time:
        return Decimal("0")
    s = entry.start_time.hour*60 + entry.start_time.minute
    e = entry.end_time.hour*60 + entry.end_time.minute
    minutes = max(0, e - s - int(entry.break_minutes or 0))
    return (Decimal(minutes)/Decimal(60)).quantize(Decimal("0.01"))

@login_required
@role_required(Role.ADMIN)
def payroll_report(request):
    today = timezone.localdate()
    year = int(request.GET.get("year", today.year))
    month = int(request.GET.get("month", today.month))
    start_d, end_d = _month_range(year, month)

    users = User.objects.select_related("profile").order_by("last_name","first_name","username")
    rows=[]
    total_pay=Decimal("0")

    for u in users:
        rate = u.profile.hourly_rate_pln or Decimal("0")
        mult = u.profile.overtime_multiplier or Decimal("1.50")
        entries = TimeEntry.objects.filter(user=u, status=EntryStatus.APPROVED, date__gte=start_d, date__lte=end_d)

        day_hours={}
        for en in entries:
            day_hours.setdefault(en.date, Decimal("0"))
            day_hours[en.date] += _hours(en)

        regular=Decimal("0"); overtime=Decimal("0")
        for d,h in day_hours.items():
            if h>Decimal("8.00"):
                regular += Decimal("8.00")
                overtime += (h-Decimal("8.00"))
            else:
                regular += h

        pay_regular=(regular*rate).quantize(Decimal("0.01"))
        pay_overtime=(overtime*rate*mult).quantize(Decimal("0.01"))
        pay_sum=(pay_regular+pay_overtime).quantize(Decimal("0.01"))
        total_pay += pay_sum

        rows.append({"user":u,"rate":rate,"regular_hours":regular,"overtime_hours":overtime,
                     "pay_regular":pay_regular,"pay_overtime":pay_overtime,"pay_sum":pay_sum})

    return render(request,"payroll/report.html",{"year":year,"month":month,"start_d":start_d,"end_d":end_d,"rows":rows,"total_pay":total_pay})
