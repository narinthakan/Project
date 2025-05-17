from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.contrib.auth.hashers import make_password, check_password
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.contrib import messages
from django.conf import settings
from django.db.models import Avg, Count
from .forms import RegistrationForm, LoginForm, ProfileForm, ProductForm, ExpertLoginForm, ExpertVerificationForm, SellerRegistrationForm,SellerProfileForm, ExpertRegistrationForm, ExpertProfileForm, SkinDataForm, ExpertResponseForm, ExpertReviewForm, SkinImageForm, ExpertArticleForm, ExpertNameEditForm
from .models import Product, Profile, Review, User, Expert, Seller, SkinUpload, SkinProfile, SkinData, ExpertResponse, ExpertReview, SkinImage, ExpertArticle, Certificate
from django.contrib.auth.models import User, Group
from django.db.models import Q
from django.core.paginator import Paginator 
from django.urls import reverse
from collections import defaultdict
from django.utils import timezone
from datetime import datetime
from io import BytesIO
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from django.http import FileResponse
import base64
import uuid
import os 
import re
from django.core.files import File


# Helper function to check if user is an expert or admin
def is_expert_or_admin(user):
    return user.is_staff or (hasattr(user, 'profile') and user.profile.role == 'Expert')

# Decorator เพื่อให้แน่ใจว่าเป็นผู้ใช้งานที่ล็อกอินแล้ว
@login_required
def profile(request):
    return render(request, 'profile.html')

# Decorator เพื่อจำกัดการเข้าถึงเฉพาะผู้ใช้ที่มี Permission 'view_dashboard'
@permission_required('yourapp.view_dashboard', raise_exception=True)
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

# ฟังก์ชันตรวจสอบว่าเป็น Admin หรือไม่
def is_admin(user):
    return user.groups.filter(name='Admin').exists()

# ใช้ @user_passes_test เพื่อตรวจสอบว่า user เป็น Admin หรือไม่
@user_passes_test(is_admin)
def admin_area(request):
    return render(request, 'admin_area.html')

# ฟังก์ชันที่ต้องการการตรวจสอบบทบาทผู้ใช้
@user_passes_test(lambda user: user.groups.filter(name='Specialist').exists())
def specialist_dashboard(request):
    return render(request, 'specialist_dashboard.html')

# ใช้ @permission_required เพื่อตรวจสอบสิทธิ์การเข้าถึง
@permission_required('yourapp.add_product', raise_exception=True)
def add_product(request):
    if request.method == 'POST':
        # Logic for adding a product
        product_name = request.POST['name']
        product_price = request.POST['price']
        Product.objects.create(name=product_name, price=product_price)
    return render(request, 'add_product.html')

def home(request):
    return render(request, 'home.html', {'message': "ยินดีต้อนรับสู่หน้าหลัก"})

# ฟังก์ชันสำหรับหน้า Home
def home(request):
    # ตรวจสอบว่าเป็นแอดมินหรือไม่
    if request.user.is_staff:
        # หากเป็นแอดมินให้แสดงผู้เชี่ยวชาญที่ยังไม่ได้รับการตรวจสอบ
        experts_to_verify = Expert.objects.filter(is_verified=False)
        
    else:
        # ถ้าไม่ใช่แอดมิน ไม่แสดงข้อมูลนี้
        experts_to_verify = []
    
    return render(request, 'home.html', {'experts_to_verify': experts_to_verify})

# ตรวจสอบว่าเป็นแอดมิน
def is_admin(user):
    return user.is_staff  # is_staff=True คือแอดมิน

# ฟังก์ชันให้แอดมินดูรายชื่อผู้ใช้งานทั้งหมด (ทุก Role)
@login_required
@user_passes_test(is_admin)
def admin_user_list(request):
    users = User.objects.prefetch_related('profile').all()  # ดึงข้อมูล User และ Profile ทุก Role
    return render(request, 'admin_user_list.html', {'users': users})

# ฟังก์ชันให้แอดมินดูโปรไฟล์ของผู้ใช้แต่ละคน (ทุก Role)
@login_required
@user_passes_test(is_admin)
def admin_view_user_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)  # ดึงข้อมูลผู้ใช้
    profile = Profile.objects.filter(user=user).first()  # ดึง Profile ที่เชื่อมกับ User

    if not profile:
        profile = Profile.objects.create(user=user)  # สร้าง Profile อัตโนมัติถ้าไม่มี

    return render(request, 'admin_user_detail.html', {'user': user, 'profile': profile})

# ฟังก์ชันโปรไฟล์ผู้เชี่ยวชาญ
@login_required
def expert_profile(request):
    expert = get_object_or_404(Expert, user=request.user)  # ดึงข้อมูลผู้เชี่ยวชาญที่เกี่ยวข้องกับผู้ใช้
    return render(request, 'expert_profile.html', {'expert_profile': expert})  # เปลี่ยนชื่อเป็น expert_profile

# ฟังก์ชันโปรไฟล์ผู้ขาย
@login_required
def seller_profile(request):
    seller = get_object_or_404(Seller, user=request.user)
    return render(request, 'seller_profile.html', {'seller': seller})

# ฟังก์ชันเลือกโปรไฟล์ตามบทบาท
@login_required
def user_profile(request):
    try:
        profile = Profile.objects.get(user=request.user)
        print(profile)
        if profile.role == 'Expert':
            return redirect('expert_profile')
        elif profile.role == 'Seller':
            return redirect('seller_profile')
        else:
            return render(request, 'user_profile.html', {'profile': profile})
    except Profile.DoesNotExist:
        return render(request, 'error.html', {'message': 'โปรไฟล์ไม่พบ'})


#ฟังก์ชันสำหรับการค้นหาเพราะผลิตภัณฑ์
def search_products(request):
    query = request.GET.get('q', '').strip()  # ดึงค่าคำค้นหา และลบช่องว่าง
    products = Product.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query)  # ค้นหาทั้งชื่อและคำอธิบาย
    ) if query else Product.objects.none()  # ถ้าไม่มีคำค้นหา ส่งผลลัพธ์ว่างเปล่า

    # แบ่งหน้าผลลัพธ์ให้แสดงทีละ 10 รายการ
    paginator = Paginator(products, 10)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'products.html', {
        'products': page_obj,  # ส่งผลลัพธ์ที่แบ่งหน้าไปที่เทมเพลต
        'query': query,  # ส่งค่าคำค้นหาเพื่อให้แสดงบนหน้าเว็บ
    })

    
# ฟังก์ชันสำหรับการสมัครสมาชิก
def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('submit_profile_view')  # ไปที่หน้ากรอกข้อมูลโปรไฟล์
            else:
                messages.error(request, 'ไม่สามารถเข้าสู่ระบบได้ กรุณาลองอีกครั้ง')
        else:
            for field, error in form.errors.items():    #แสดงข้อผอดพลาดจากฟอร์ม
                messages.error(request, f"{field}: {error}")
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})


# ฟังก์ชันสำหรับรายการผู้เชี่ยวชาญที่ต้องการการตรวจสอบ
@user_passes_test(lambda u: u.is_staff)  # เฉพาะแอดมินเท่านั้นที่สามารถเข้าได้
def verify_expert_list(request):
    experts_to_verify = Expert.objects.filter(is_verified=False)  # ดึงข้อมูลผู้เชี่ยวชาญที่ยังไม่ได้รับการตรวจสอบ
    return render(request, 'verify_expert_list.html', {'experts_to_verify': experts_to_verify})

