from django.urls import path
from . import views
from django.contrib.auth import views as auth_views  # นำเข้าฟังก์ชันการเข้าสู่ระบบและออกจากระบบจาก Django
from django.conf import settings
from django.conf.urls.static import static
from .views import expert_login, seller_login, register_seller, expert_view, admin_user_list, admin_view_user_profile, verify_expert, verify_seller,upload_success, expert_certificate_view

urlpatterns = [
    # เส้นทางสำหรับการสมัครสมาชิก
    path('register/', views.register_view, name='register'),
    
    
    # เส้นทางเข้าสู่ระบบและออกจากระบบ
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # เส้นทางหน้าหลัก
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    
    # เส้นทางแอดมินดูข้อมุลผู้ใช้งาน
    path('admin/users/', admin_user_list, name='admin_user_list'),  # ดูรายชื่อผู้ใช้ทั้งหมด
    path('admin/user/<int:user_id>/', admin_view_user_profile, name='admin_view_user_profile'),  # ดูโปรไฟล์แต่ละคน
    
    #เส้นทางค้นหาผลิตภัณฑ์
    path('search/', views.search_products, name='search_products'),

    # เส้นทางหน้าสมาชิก
    path('member/', views.member_home, name='member_home'),
    path('user_home/', views.member_home, name='user_home'),
    
    #path('expert-login/', views.expert_login, name='expert_login'),  # ผู้เชี่ยวชาญ
    
    # เส้นทางสำหรับการสมัครสมาชิกผู้เชี่ยวชาญ
    path('expert-login/', views.expert_login, name='expert_login'),
    path('register-expert/', views.register_expert, name='register_expert'),
    path('home/', views.home, name='home'),
    
    # เส้นทางสำหรับตรวจสอบผู้เชี่ยวชาญและผู้ขาย
    path('verify_expert/', views.verify_expert_list, name='verify_expert_list'),  # รายการผู้เชี่ยวชาญที่ต้องการการตรวจสอบ
    path('verify_expert/<int:expert_id>/', views.verify_expert, name='verify_expert'),  # หน้า ตรวจสอบผู้เชี่ยวชาญ
    path('verify_sellers/', views.verify_seller_list, name='verify_seller_list'),
    path('verify_sellers/<int:seller_id>/', views.verify_seller, name='verify_seller'),
    
    #เส้นทางสำหรับเข้าสู่ระบบผู้ขาย
    path('seller_login/', seller_login, name='seller_login'),
    #เส้นทางสำหรับหน้าลงทะเบียนผู้ขาย
    path('register_seller/', views.register_seller, name='register_seller'),
    path('home/', views.home, name='home'),

    # เส้นทางสำหรับแสดงหน้าโปรไฟล์และแก้ไขโปรไฟล์
    path('user_profile/', views.user_profile, name='user_profile'),  # ดูโปรไฟล์
    path('seller_profile/', views.seller_profile, name='seller_profile'),
    path('expert_profile/', views.expert_profile, name='expert_profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),  # ฟังก์ชันแก้ไขโปรไฟล์ใหม่
    path('edit_expert_profile/', views.edit_expert_profile, name='edit_expert_profile'),
    path('edit_seller_profile/', views.edit_seller_profile, name='edit_seller_profile'),

    # เส้นทางสำหรับหน้าแดชบอร์ด
    path('dashboard/', views.user_dashboard, name='user_dashboard'),

    # เส้นทางหน้าผลิตภัณฑ์
    path('products/', views.products_views, name='products'),
    
    # เส้นบทความเกี่ยวกับการดูแลผิว
    path('articles-web/', views.articles_web, name='articles_web'),
    path('articles-web/<str:article>/', views.load_article, name='load_article'),
    path('normal-skin/', views.normal_skin_view, name='normal_skin'),
    path('oily-skin/', views.oily_skin_view, name='oily_skin'),
    path('dry-skin/', views.dry_skin_view, name='dry_skin'),
    path('combination-skin/', views.combination_skin_view, name='combination_skin'),
    path('sensitive-skin/', views.sensitive_skin_view, name='sensitive_skin'),
    
    # เส้นทางสำหรับบทความของผู้เชี่ยวชาญ
    path('articles-expert/', views.articles_expert, name='articles_expert'),
    path('articles-expert/add/', views.add_expert_article, name='add_expert_article'),
    path('articles-expert/edit/<int:article_id>/', views.edit_expert_article, name='edit_expert_article'),
    path('articles-expert/delete/<int:article_id>/', views.delete_expert_article, name='delete_expert_article'),
    
    # เส้นทางสำหรับบทความ
    path('articles-web/', views.articles_web, name='articles_web'),
    path('articles-expert/', views.articles_expert, name='articles_expert'),
    

    # เส้นทางหน้าวิเคราะห์
    path('analysis/', views.analysis_view, name='analysis'),
    
    #เส้นทางสำหรับกรอกข้อมูลผิวหน้าและอัปโหลดภาพผิวหน้า
    path('skin-data-upload/', views.upload_skin_view, name='skin_data_upload'),
    
    #เส้นทางสำหรับดูข้อมูลผิวหน้า
    # path('user_skin_data/<int:user_id>/', views.user_skin_data_view, name='user_skin_data'),
    #path('expert/skin_data/', views.expert_user_skin_data, name='expert_user_skin_data'),
    # path('expert/skin_data/<int:user_id>/', views.expert_user_skin_data, name='expert_user_skin_data'),
    path('expert-view/', views.expert_view, name='expert_view'),
    path('general-advice/', views.general_advice, name='general_advice'),
    #path('add-skin-profile/', views.add_skin_profile, name='add_skin_profile'),
    #path('expert-view/', views.expert_view_page, name='expert_view_page'),
    path('expert-view/<int:skin_data_id>/', views.expert_view_detail, name='expert_view_detail'),
    #path('skin-data-list/', views.skin_data_list_view, name='skin_data_list'),  # เส้นทางแสดงรายการ
    path('expert-view/<int:skin_data_id>/', views.expert_view_detail, name='expert_view_detail'),  # เส้นทางสำหรับดูรายละเอียด
    #path('expert-response/<int:skin_data_id>/', views.expert_response, name='expert_response'),
    path('expert-dashboard/', expert_view, name='expert_dashboard'),
 
    # เส้นทางสำหรับรีวิวผู้เชี่ยวชาญ
    path('reviews/', views.review_list, name='reviews'),  # แสดงรายการรีวิวทั้งหมด
    path('reviews/', views.review_list, name='reviews_list'),
    path('review-expert/<int:expert_id>/', views.review_expert, name='review_expert'),  # เพิ่มหรือแก้ไขรีวิวของผู้เชี่ยวชาญ
    path('expert-reviews/<int:expert_id>/', views.view_expert_reviews, name='view_expert_reviews'),  # ดูรีวิวของผู้เชี่ยวชาญ
    path('delete-review/<int:review_id>/', views.delete_expert_review, name='delete_expert_review'),  # ลบรีวิว

    # เส้นทางเกี่ยวกับผู้เชี่ยวชาญ
    path('expert-list/', views.expert_list, name='expert_list'),  # รายชื่อผู้เชี่ยวชาญ
    path('expert-detail/<int:expert_id>/', views.expert_detail, name='expert_detail'),  # หน้าแสดงรายละเอียดของผู้เชี่ยวชาญ

    
    #path('delete-review-review/<int:review_id>/', views.delete_review, name='delete_expert_review'),
    
    #เส้นทางสำหรับใบเกียรติบัตรผู้เชี่ยวชาญ
    path('expert-certificate/', views.expert_certificate_view, name='expert_certificate_view'),
    path('generate_certificate/<int:expert_id>/', views.generate_and_view_certificate, name='generate_certificate'),
    path('view_certificate/<int:expert_id>/', views.view_certificate, name='view_certificate'),
    
    # เส้นทางสำหรับแก้ไขชื่อใบเกียรติบัตร
    path('edit_expert_name/', views.edit_expert_name, name='edit_expert_name'),

    #เส้นทางสำหรับกรอกข้อมูลผิวหน้าของคุณ
    path('skin-data/', views.skin_data_form, name='skin_data_form'),
    
    #เส้นทางสำหรับอัปโหลดผิวหน้า
    #path('upload-skin/', views.upload_skin_view, name='upload_skin'),
    path('upload-success/', views.upload_success, name='upload_success'),
    path('accounts/expert-view/<int:user_id>/', views.expert_view_detail, name='expert_view_detail'),
    

    
    # เส้นทางสำหรับส่งข้อมูลโปรไฟล์เพิ่มเติมหลังจากสมัครสมาชิก
    path('submit-profile/', views.submit_profile_view, name='submit_profile_view'),

    # เส้นทางสำหรับการรีเซ็ตรหัสผ่าน
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # สำหรับการแสดงหน้ารายละเอียดของผลิตภัณฑ์
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),

    # สำหรับการเพิ่มรีวิวและลบรีวิวผลิตภัณฑ์
    path('product/<int:product_id>/review/', views.add_review, name='add_review'),
    path('delete_review/<int:review_id>/', views.delete_review, name='delete_review'),

    # สำหรับเพิ่มผลิตภัณฑ์
    path('add_product/', views.add_product, name='add_product'),

    # เส้นทางสำหรับการแก้ไขและลบผลิตภัณฑ์
    path('product/edit/<int:product_id>/', views.edit_product, name='edit_product'),  # แก้ไขผลิตภัณฑ์
    path('product/delete/<int:product_id>/', views.delete_product, name='delete_product'),  # ลบผลิตภัณฑ์

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)