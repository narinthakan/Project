from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Product, Expert

# Register your models here.


admin.site.register(Product)

@admin.register(Expert)
class ExpertAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'license_number', 'is_verified', 'verify_link')  # แสดงคอลัมน์ใน admin

    def verify_link(self, obj):
        # สร้างลิงค์ที่ใช้ในการตรวจสอบผู้เชี่ยวชาญ
        url = reverse('verify_expert', args=[obj.id])  # ดึง URL ที่จะไปหน้า verify_expert
        return format_html('<a href="{}" target="_blank">ตรวจสอบ</a>', url)

    verify_link.short_description = 'ตรวจสอบผู้เชี่ยวชาญ'  # ตั้งชื่อคอลัมน์เป็น "ตรวจสอบ"