# ฟังก์ชันสำหรับการตรวจสอบผู้เชี่ยวชาญ
@user_passes_test(lambda u: u.is_staff)  # ให้สามารถเข้าถึงได้เฉพาะแอดมิน
def verify_expert(request, expert_id):
    # ใช้ get_object_or_404 เพื่อดึงข้อมูลผู้เชี่ยวชาญหรือส่งกลับ 404 หากไม่พบ
    expert = get_object_or_404(Expert, id=expert_id)
    
    if request.method == 'POST':
        # ยืนยันผู้เชี่ยวชาญ
        expert.is_verified = True
        expert.save()
        
        # ส่งข้อความแจ้งเตือนว่าการยืนยันสำเร็จ
        messages.success(request, f"ผู้เชี่ยวชาญ {expert.full_name} ได้รับการยืนยันแล้ว")
        
        # เปลี่ยนเส้นทางไปยังรายการผู้เชี่ยวชาญที่ต้องการการตรวจสอบ
        return redirect('verify_expert_list')
    
    return render(request, 'verify_expert.html', {'expert': expert})

# ฟังก์ชันสำหรับรายการผู้ขายที่ต้องการการตรวจสอบ
@user_passes_test(lambda u: u.is_staff)  # เฉพาะแอดมินเท่านั้นที่สามารถเข้าได้
def verify_seller_list(request):
    sellers_to_verify = Seller.objects.filter(is_verified=False)  # ดึงข้อมูลผู้ขายที่ยังไม่ได้รับการตรวจสอบ
    return render(request, 'verify_seller_list.html', {'sellers_to_verify': sellers_to_verify})

# ฟังก์ชันสำหรับการตรวจสอบผู้ขาย
@user_passes_test(lambda u: u.is_staff)  # ให้สามารถเข้าถึงได้เฉพาะแอดมิน
def verify_seller(request, seller_id):
    seller = get_object_or_404(Seller, id=seller_id)  # ดึงข้อมูล Seller หรือส่งกลับ 404 หากไม่พบ
    if request.method == 'POST':
        seller.is_verified = True
        seller.save()
        messages.success(request, f"ผู้ขาย {seller.business_name} ได้รับการยืนยันแล้ว")
        return redirect('verify_seller_list')  # กลับไปยังรายการผู้ขาย
    return render(request, 'verify_seller.html', {'seller': seller})


