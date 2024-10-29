from django.urls import path
from . import views
from django.contrib.auth import views as auth_views  # นำเข้าฟังก์ชันการเข้าสู่ระบบและออกจากระบบจาก Django
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # เส้นทางสำหรับการสมัครสมาชิก
    path('register/', views.register_view, name='register'),

    # เส้นทางเข้าสู่ระบบและออกจากระบบ
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # เส้นทางหน้าหลัก
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),

    # เส้นทางหน้าสมาชิก
    path('member/', views.member_home, name='member_home'),
    path('user_home/', views.member_home, name='user_home'),

    # เส้นทางสำหรับแสดงหน้าโปรไฟล์และแก้ไขโปรไฟล์
    path('user_profile/', views.user_profile, name='user_profile'),  # ดูโปรไฟล์
    path('edit-profile/', views.edit_profile, name='edit_profile'),  # ฟังก์ชันแก้ไขโปรไฟล์ใหม่

    # เส้นทางสำหรับหน้าแดชบอร์ด
    path('dashboard/', views.user_dashboard, name='user_dashboard'),

    # เส้นทางหน้าผลิตภัณฑ์และบทความเกี่ยวกับการดูแลผิว
    path('products/', views.products_views, name='products'),
    path('normal-skin/', views.normal_skin_view, name='normal_skin'),
    path('oily-skin/', views.oily_skin_view, name='oily_skin'),
    path('dry-skin/', views.dry_skin_view, name='dry_skin'),
    path('combination-skin/', views.combination_skin_view, name='combination_skin'),
    path('sensitive-skin/', views.sensitive_skin_view, name='sensitive_skin'),

    # เส้นทางหน้าวิเคราะห์และรีวิว
    path('analysis/', views.analysis_view, name='analysis'),
    path('reviews/', views.reviews_view, name='reviews'),

    # เส้นทางสำหรับส่งข้อมูลโปรไฟล์เพิ่มเติมหลังจากสมัครสมาชิก
    path('submit-profile/', views.submit_profile_view, name='submit_profile_view'),

    # เส้นทางสำหรับการรีเซ็ตรหัสผ่าน
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

     # สำหรับการแสดงหน้ารายละเอียดของผลิตภัณฑ์
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),

    # สำหรับการเพิ่มรีวิวและลบรีวิว
    path('product/<int:product_id>/review/', views.add_review, name='add_review'),
    path('delete_review/<int:review_id>/', views.delete_review, name='delete_review'),

    # สำหรับเพิ่มผลิตภัณฑ์
    path('add_product/', views.add_product, name='add_product'),

    # เส้นทางสำหรับการแก้ไขและลบผลิตภัณฑ์
    path('product/edit/<int:product_id>/', views.edit_product, name='edit_product'),  # แก้ไขผลิตภัณฑ์
    path('product/delete/<int:product_id>/', views.delete_product, name='delete_product'),  # ลบผลิตภัณฑ์

    

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)









