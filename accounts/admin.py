from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Product, Expert, Seller,Profile, SkinUpload

# Register your models here.


admin.site.register(Product)
admin.site.register(Profile)
@admin.register(Expert)
class ExpertAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'license_number', 'is_verified', 'verify_link')  # แสดงคอลัมน์ใน admin

    def verify_link(self, obj):
        # สร้างลิงค์ที่ใช้ในการตรวจสอบผู้เชี่ยวชาญ
        url = reverse('verify_expert', args=[obj.id])  # ดึง URL ที่จะไปหน้า verify_expert
        return format_html('<a href="{}" target="_blank">ตรวจสอบ</a>', url)

    verify_link.short_description = 'ตรวจสอบผู้เชี่ยวชาญ'  # ตั้งชื่อคอลัมน์เป็น "ตรวจสอบ"
    
    
# กำหนดการตั้งค่าสำหรับโมเดล Seller ใน Admin
@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    # แสดงฟิลด์ในหน้า Admin
    list_display = ('full_name', 'email', 'business_name', 'product_category', 'created_at')
    # เพิ่มฟิลด์สำหรับการค้นหา
    search_fields = ('full_name', 'email', 'business_name', 'product_category')
    # เพิ่มตัวกรอง
    list_filter = ('product_category', 'created_at')
    # ระบุฟิลด์ที่ไม่ให้แก้ไข
    readonly_fields = ('created_at',)
    # ระบุลำดับการเรียงข้อมูล
    ordering = ('-created_at',)
    
@admin.register(SkinUpload)
class SkinUploadAdmin(admin.ModelAdmin):
    list_display = ('user', 'uploaded_at')   