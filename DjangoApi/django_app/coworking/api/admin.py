from django.contrib import admin, messages
from django import forms
from django.urls import path, reverse
from django.shortcuts import render, redirect
from io import TextIOWrapper
import csv

from .models import Seat
from django.contrib.admin.sites import NotRegistered

def combo_code(d, s, e):
    if d and s and e: return 'DSE'
    if d and s: return 'DS'
    if d and e: return 'DE'
    if s and e: return 'SE'
    if d: return 'D'
    if s: return 'S'
    if e: return 'E'
    return '0'

def split_code(code):
    code = (code or '0').upper()
    return ('D' in code, 'S' in code, 'E' in code)

class SeatAdminForm(forms.ModelForm):
    cb_d = forms.BooleanField(label="D – Docking station", required=False)
    cb_s = forms.BooleanField(label="S – Two screens", required=False)
    cb_e = forms.BooleanField(label="E – Electric desk", required=False)
    class Meta:
        model = Seat
        fields = ["code", "floor", "features"]
        widgets = {"features": forms.HiddenInput()}
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        d, s, e = split_code(getattr(self.instance, "features", "0"))
        if not self.is_bound:
            self.fields["cb_d"].initial = d
            self.fields["cb_s"].initial = s
            self.fields["cb_e"].initial = e
    def clean(self):
        cleaned = super().clean()
        d = cleaned.get("cb_d") or False
        s = cleaned.get("cb_s") or False
        e = cleaned.get("cb_e") or False
        cleaned["features"] = combo_code(d, s, e)
        return cleaned

class SeatAdmin(admin.ModelAdmin):
    form = SeatAdminForm
    list_display = ("code", "floor", "features_badge")
    search_fields = ("code",)
    list_filter = ("floor",)
    actions = ["set_0","set_D","set_S","set_E","set_DS","set_DE","set_SE","set_DSE"]

    def features_badge(self, obj):
        col = {"D":"#f59e0b","S":"#3b82f6","E":"#a855f7","DS":"#2563eb","DE":"#3f51b5","SE":"#009688","DSE":"#ff5722","0":"#4caf50"}
        f = (obj.features or "0").upper()
        c = col.get(f, "#6b7280")
        return f'<span style="display:inline-block;padding:2px 8px;border-radius:10px;background:{c};color:#fff;font-weight:600">{f}</span>'
    features_badge.allow_tags = True
    features_badge.short_description = "Features"

    def _set_feature(self, request, queryset, code):
        n = queryset.update(features=code)
        self.message_user(request, f"Updated {n} seat(s) → {code}", messages.SUCCESS)
    def set_0(self, r, qs): self._set_feature(r, qs, "0")
    def set_D(self, r, qs): self._set_feature(r, qs, "D")
    def set_S(self, r, qs): self._set_feature(r, qs, "S")
    def set_E(self, r, qs): self._set_feature(r, qs, "E")
    def set_DS(self, r, qs): self._set_feature(r, qs, "DS")
    def set_DE(self, r, qs): self._set_feature(r, qs, "DE")
    def set_SE(self, r, qs): self._set_feature(r, qs, "SE")
    def set_DSE(self, r, qs): self._set_feature(r, qs, "DSE")
    set_0.short_description="Set amenities → 0"
    set_D.short_description="Set amenities → D"
    set_S.short_description="Set amenities → S"
    set_E.short_description="Set amenities → E"
    set_DS.short_description="Set amenities → DS"
    set_DE.short_description="Set amenities → DE"
    set_SE.short_description="Set amenities → SE"
    set_DSE.short_description="Set amenities → DSE"

    def get_urls(self):
        urls = super().get_urls()
        my = [
            path("import-csv/", self.admin_site.admin_view(self.import_csv_view), name="seat_import_csv"),
            path("generate/", self.admin_site.admin_view(self.generate_view), name="seat_generate"),
        ]
        return my + urls

    def import_csv_view(self, request):
        if request.method == "POST" and request.FILES.get("file"):
            f = TextIOWrapper(request.FILES["file"].file, encoding="utf-8")
            reader = csv.DictReader(f)
            for row in reader:
                code = (row.get("code") or "").strip()
                if not code: continue
                floor = int(row.get("floor") or 0)
                features = (row.get("features") or "0").upper()
                Seat.objects.update_or_create(code=code, defaults={"floor": floor, "features": features})
            return redirect(reverse("admin:%s_%s_changelist" % (Seat._meta.app_label, Seat._meta.model_name)))
        return render(request, "admin/seat_import.html", {})

    def generate_view(self, request):
        if request.method == "POST":
            floor = int(request.POST.get("floor") or 0)
            rows = int(request.POST.get("rows") or 1)
            prefix = (request.POST.get("prefix") or str(floor)).strip()
            pad = int(request.POST.get("pad") or 2)
            for r in range(1, rows+1):
                code = f"{prefix}-{str(r).zfill(pad)}"
                Seat.objects.get_or_create(code=code, defaults={"floor": floor, "features": "0"})
            return redirect(reverse("admin:%s_%s_changelist" % (Seat._meta.app_label, Seat._meta.model_name)))
        return render(request, "admin/seat_generate.html", {})

# bezpieczna rejestracja: najpierw spróbuj wyrejestrować, potem zarejestruj naszą klasę
try:
    admin.site.unregister(Seat)
except NotRegistered:
    pass
admin.site.register(Seat, SeatAdmin)