# ฟังก์ชันเข้าสู่ระบบผู้เชี่ยวชาญ
def expert_login(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()  # ใช้ฟิลด์ email
        password = request.POST.get('password', '').strip()  # ใช้ฟิลด์ password

        try:
            # ค้นหา User ที่ใช้อีเมลนี้
            user = User.objects.get(email=email)

            # ตรวจสอบรหัสผ่าน
            if user.check_password(password):  # ตรวจสอบว่ารหัสผ่านถูกต้อง
                login(request, user)  # เข้าสู่ระบบ
                messages.success(request, "เข้าสู่ระบบสำเร็จ!")
                return redirect('home')  # Redirect ไปยังหน้า Home
            else:
                messages.error(request, "รหัสผ่านไม่ถูกต้อง")
        except User.DoesNotExist:
            messages.error(request, "ไม่พบบัญชีที่ใช้อีเมลนี้ในระบบ")
    return render(request, 'expert_login.html')


# ฟังก์ชันลงทะเบียนผู้เชี่ยวชาญ
def register_expert(request):
    if request.method == "POST":
        form = ExpertRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            full_name = form.cleaned_data['full_name']

            # ตรวจสอบว่ามี username หรือ email ซ้ำหรือไม่
            if User.objects.filter(username=username).exists():
                messages.error(request, "ชื่อผู้ใช้นี้ถูกใช้ไปแล้ว")
                return render(request, 'register_expert.html', {'form': form})

            if User.objects.filter(email=email).exists():
                messages.error(request, "อีเมลนี้ถูกใช้ไปแล้ว")
                return render(request, 'register_expert.html', {'form': form})

            # ตรวจสอบ username ใน Expert อีกชั้น
            if Expert.objects.filter(user__username=username).exists():
                messages.error(request, "ชื่อผู้ใช้นี้ถูกใช้ไปแล้วในระบบผู้เชี่ยวชาญ")
                return render(request, 'register_expert.html', {'form': form})

            # สร้าง User
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

            # สร้าง Expert ที่เชื่อมกับ User
            expert = Expert.objects.create(
                user=user,
                full_name=full_name,
                license_number=form.cleaned_data['license_number'],
                expertise=form.cleaned_data['expertise'],
                workplace=form.cleaned_data['workplace'],
                experience=form.cleaned_data['experience'],
                profile_image=form.cleaned_data['profile_image']
            )

            # เพิ่ม User ไปที่ Group 'Expert'
            expert_group = Group.objects.get(name='Expert')
            user.groups.add(expert_group)
            user.save()  # บันทึกการเปลี่ยนแปลง

            messages.success(request, "ลงทะเบียนผู้เชี่ยวชาญสำเร็จ!")
            return redirect('login')  # เปลี่ยนไปยังหน้า login
    else:
        form = ExpertRegistrationForm()

    return render(request, 'register_expert.html', {'form': form})

# ฟังก์ชันเข้าสู่ระบบผู้ขาย
def seller_login(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        # ค้นหา User ที่ใช้ email นี้
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "ไม่พบอีเมลนี้ในระบบ")
            return render(request, 'seller_login.html')

        # ตรวจสอบรหัสผ่าน
        user = authenticate(request, username=user.username, password=password)
        if user is not None:
            login(request, user)
            # ตั้งค่าเซสชันหลังจากล็อกอินสำเร็จ
            request.session['seller_id'] = user.seller_profile.id
            request.session['seller_email'] = user.email
            request.session['seller_fullname'] = user.seller_profile.full_name
            messages.success(request, "เข้าสู่ระบบสำเร็จ!")
            return redirect('home')  # เปลี่ยนไปยังหน้าหลัก
        else:
            messages.error(request, "รหัสผ่านไม่ถูกต้อง")

    return render(request, 'seller_login.html')


# ฟังก์ชันลงทะเบียนผู้ขาย
def register_seller(request):
    if request.method == 'POST':
        form = SellerRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            seller = form.save()  # สร้าง Seller และ User โดยอัตโนมัติจากฟอร์ม
            messages.success(request, "ลงทะเบียนสำเร็จ! คุณสามารถเข้าสู่ระบบได้แล้ว")
            return redirect('seller_login')  # เปลี่ยนไปหน้าล็อกอินผู้ขาย
        else:
            messages.error(request, "ข้อมูลที่กรอกไม่ถูกต้อง")
    else:
        form = SellerRegistrationForm()

    return render(request, 'register_seller.html', {'form': form})


#สำหรับอัปโหลดภาพ
@login_required
def upload_skin(request):
    if request.method == "POST":
        skin_type = request.POST.get("skin_type")
        concern = request.POST.get("concern")
        image = request.FILES.get("skin_image") or request.FILES.get("captured_image")


        if not image:
            messages.error(request, "กรุณาเลือกหรือถ่ายภาพเพื่ออัปโหลด")
            return redirect("upload_skin")

        # บันทึกภาพลงในโมเดล
        skin_data = SkinData.objects.create(
            user=request.user,
            skin_type=skin_type,
            concern=concern,
            skin_image=image
        )


        messages.success(request, "อัปโหลดภาพสำเร็จ!")
        return redirect("expert_view_detail", skin_data_id=skin_data.id)

    return render(request, "upload_skin.html")


# ตรวจสอบว่าเป็น Expert หรือ Admin
def is_expert_or_admin(user):
    return user.is_staff or (hasattr(user, 'profile') and user.profile.role == 'Expert')

#ดูข้อมูลผิว
def analysis_view(request):
    user = request.user
    user_role = None  # กำหนดค่าเริ่มต้น

    # ตรวจสอบว่าผู้ใช้ล็อกอิน และมี Profile หรือไม่
    if user.is_authenticated and hasattr(user, 'profile'):
        profile = user.profile
        if profile.role == "Expert":
            user_role = "expert"
        elif profile.role == "User":
            user_role = "user"
        else:
            user_role = None  # Admin หรือ Role อื่น

    print(f"Debug: User Role = {user_role}")  # ตรวจสอบค่าผ่าน Console
    return render(request, 'analysis.html', {
        'user_role': user_role,  # ส่งค่าไปที่ Template
    })
    
@login_required
def expert_view_page(request):
    if request.user.profile.role != "Expert":
        return redirect('analysis')  # ย้อนกลับหากไม่ได้เป็น Expert
    # ดึงข้อมูลที่ต้องการแสดงให้ผู้เชี่ยวชาญ
    skin_data = SkinUpload.objects.all()
    return render(request, 'expert_view.html', {'skin_data': skin_data})


@login_required
def general_advice_page(request):
    if request.user.profile.role != "User":
        return redirect('analysis')  # ย้อนกลับหากไม่ได้เป็น User ทั่วไป
    # เพิ่มคำแนะนำที่ต้องการแสดง
    return render(request, 'general_advice.html')
    

def home(request):
    context = {}
    
    # ตรวจสอบผู้เชี่ยวชาญที่เข้าสู่ระบบ
    expert_id = request.session.get('expert_id')
    if expert_id:
        try:
            expert = Expert.objects.get(id=expert_id)
            context['user_name'] = expert.full_name  # ชื่อของผู้เชี่ยวชาญ
            context['is_expert'] = True  # สถานะ Expert
        except Expert.DoesNotExist:
            del request.session['expert_id']  # ลบ session ถ้าไม่มีข้อมูล
            context['user_name'] = "Guest"
            context['is_expert'] = False
    # ตรวจสอบ User ปกติที่เข้าสู่ระบบ
    elif request.user.is_authenticated:
        context['user_name'] = request.user.username  # ชื่อของ User ปกติ
        context['is_expert'] = False
    else:
        context['user_name'] = "Guest"  # ยังไม่เข้าสู่ระบบ
        context['is_expert'] = False

    return render(request, 'hom.html', context)


def expert_logout(request):
    if 'expert_id' in request.session:  # ตรวจสอบว่ามี session ของ expert หรือไม่
        del request.session['expert_id']  # ลบค่า expert_id ออกจาก session
        messages.success(request, "ออกจากระบบสำเร็จ!")
    return redirect('home')  # กลับไปที่หน้าหลัก

#อัปเดตข้อมูลโปรไปล์
@login_required
def submit_profile_view(request):
    if request.method == 'POST':
        # ตรวจสอบว่า Profile มีอยู่แล้วหรือไม่
        profile, created = Profile.objects.get_or_create(user=request.user)
        
        # อัปเดตข้อมูลใน Profile
        profile.phone_number = request.POST.get('phone')
        profile.address = request.POST.get('address')
        profile.skin_problem = request.POST.get('skin_problem')
        profile.age = request.POST.get('age')
        profile.gender = request.POST.get('gender')
        profile.save()
        
        # ส่งข้อความแจ้งเตือนสำเร็จ
        if created:
            messages.success(request, 'ลงทะเบียนโปรไฟล์สำเร็จ!')
        else:
            messages.success(request, 'อัปเดตโปรไฟล์สำเร็จ!')
        
        return redirect('home')
    
    return render(request, 'register_success.html')


# ฟังก์ชันแก้ไขโปรไฟล์สำหรับการอัปโหลดรูปภาพและอัปเดตข้อมูล
@login_required
def edit_profile(request):
    profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('user_profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'edit_profile.html', {'form': form})

#ฟังก์ชันแก้ไขโปรไฟล์ผู้เชี่ยวชาญ
@login_required
def edit_expert_profile(request):
    try:
        expert = Expert.objects.get(user=request.user)
    except Expert.DoesNotExist:
        messages.error(request, "ไม่พบข้อมูลผู้เชี่ยวชาญ")
        return redirect('expert_profile')

    if request.method == 'POST':
        form = ExpertProfileForm(request.POST, request.FILES, instance=expert)
        if form.is_valid():
            form.save()
            messages.success(request, "แก้ไขข้อมูลสำเร็จ")
            return redirect('expert_profile')
    else:
        form = ExpertProfileForm(instance=expert)

    return render(request, 'edit_expert_profile.html', {'form': form})

# ฟังก์ชันแก้ไขโปรไฟล์ผู้ขาย
@login_required
def edit_seller_profile(request):
    try:
        seller = Seller.objects.get(user=request.user)
    except Seller.DoesNotExist:
        messages.error(request, "ไม่พบข้อมูลผู้ขาย")
        return redirect('seller_profile')

    if request.method == 'POST':
        form = SellerProfileForm(request.POST, request.FILES, instance=seller)
        if form.is_valid():
            form.save()
            messages.success(request, "แก้ไขโปรไฟล์สำเร็จแล้ว!")
            return redirect('seller_profile')
    else:
        form = SellerProfileForm(instance=seller)

    return render(request, 'edit_seller_profile.html', {'form': form})



# #ฟังก์ชันกรอกข้อมูลผิวหน้า
# def skin_data_form(request):
#     return render(request, 'skin_data_form.html')

# #ฟังก์ชันสำหรับอัปโหลดผิวหน้า
# @login_required
# def upload_skin_view(request):
#     if request.method == 'POST':
#         print("🔍 DEBUG: request.FILES =", request.FILES)
#         skin_data_form = SkinDataForm(request.POST)
#         skin_image_form = SkinImageForm(request.POST, request.FILES)
#         print("🔍 fields in form:", list(skin_image_form.fields.keys()))
#         for k, v in request.FILES.lists():
#             print(f"🔍 FILES key='{k}', value={v}")

#         print(skin_data_form.is_valid())
#         print(skin_image_form.is_valid())

#         if skin_data_form.is_valid():#and skin_image_form.is_valid():
#             try:
#                 skin_data = skin_data_form.save(commit=False)
#                 skin_data.user = request.user
#                 skin_data.save()

#                 images = request.FILES.getlist('images')
#                 print(f"✅ DEBUG: Images uploaded ({len(images)} files)")
                
#                 for img in images:
#                     new_image = SkinImage.objects.create(skin_data=skin_data, image=img)
#                     print(f"✅ DEBUG: Image saved -> {new_image.image.url}")


#                 messages.success(request, "✅ อัปโหลดข้อมูลและภาพสำเร็จ!")

#                 print("🔄 DEBUG: Redirecting to upload_success!")  # เช็คจุด Redirect
#                 return redirect("upload_success")  

#             except Exception as e:
#                 messages.error(request, f"❌ เกิดข้อผิดพลาด: {str(e)}")
#                 print(f"❌ ERROR: {e}")
#                 return redirect("upload_skin")
#         else:
#             print("❌ Form validation failed.")  # เช็คว่าฟอร์มไม่ผ่าน
#             print("SkinDataForm Errors:", skin_data_form.errors)
#             print("SkinImageForm Errors:", skin_image_form.errors)

#             messages.error(request, "❌ กรุณาตรวจสอบข้อมูลที่กรอก")

#     skin_data_form = SkinDataForm()
#     skin_image_form = SkinImageForm()

#     return render(request, "upload_skin.html", {
#         "skin_data_form": skin_data_form,
#         "skin_image_form": skin_image_form,
#     })

#ฟังก์ชันข้อมูลผิวหน้าและอัปโหลภาพ
@login_required
def upload_skin_view(request):
    if request.method == 'POST':
        skin_data_form = SkinDataForm(request.POST)
        skin_image_form = SkinImageForm(request.POST, request.FILES)

        print("🔍 DEBUG: Form Data Received")  # ✅ ตรวจสอบว่ามีการส่งข้อมูลมา
        print("SkinDataForm Valid:", skin_data_form.is_valid())
        print("SkinImageForm Valid:", skin_image_form.is_valid())

        if skin_data_form.is_valid():
            try:
                skin_data = skin_data_form.save(commit=False)
                skin_data.user = request.user
                skin_data.save()
                print(f"✅ Data Saved: {skin_data.skin_type}, {skin_data.concern}")

                # ✅ ตรวจสอบว่ามีไฟล์ที่ถูกอัปโหลดหรือไม่
                images = request.FILES.getlist('images')
                if not images:
                    print("❌ ไม่มีภาพถูกอัปโหลด")
                    messages.error(request, "❌ กรุณาอัปโหลดอย่างน้อย 2 ภาพ")
                    return redirect("skin_data_upload")

                for img in images:
                    skin_image = SkinImage.objects.create(skin_data=skin_data, image=img)
                    print(f"✅ Image Saved: {skin_image.image.url}")

                messages.success(request, "✅ อัปโหลดข้อมูลและภาพสำเร็จ!")
                return redirect("upload_success")

            except Exception as e:
                print(f"❌ ERROR: {e}")
                messages.error(request, f"❌ เกิดข้อผิดพลาด: {str(e)}")
                return redirect("skin_data_upload")

        else:
            print("❌ Form Validation Failed")
            print("SkinDataForm Errors:", skin_data_form.errors)
            print("SkinImageForm Errors:", skin_image_form.errors)
            messages.error(request, "❌ กรุณาตรวจสอบข้อมูลที่กรอก")

    return render(request, "skin_data_upload.html", {
        "skin_data_form": SkinDataForm(),
        "skin_image_form": SkinImageForm(),
    })


def skin_data_upload(request):
    return render(request, 'skin_data_upload.html')


def upload_success(request):
    return render(request, "upload_success.html")

# #ฟังก์ชันสำหรับกรอกข้อมูลผิวหน้า
# @login_required
# def add_skin_profile(request):
#     if request.method == 'POST':
#         skin_type = request.POST.get('skin_type')
#         concern = request.POST.get('concern')
#         allergies = request.POST.get('allergies')
#         current_products = request.POST.get('current_products')
#         skincare_goal = request.POST.get('skincare_goal')

#         SkinProfile.objects.create(
#             user=request.user,
#             skin_type=skin_type,
#             concern=concern,
#             allergies=allergies,
#             current_products=current_products,
#             skincare_goal=skincare_goal
#         )
#         return redirect('expert_view_page')  # เปลี่ยนเส้นทางไปหน้าแสดงข้อมูล
#     return render(request, 'add_skin_profile.html')

# # ฟังก์ชันสำหรับข้อมูลจากฟอร์มและบันทึกลงฐานข้อมูล
# @login_required
# def submit_skin_data(request):
#     if request.method == "POST":
#         form = SkinDataForm(request.POST, request.FILES)
#         if form.is_valid():
#             skin_data = form.save(commit=False)
#             skin_data.user = request.user  # เชื่อมข้อมูลกับผู้ใช้งานที่ล็อกอิน
#             try:
#                 skin_data.save()
#                 messages.success(request, "บันทึกข้อมูลผิวหน้าเรียบร้อยแล้ว!")
#                 return redirect('home')  # เปลี่ยนเป็นหน้า home หลังจากบันทึกข้อมูล
#             except Exception as e:
#                 messages.error(request, "เกิดข้อผิดพลาดในการบันทึกข้อมูล")
#         else:
#             messages.error(request, "เกิดข้อผิดพลาดในการบันทึกข้อมูล กรุณาตรวจสอบข้อมูลอีกครั้ง")
#     else:
#         form = SkinDataForm()
    
#     return render(request, 'skin-data.html', {'form': form})


# ตรวจสอบว่าผู้ใช้เป็นผู้เชี่ยวชาญหรือไม่
def is_expert(user):
    return user.groups.filter(name='Expert').exists()

# ฟังก์ชันสำหรับแสดงรายการข้อมูลผิวหน้าของผู้ใช้งานทั้งหมด
@login_required
@user_passes_test(is_expert)  # อนุญาตเฉพาะผู้เชี่ยวชาญ
def expert_view(request):
    skin_data_list = SkinData.objects.all()  # ดึงข้อมูลผิวหน้าทั้งหมด
    current_expert = request.user  # ดึง Expert ที่ล็อกอินอยู่

    # เตรียมข้อมูลสถานะเฉพาะของ Expert ที่ล็อกอินอยู่
    skin_data_with_status = []
    for skin_data in skin_data_list:
        has_response = ExpertResponse.objects.filter(skin_data=skin_data, expert=current_expert).exists()
        status = "ตอบแล้ว" if has_response else "ยังไม่ตอบ"

        skin_data_with_status.append({
            'data': skin_data,
            'status': status
        })

    return render(request, 'expert_view.html', {
        'skin_data_with_status': skin_data_with_status
    })
    
    

# ฟังก์ชันสำหรับดูรายละเอียดข้อมูลผิวหน้า
@login_required
@user_passes_test(is_expert)
def expert_view_detail(request, user_id):
    """ ดึงข้อมูลทั้งหมดของผู้ใช้ พร้อมรูปภาพ ให้ผู้เชี่ยวชาญดู """

    print(f"🔍 DEBUG: กำลังโหลดข้อมูลของ user_id = {user_id}")

    # ตรวจสอบว่า user_id ที่ส่งเข้ามาเป็น `SkinData.id` หรือ `User.id`
    skin_data_entry = SkinData.objects.filter(id=user_id).select_related("user").first()
    if skin_data_entry:
        actual_user_id = skin_data_entry.user.id
        user_skin_data = SkinData.objects.filter(user=skin_data_entry.user).order_by('-submitted_at')
    else:
        actual_user_id = None
        user_skin_data = SkinData.objects.none()

    print(f"✅ DEBUG: user_id ที่ใช้ในการค้นหา = {actual_user_id}")
    print(f"✅ DEBUG: พบข้อมูล SkinData = {user_skin_data.count()} รายการ")

    # ✅ ดึงข้อมูลล่าสุดและรูปภาพ
    latest_skin_data = user_skin_data.first() if user_skin_data.exists() else None
    all_images = SkinImage.objects.filter(skin_data=latest_skin_data) if latest_skin_data else None

    print(f"✅ DEBUG: จำนวนรูปภาพที่เกี่ยวข้อง = {all_images.count() if all_images else 0}")

    # ✅ ดึงคำตอบล่าสุดของผู้เชี่ยวชาญ
    expert_responses = ExpertResponse.objects.filter(skin_data=latest_skin_data, expert=request.user).order_by('-created_at')

    # ✅ จัดการฟอร์มเมื่อส่ง POST
    if request.method == "POST":
        form = ExpertResponseForm(request.POST)
        if form.is_valid():
            # บันทึกคำตอบใหม่จากผู้เชี่ยวชาญ
            ExpertResponse.objects.create(
                skin_data=latest_skin_data,
                expert=request.user,
                response_text=form.cleaned_data['response_text']
            )
            return redirect('expert_view_detail', user_id=user_id)  # รีเฟรชหน้าหลังจากบันทึกสำเร็จ
    else:
        form = ExpertResponseForm()

    return render(request, 'expert_view_detail.html', {
        "user_skin_data": user_skin_data,
        "latest_skin_data": latest_skin_data,
        "all_images": all_images,
        "expert_responses": expert_responses,  # ส่งคำตอบทั้งหมดไปที่ Template
        "form": form,  # ส่งฟอร์มไปยังเทมเพลต
    })



# ฟังก์ชันสำหรับแสดงข้อมูลผู้ใช้และรีวิวของผู้เชี่ยวชาญ
@login_required
def general_advice(request):
    # ดึงข้อมูลผิวหน้าของผู้ใช้ปัจจุบัน
    user_skin_data = SkinData.objects.filter(user=request.user)

    # ดึงคำแนะนำจากผู้เชี่ยวชาญที่เกี่ยวข้องกับผู้ใช้
    expert_responses = ExpertResponse.objects.filter(skin_data__user=request.user)

    # ดึงข้อมูลที่ส่งไป แต่ยังไม่ได้รับคำตอบ
    skin_data_without_response = user_skin_data.exclude(id__in=expert_responses.values('skin_data'))

    # ดึง "ผู้เชี่ยวชาญทั้งหมด" ที่เคยให้คำแนะนำกับข้อมูลของผู้ใช้
    experts_reviewable = User.objects.filter(expertresponse__skin_data__user=request.user).distinct()

    # ดึง "รีวิวที่ผู้ใช้เคยให้กับผู้เชี่ยวชาญ"
    expert_reviews = ExpertReview.objects.filter(user=request.user)

    # ส่งข้อมูลไปยัง Template
    return render(request, 'general-advice.html', {
        'user_skin_data': user_skin_data,
        'expert_responses': expert_responses,
        'experts_reviewable': experts_reviewable,  # แสดงเฉพาะผู้เชี่ยวชาญที่ให้คำแนะนำแล้ว
        'expert_reviews': expert_reviews,
        'skin_data_without_response': skin_data_without_response,  # ข้อมูลที่ยังไม่ได้รับคำแนะนำ
    })
    
    
# ฟังก์ชันสำหรับเพิ่มรีวิวผู้เชี่ยวชาญ
#@login_required
def review_expert(request, expert_id):
    expert = get_object_or_404(User, id=expert_id)

    if request.method == 'POST':
        form = ExpertReviewForm(request.POST)
        
        if form.is_valid():
            review = form.save(commit=False)
            review.expert = expert
            review.user = request.user  # กำหนดให้ผู้ใช้ที่ล็อกอินเป็นเจ้าของรีวิว
            review.save()

            messages.success(request, "รีวิวของคุณถูกบันทึกเรียบร้อยแล้ว!")
            return redirect('expert_detail', expert_id=expert.id)  # กลับไปหน้าผู้เชี่ยวชาญ
    else:
        form = ExpertReviewForm()

    # **ดึงรีวิวทั้งหมดของผู้เชี่ยวชาญ**
    reviews = ExpertReview.objects.filter(expert=expert).order_by('-created_at')

    return render(request, 'review_expert.html', {
        'form': form,
        'expert': expert,
        'reviews': reviews,  # ส่งรายการรีวิวไปยังเทมเพลต
    })



# ฟังก์ชันลบรีวิวผู้เชี่ยวชาญ
#@login_required
def delete_expert_review(request, review_id):
    review = get_object_or_404(ExpertReview, id=review_id)
    
    # อนุญาตให้ลบได้ถ้าเป็นเจ้าของรีวิวหรือเป็นแอดมิน
    if request.user == review.user or request.user.is_staff:
        review.delete()
        messages.success(request, "ลบรีวิวเรียบร้อยแล้ว")
    else:
        messages.error(request, "คุณไม่มีสิทธิ์ลบความคิดเห็นนี้")

    return redirect('expert_detail', expert_id=review.expert.id)  # กลับไปยังหน้าผู้เชี่ยวชาญ



#@login_required
def review_list(request):
    # ดึงผู้เชี่ยวชาญที่มีรีวิว
    experts = User.objects.filter(reviews__isnull=False).distinct()

    # ดึงข้อมูลรีวิวทั้งหมด
    expert_reviews = ExpertReview.objects.select_related('expert', 'user')

    # สร้าง dictionary {expert_id: <QuerySet รีวิวทั้งหมด>}
    reviews_by_expert = {}
    for expert in experts:
        rqs = expert_reviews.filter(expert=expert)
        if rqs.exists():
            reviews_by_expert[expert.id] = rqs

    return render(request, 'reviews.html', {
        'reviews_by_expert': reviews_by_expert,
        'experts': experts,  # ส่งข้อมูลผู้เชี่ยวชาญ
    })
    
#ดึงข้อมูลผู้เชี่ยวชาญ (User) ที่คุณต้องการมาแสดงเป็นรายการ    
#@login_required
def expert_list(request):
    # สมมุติว่าคุณจะดึงผู้เชี่ยวชาญที่เป็น User ทุกคน
    # หรือถ้ามี field ระบุว่า user นี้เป็นผู้เชี่ยวชาญ ให้กรองตามนั้น
    experts = User.objects.all()
    # ตัวอย่างเช่น: User.objects.filter(is_expert=True)

    return render(request, 'expert_list.html', {
        'experts': experts,
    })

#ดึงข้อมูล “ผู้เชี่ยวชาญ” และ “รีวิว” ทั้งหมดของเขา
#@login_required
def expert_detail(request, expert_id):
    # ดึงข้อมูล Expert ตาม user_id (จะใช้ expert_id จาก URL)
    expert = get_object_or_404(Expert, user_id=expert_id)
    
    # ดึงรีวิวทั้งหมดของผู้เชี่ยวชาญ
    reviews = ExpertReview.objects.filter(expert=expert.user)  # ใช้ expert.user ซึ่งเป็น User ที่เชื่อมกับ Expert
    
    return render(request, 'expert_detail.html', {
        'expert': expert,  # ส่งข้อมูล Expert ไปที่ Template
        'reviews': reviews,  # ส่งข้อมูลรีวิวไปที่ Template
    })




# @login_required
# def expert_detail(request, expert_id):
#     # ดึงข้อมูลผู้เชี่ยวชาญจาก ID
#     expert = get_object_or_404(Expert, id=expert_id)
    
#     # ดึงรีวิวทั้งหมดของผู้เชี่ยวชาญ
#     reviews = ExpertReview.objects.filter(expert=expert.user)  # expert.user คือ User ที่เชื่อมกับ Expert
    
#     return render(request, 'expert_detail.html', {
#         'expert': expert,  # ส่งข้อมูล Expert ไปที่ Template
#         'reviews': reviews,  # ส่งข้อมูลรีวิวไปที่ Template
#     })


    
# @login_required
# def expert_detail(request, expert_id):
#     expert = get_object_or_404(User, id=expert_id)
#     reviews = ExpertReview.objects.filter(expert=expert)

#     return render(request, 'expert_detail.html', {
#         'expert': expert,
#         'reviews': reviews,
#     })



@login_required
def view_expert_reviews(request, expert_id):
    
     expert = get_object_or_404(User, id=expert_id)
     reviews = ExpertReview.objects.filter(expert=expert)

     return render(request, 'expert_reviews.html', {'expert': expert, 'reviews': reviews})


# 🔹 ฟังก์ชันเพิ่มข้อมูลลงใน PDF เทมเพลต
def add_text_to_certificate_template(input_pdf, output_pdf, expert, certificate):
    try:
        # ตรวจสอบฟอนต์ Sarabun
        font_path = os.path.join(settings.BASE_DIR, "static", "fonts", "Sarabun", "Sarabun-Regular.ttf")
        if not os.path.exists(font_path):
            print(f"❌ ไม่พบฟอนต์: {font_path}")
            return False
        
        # ลงทะเบียนฟอนต์ Sarabun
        pdfmetrics.registerFont(TTFont("Sarabun", font_path))

        # อ่านไฟล์ PDF เทมเพลต `Certificate.pdf`
        pdf_reader = PdfReader(input_pdf)
        pdf_writer = PdfWriter()
        page = pdf_reader.pages[0]

        # สร้างไฟล์ PDF ใหม่
        packet = BytesIO()
        canvas_obj = canvas.Canvas(packet, pagesize=letter)
        canvas_obj.setFont("Sarabun", 30)
        
        print(f"🔹 ชื่อผู้เชี่ยวชาญ: {expert.full_name}")

        # เพิ่มข้อมูลลงในใบเกียรติบัตร
        canvas_obj.drawString(340, 300, expert.full_name)  # ชื่อผู้เชี่ยวชาญ

        canvas_obj.setFont("Sarabun",15)
        canvas_obj.drawString(375, 223, f"{round(certificate.average_rating, 2)}")  # คะแนนเฉลี่ย
        canvas_obj.drawString(550, 223, f"{certificate.total_reviews}")  # จำนวนรีวิว
        
        issue_date = certificate.issue_date.strftime('%d %m %Y')  # วันที่ในรูปแบบภาษาอังกฤษ

        # แปลงปี ค.ศ. เป็น พ.ศ.
        day, month, year = issue_date.split(' ')
        year_buddhist = int(year) + 543  # คำนวณปี พ.ศ.
        issue_date_th = f"{day} {month} {year_buddhist}"

        # แทนที่เดือนในรูปแบบภาษาอังกฤษเป็นภาษาไทย
        month_map = {
            '01': 'มกราคม', '02': 'กุมภาพันธ์', '03': 'มีนาคม', 
            '04': 'เมษายน', '05': 'พฤษภาคม', '06': 'มิถุนายน',
            '07': 'กรกฎาคม', '08': 'สิงหาคม', '09': 'กันยายน',
            '10': 'ตุลาคม', '11': 'พฤศจิกายน', '12': 'ธันวาคม'
        }

        # แทนที่เดือนภาษาอังกฤษเป็นภาษาไทย
        for month_num, month_th in month_map.items():
            if month_num in issue_date_th:
                issue_date_th = issue_date_th.replace(month_num, month_th)

        canvas_obj.setFont("Sarabun",20)
        canvas_obj.drawString(440, 177, issue_date_th)        
        # canvas_obj.drawString(280, 340, f"{certificate.issue_date.strftime('%d %B %Y')}")  # วันที่ออก

        # บันทึกการเพิ่มข้อความลงใน PDF
        canvas_obj.save()
        packet.seek(0)

        # ผสานข้อมูลที่เพิ่มเข้าไปใน PDF
        overlay_reader = PdfReader(packet)
        overlay_page = overlay_reader.pages[0]
        page.merge_page(overlay_page)
        pdf_writer.add_page(page)

        # บันทึกไฟล์ PDF ใหม่ทับไฟล์เดิม
        with open(output_pdf, "wb") as output_file:
            pdf_writer.write(output_file)

        print(f"✅ ใบเกียรติบัตรสำหรับ {expert.full_name} ถูกสร้างแล้ว!")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    



# 🔹 ฟังก์ชันสร้างไฟล์ PDF สำหรับใบเกียรติบัตรและแสดงในหน้าเว็บ
@login_required
def generate_and_view_certificate(request, expert_id):
    """
    ตรวจสอบฐานข้อมูล → ตรวจสอบเงื่อนไข → สร้างใบเกียรติบัตรหากผ่านเกณฑ์
    """
    print("🔹 ฟังก์ชัน generate_and_view_certificate ถูกเรียกใช้งานแล้ว!")

    #  1. ตรวจสอบว่าผู้เชี่ยวชาญมีอยู่จริงหรือไม่
    expert = get_object_or_404(Expert, id=expert_id)
    print(f"📌 กำลังตรวจสอบข้อมูลของผู้เชี่ยวชาญ: {expert.user.username}")

    #  2. ตรวจสอบว่ามีใบเกียรติบัตรอยู่ในฐานข้อมูลหรือไม่
    certificate = Certificate.objects.filter(expert=expert.user).first()

    if certificate:
        print(f" พบใบเกียรติบัตรของ {expert.user.username} แล้ว")

    #  3. ตรวจสอบรีวิวของผู้เชี่ยวชาญ
    reviews = ExpertReview.objects.filter(expert=expert.user)
    total_reviews = reviews.count()
    average_rating = sum([review.rating for review in reviews]) / total_reviews if total_reviews > 0 else 0

    print(f" มีรีวิวทั้งหมด: {total_reviews} | คะแนนเฉลี่ย: {average_rating}")

    #  4. ตรวจสอบว่าเพราะอะไรถึงไม่ได้ใบเกียรติบัตร
    if total_reviews < 30:
        return HttpResponse(" ไม่สามารถออกใบเกียรติบัตรได้: จำนวนรีวิวไม่ถึง 30", status=400)

    if average_rating < 4:
        return HttpResponse(" ไม่สามารถออกใบเกียรติบัตรได้: คะแนนเฉลี่ยต่ำกว่า 4.0", status=400)

    #  5. ถ้ายังไม่มีใบเกียรติบัตร → สร้างใหม่
    if not certificate:
        print(f" สร้างใบเกียรติบัตรใหม่ให้ {expert.user.username}")
        print(f"🔹 คะแนนเฉลี่ย: {average_rating}")
        print(f"🔹 จำนวนรีวิว: {total_reviews}")


        certificate = Certificate.objects.create(
            expert=expert.user,
            average_rating=average_rating,
            total_reviews=total_reviews
        )

        certificate.save()
        print(f"✅ บันทึกใบเกียรติบัตรสำเร็จ!")
        


    #  6. อัปเดตใบเกียรติบัตรถ้าข้อมูลเปลี่ยนแปลง
    elif certificate.average_rating != average_rating or certificate.total_reviews != total_reviews:
        print(f" อัปเดตใบเกียรติบัตรของ {expert.user.username}")
        certificate.average_rating = average_rating
        certificate.total_reviews = total_reviews
        certificate.save()

    #  7. ตรวจสอบโฟลเดอร์เก็บไฟล์ PDF
    output_dir = os.path.join(settings.BASE_DIR, "static", "certificates")
    os.makedirs(output_dir, exist_ok=True)

    #  8. ตรวจสอบว่าใบเกียรติบัตร PDF มีอยู่หรือไม่
    output_pdf = os.path.join(output_dir, f"{expert.user.username}_certificate.pdf")
    input_pdf = os.path.join(settings.BASE_DIR, "static", "pdf", "Certificate.pdf")

    certificate_exists = os.path.exists(output_pdf)
    print(f" ตรวจสอบไฟล์ PDF: {'พบ' if certificate_exists else 'ไม่พบ'}")
    
    success = add_text_to_certificate_template(input_pdf, output_pdf, expert, certificate)
    if not success:
            return HttpResponse(" เกิดข้อผิดพลาดในการสร้างใบเกียรติบัตร", status=500)

    #  9. ถ้าไม่มีไฟล์ PDF → สร้างใหม่
    if not certificate_exists:
        if not os.path.exists(input_pdf):
            print(f" ไม่พบไฟล์เทมเพลต PDF ที่ {input_pdf}")
            return HttpResponse(" ไม่พบไฟล์เทมเพลต PDF", status=404)

        print(f"🔹 กำลังสร้างไฟล์ PDF สำหรับ {expert.user.username}")
        # success = add_text_to_certificate_template(input_pdf, output_pdf, expert, certificate)

        # if not success:
        #     return HttpResponse(" เกิดข้อผิดพลาดในการสร้างใบเกียรติบัตร", status=500)
        
        

    #  10. คืนค่า URL ของใบเกียรติบัตร
    pdf_url = f"{settings.STATIC_URL}certificates/{expert.user.username}_certificate.pdf"
    print(f" ใบเกียรติบัตรอยู่ที่: {pdf_url}")

    return render(request, 'expert_certificate.html', {
        'certificate': certificate,
        'pdf_url': pdf_url,
        'expert': expert
    })


# 🔹 ฟังก์ชันแสดงใบเกียรติบัตรเป็น PDF
def view_certificate(request, expert_id):
    expert = get_object_or_404(Expert, id=expert_id)

    # ตรวจสอบสิทธิ์
    if request.user != expert.user and not request.user.is_staff:
        return HttpResponse("คุณไม่มีสิทธิ์เข้าถึงใบเกียรติบัตรนี้", status=403)

    # แปลง username ให้ปลอดภัย
    safe_username = re.sub(r'[^\w.-]', '_', expert.user.username)
    certificate_path = os.path.join(settings.BASE_DIR, "static", "certificates", f"{safe_username}_certificate.pdf")

    if not os.path.exists(certificate_path):
        return HttpResponse("ไม่พบไฟล์ใบเกียรติบัตร", status=404)

    # ✅ ส่งไฟล์ PDF พร้อมเฮดเดอร์ให้ดาวน์โหลด
    response = FileResponse(open(certificate_path, "rb"), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{safe_username}_certificate.pdf"'
    
    return response
    

# 🔹 ฟังก์ชันแสดงใบเกียรติบัตรในหน้าเว็บ
# @login_required
# def expert_certificate_view(request):
#     """
#     แสดงใบเกียรติบัตรของผู้เชี่ยวชาญในหน้าเว็บ
#     """
#     try:
#         expert = request.user
#         certificate = Certificate.objects.filter(expert=expert).first()

#         # สร้าง URL สำหรับไฟล์ PDF ใบเกียรติบัตร
#         pdf_url = f"{settings.STATIC_URL}certificates/{expert.user.username}_certificate.pdf" if certificate else None

#         return render(request, 'expert_certificate.html', {
#             'certificate': certificate,
#             'pdf_url': pdf_url,  # ส่ง URL ของ PDF ไปที่เทมเพลต
#             'expert': expert
#         })

#     except Exception as e:
#         return render(request, 'expert_certificate.html', {
#             'certificate': None,
#             'pdf_url': None,
#             'expert': None,
#             'message': str(e)
#         })

#ฟังก์ชันแก้ไขชื่อใบเกียรติบัตร
@login_required
def edit_expert_name(request):
    expert = get_object_or_404(Expert, user=request.user)
    user = expert.user  # ดึงข้อมูล User จาก Expert

    if request.method == 'POST':
        form = ExpertNameEditForm(request.POST, instance=expert)
        if form.is_valid():
            expert = form.save()

            # รีเฟรชข้อมูลจากฐานข้อมูล
            expert.refresh_from_db()
            user.refresh_from_db()

            messages.success(request, "ชื่อผู้เชี่ยวชาญถูกอัปเดตเรียบร้อยแล้ว")

            # ตรวจสอบว่าเกณฑ์การรับใบเกียรติบัตรผ่านหรือไม่
            certificate = Certificate.objects.filter(expert=expert).first()
            if certificate and certificate.is_eligible_for_certificate():  # ถ้าผ่านเกณฑ์
                output_pdf = os.path.join(settings.BASE_DIR, 'static', 'certificates', f"{user.username}_certificate.pdf")
                input_pdf = os.path.join(settings.BASE_DIR, 'static', 'pdf', 'Certificate.pdf')

                if os.path.exists(input_pdf):
                    if os.path.exists(output_pdf):
                        os.remove(output_pdf)  # ลบไฟล์เก่าก่อนสร้างใหม่
                    print('activate add_text_to_certificate_template')
                    add_text_to_certificate_template(input_pdf, output_pdf, expert, certificate)

            return redirect('expert_certificate_view')

    else:
        form = ExpertNameEditForm(instance=expert)

    return render(request, 'edit_expert_name.html', {'form': form, 'expert': expert})



#ฟังก์ชันการแสดงใบเกียรติบัตรในหน้าเว็บ
# @login_required
# def expert_certificate_view(request):
#     try:
#         # ดึงใบเกียรติบัตรของผู้เชี่ยวชาญที่ล็อกอินอยู่
#         certificate = Certificate.objects.get(expert=request.user)
#     except Certificate.DoesNotExist:
#         certificate = None

#     # ส่งข้อมูลไปที่เทมเพลต
#    return render(request, 'expert_certificate.html', {'certificate': certificate})
   
@login_required
def expert_certificate_view(request):
    try:
        # ดึงข้อมูลผู้เชี่ยวชาญที่ล็อกอินอยู่
        expert = request.user
        print('id',expert)
        certificate = Certificate.objects.filter(expert=expert).first()
        print('expert certificate')

        if certificate:
            print('id',certificate)
            # URL ของ PDF ใน `static/pdf/`
            pdf_url = f"{settings.STATIC_URL}Certificate.pdf"
            
            
        else:
            print('xxx',)
            pdf_url = None  # ถ้ายังไม่มีใบเกียรติบัตร ไม่ต้องแสดง PDF

        return render(request, 'expert_certificate.html', {
            'certificate': certificate,
            'pdf_url': pdf_url,
            'expert': expert
        })

    except Exception as e:
        return render(request, 'expert_certificate.html', {
            'certificate': None,
            'pdf_url': None,
            'expert': None,
            'message': str(e)
        })
        
        
# เหลือฟังชันดาวน์โหลดใบเกียรติบัตรเป็น PDF

#ฟังก์ชันสำหรับแสดงข้อมูลผิวหน้าจากผู้เชี่ยวชาญตอบกลับ
@login_required
def general_advice(request):
    expert_responses = ExpertResponse.objects.filter(skin_data__user=request.user)
    return render(request, 'general_advice.html', {'expert_responses': expert_responses})
    
    
# ฟังก์ชันสำหรับบันทึกข้อมูลผิวหน้า SkinData
def skin_data_form(request):
    if request.method == 'POST':
        # ดีบัค: แสดงข้อมูลที่รับจากฟอร์ม
        print("DEBUG: รับข้อมูล POST:")
        print(f"skin_type: {request.POST.get('skin_type')}")
        print(f"concern: {request.POST.get('concern')}")
        print(f"allergy_history: {request.POST.get('allergy_history', '')}")
        print(f"current_products: {request.POST.get('current_products', '')}")
        print(f"skincare_goal: {request.POST.get('skincare_goal', '')}")

        skin_type = request.POST.get('skin_type')
        concern = request.POST.get('concern')
        allergy_history = request.POST.get('allergy_history', '')
        current_products = request.POST.get('current_products', '')
        skincare_goal = request.POST.get('skincare_goal', '')

        try:
            skin_data = SkinData.objects.create(
                user=request.user,
                skin_type=skin_type,
                concern=concern,
                allergy_history=allergy_history,
                current_products=current_products,
                skincare_goal=skincare_goal
            )
            # ดีบัค: แสดงข้อความเมื่อบันทึกข้อมูลสำเร็จ
            print(f"DEBUG: SkinData ถูกบันทึกสำเร็จ: {skin_data}")
            return redirect('home')  # กลับไปยังหน้าหลักหลังส่งข้อมูล
        except Exception as e:
            # ดีบัค: แสดงข้อความเมื่อเกิดข้อผิดพลาด
            print(f"DEBUG: เกิดข้อผิดพลาดในการบันทึก SkinData: {e}")

    # ดีบัค: สำหรับ GET Request
    print("DEBUG: GET Request - แสดงฟอร์ม")
    return render(request, 'skin_data_form.html')


# ฟังก์ชันเข้าสู่ระบบ
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('member_home')
            else:
                messages.error(request, 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง')
                return redirect('login')
        else:
            messages.error(request, 'กรุณากรอกข้อมูลที่ถูกต้อง')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


# ฟังก์ชันออกจากระบบ
def logout_view(request):
    logout(request)
    return redirect('home')

# ฟังก์ชันบทความ
def articles_web(request):
    return render(request, "articles_web.html")

# ฟังก์ชันตรวจสอบว่าผู้ใช้เป็นผู้เชี่ยวชาญหรือไม่
def is_expert(user):
    return user.is_authenticated and user.groups.filter(name="Expert").exists()

# แสดงบทความของผู้เชี่ยวชาญ
def articles_expert(request):
    """ แสดงรายการบทความของผู้เชี่ยวชาญ """
    articles = ExpertArticle.objects.all()  # ดึงข้อมูลบทความทั้งหมด
    user_is_expert = is_expert(request.user)  # ตรวจสอบว่าเป็นผู้เชี่ยวชาญหรือไม่
    return render(request, "articles_expert.html", {"articles": articles, "user_is_expert": user_is_expert})

def load_article(request, article):
    return render(request, f"{article}.html")

# เพิ่มบทความใหม่ (เฉพาะผู้เชี่ยวชาญ)
@login_required
@user_passes_test(is_expert)
def add_expert_article(request):
    if request.method == 'POST':
        form = ExpertArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.expert = request.user
            article.save()
            messages.success(request, "เพิ่มบทความเรียบร้อยแล้ว!")
            return redirect('articles_expert')
        else:
            messages.error(request, "เกิดข้อผิดพลาด กรุณาตรวจสอบข้อมูลของคุณ")
    else:
        form = ExpertArticleForm()
    
    return render(request, 'add_expert_article.html', {'form': form})

# แก้ไขบทความ (เฉพาะเจ้าของบทความ)
@login_required
@user_passes_test(is_expert)
def edit_expert_article(request, article_id):
    article = get_object_or_404(ExpertArticle, id=article_id, expert=request.user)
    
    if request.method == "POST":
        form = ExpertArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, "แก้ไขบทความเรียบร้อยแล้ว!")
            return redirect("articles_expert")
        else:
            messages.error(request, "เกิดข้อผิดพลาด กรุณาตรวจสอบข้อมูลของคุณ")
    else:
        form = ExpertArticleForm(instance=article)

    return render(request, "edit_expert_article.html", {"form": form, "article": article})

# ลบบทความ (เฉพาะเจ้าของบทความ)
@login_required
@user_passes_test(is_expert)
def delete_expert_article(request, article_id):
    article = get_object_or_404(ExpertArticle, id=article_id, expert=request.user)
    
    if request.method == "POST":
        article.delete()
        messages.success(request, "ลบบทความเรียบร้อยแล้ว!")
        return redirect("articles_expert")

    return render(request, "delete_expert_article.html", {"article": article})

# ฟังก์ชันแสดงหน้าโปรไฟล์
'''
@login_required
def user_profile(request):
     profile = Profile.objects.get(user=request.user)
     return render(request, 'user_profile.html', {'profile': profile})
'''
# ฟังก์ชันสำหรับหน้าแดชบอร์ด
@login_required
def user_dashboard(request):
    return render(request, 'user_dashboard.html')

# ฟังก์ชันหน้าสมาชิกหลัก
@login_required
def member_home(request):
    return render(request, 'home.html')

# ฟังก์ชันหน้าแรกของแอป
def home(request):
    return render(request, 'home.html')

# ฟังก์ชันตรวจสอบสิทธิ์ (Admin, หรือ Seller)
def is_seller_or_admin(request):
    return request.user.is_staff  or hasattr(request.user, 'seller')

# ฟังก์ชันหน้าผลิตภัณฑ์
#@login_required
def products_views(request):
    products = Product.objects.all()
    # ตรวจสอบสิทธิ์ว่าผู้ใช้งานสามารถแก้ไขได้หรือไม่
    can_edit = request.user.is_staff  or hasattr(request.user, 'seller')
    return render(request, 'products.html', {'products': products, 'can_edit': can_edit})


# ตรวจสอบสิทธิ์ของผู้ใช้ (Admin, Seller)
def is_seller_or_admin(user):
    return user.is_authenticated and (user.is_staff or user.groups.filter(name='Seller').exists())

# ฟังก์ชันสำหรับเพิ่มผลิตภัณฑ์
@login_required
@user_passes_test(is_seller_or_admin)
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.user = request.user  # กำหนด user โดยตรงที่นี่
            product.save()
            messages.success(request, 'เพิ่มผลิตภัณฑ์สำเร็จ!')
            return redirect('products')
        else:
            messages.error(request, 'ฟอร์มมีข้อผิดพลาด กรุณาตรวจสอบข้อมูลอีกครั้ง')
    else:
        form = ProductForm()

    return render(request, 'add_product.html', {'form': form})



# แก้ไขผลิตภัณฑ์
@login_required
@user_passes_test(is_seller_or_admin)
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save(commit=False)
            product.user = request.user  # กำหนด user โดยตรงที่นี่
            product.save()
            
            messages.success(request, 'แก้ไขผลิตภัณฑ์สำเร็จ!')
            return redirect('products')
    else:
        form = ProductForm(instance=product)
    return render(request, 'edit_product.html', {'form': form, 'product': product})


# ลบผลิตภัณฑ์
@login_required
@user_passes_test(is_seller_or_admin)
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'ลบผลิตภัณฑ์สำเร็จ!')
        return redirect('products')
    else:
        messages.error(request, 'เกิดข้อผิดพลาดในการลบผลิตภัณฑ์')
    return redirect('products')



# ฟังก์ชันสำหรับเพิ่มรีวิว
@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        comment = request.POST.get('comment')
        rating = request.POST.get('rating')  # รับค่าคะแนนจากฟอร์ม
        
        # ตรวจสอบว่าคะแนนอยู่ในช่วง 1-5 หรือไม่
        if not rating or int(rating) not in range(1, 6):
            messages.error(request, "กรุณาเลือกคะแนนระหว่าง 1-5 ดาว")
            return redirect("product_detail", product_id=product.id)

        # บันทึกรีวิวลงฐานข้อมูล
        Review.objects.create(
            user=request.user,
            product=product,
            comment=comment,
            rating=int(rating),  # แปลงเป็น integer ก่อนบันทึก
        )

        messages.success(request, 'เพิ่มรีวิวสำเร็จ!')
    
    return redirect('product_detail', product_id=product_id)


# ฟังก์ชันลบรีวิว
@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)  # ดึงรีวิวมาโดยไม่จำกัดเฉพาะเจ้าของ
    product_id = review.product.id

    # อนุญาตให้ลบได้หากเป็นเจ้าของรีวิวหรือเป็นแอดมิน
    if request.user == review.user or request.user.is_staff:
        review.delete()
        messages.success(request, 'ความคิดเห็นถูกลบแล้ว')
    else:
        messages.error(request, 'คุณไม่มีสิทธิ์ลบความคิดเห็นนี้')

    return redirect('product_detail', product_id=product_id)

    
#เพิ่มรีวิวในฐานข้อมูล    
@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)  # ดึงข้อมูลสินค้า
    if request.method == 'POST':
        rating = request.POST.get('rating')  # คะแนนที่ส่งมาจากฟอร์ม
        comment = request.POST.get('comment')  # ข้อความรีวิว
        # สร้างรีวิวใหม่และเพิ่มลงฐานข้อมูล
        Review.objects.create(
            user=request.user,  # ผู้ใช้ปัจจุบัน
            product=product,  # สินค้าที่รีวิว
            rating=rating,  # คะแนนรีวิว
            comment=comment  # ข้อความรีวิว
        )
        # อัปเดตคะแนนเฉลี่ยสินค้า
        product.rating = product.average_rating()
        product.save()
        return redirect('product_detail', product_id=product.id)  # กลับไปยังหน้ารายละเอียดสินค้า    

# ฟังก์ชันสำหรับแสดงหน้ารายละเอียดสินค้า
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = Review.objects.filter(product=product)
    context = {
        'product': product,
        'reviews': reviews
    }
    return render(request, 'product_detail.html', context)

# ฟังก์ชันสำหรับหน้า 'Normal Skin'
def normal_skin_view(request):
    return render(request, 'normal_skin.html')

# ฟังก์ชันสำหรับหน้า 'Oily Skin'
def oily_skin_view(request):
    return render(request, 'oily_skin.html')

# ฟังก์ชันสำหรับหน้า 'Dry Skin'
def dry_skin_view(request):
    return render(request, 'dry_skin.html')

# ฟังก์ชันสำหรับหน้า 'Combination Skin'
def combination_skin_view(request):
    return render(request, 'combination_skin.html')

# ฟังก์ชันสำหรับหน้า 'Sensitive Skin'
def sensitive_skin_view(request):
    return render(request, 'sensitive_skin.html')

# ฟังก์ชันแสดงหน้ารีวิวและวิเคราะห์
'''
def analysis_view(request):
    return render(request, 'analysis.html')
'''

def reviews_view(request):
    return render(request, 'reviews.html')
