from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Product, Expert, Seller, Profile, SkinUpload, SkinData,  ExpertResponse,ExpertReview
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

@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    # แสดงฟิลด์ในหน้า Admin
    list_display = ('full_name', 'get_email', 'business_name', 'product_category', 'created_at', 'is_verified', 'verify_link')
    
    # เพิ่มฟิลด์สำหรับการค้นหา
    search_fields = ('full_name', 'user__email', 'business_name', 'product_category')
    
    # เพิ่มตัวกรอง
    list_filter = ('product_category', 'created_at', 'is_verified')
    
    # ระบุฟิลด์ที่ไม่ให้แก้ไข
    readonly_fields = ('created_at',)
    
    # ระบุลำดับการเรียงข้อมูล
    ordering = ('-created_at',)

    # ฟังก์ชันเพื่อแสดงอีเมลจากโมเดล User
    def get_email(self, obj):
        return obj.user.email if obj.user else None
    get_email.short_description = 'อีเมล'  # ตั้งชื่อคอลัมน์ในหน้า Admin

    # ฟังก์ชันเพื่อสร้างลิงก์ตรวจสอบผู้ขาย
    def verify_link(self, obj):
        url = reverse('verify_seller', args=[obj.id])  # ดึง URL ที่จะไปหน้า verify_seller
        return format_html('<a href="{}" target="_blank">ตรวจสอบ</a>', url)
    verify_link.short_description = 'ตรวจสอบผู้ขาย'

@admin.register(SkinUpload)
class SkinUploadAdmin(admin.ModelAdmin):
    list_display = ('user', 'uploaded_at')

# ตั้งค่าการแสดง SkinData ใน Django Admin
class SkinDataAdmin(admin.ModelAdmin):
    list_display = ('user', 'skin_type', 'submitted_at')  # คอลัมน์ที่จะแสดงในหน้า Admin
    list_filter = ('skin_type', 'submitted_at')  # ตัวกรอง
    search_fields = ('user__username', 'skin_type', 'concern')  # ช่องค้นหา

# ตั้งค่าการแสดง ExpertResponse ใน Django Admin
class ExpertResponseAdmin(admin.ModelAdmin):
    list_display = ('expert', 'skin_data', 'created_at')  # คอลัมน์ที่จะแสดง
    list_filter = ('created_at',)  # ตัวกรอง
    search_fields = ('expert__username', 'skin_data__user__username')  # ช่องค้นหา

# ลงทะเบียนโมเดลใน Django Admin
admin.site.register(SkinData, SkinDataAdmin)
admin.site.register(ExpertResponse, ExpertResponseAdmin)

# สำหรับรีวิวผู้เชี่ยวชาญ
@admin.register(ExpertReview)
class ExpertReviewAdmin(admin.ModelAdmin):
    list_display = ('expert', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')