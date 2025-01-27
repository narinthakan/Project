from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test,  permission_required
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from .forms import RegistrationForm,LoginForm,ProfileForm,ProductForm,ExpertLoginForm,ExpertVerificationForm,SellerRegistrationForm,ExpertRegistrationForm,SkinUploadForm,ExpertProfileForm,SkinDataForm,ExpertResponseForm,ExpertReviewForm
from .models import Product, Profile, Review, User, Expert, Seller, SkinUpload, SkinProfile, SkinData, ExpertResponse,ExpertReview
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import redirect, render
import base64

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

# @login_required
# def user_profile(request):
#     # ดึงโปรไฟล์ของผู้ใช้ปัจจุบัน
#     profile = Profile.objects.get(user=request.user)

#     # ตรวจสอบว่าเป็น Expert หรือ Seller เพื่อดึงข้อมูลเพิ่มเติม
#     expert_profile = None
#     seller_profile = None
    
#     # ตรวจสอบบทบาทของผู้ใช้
#     if profile.role == 'Expert' and hasattr(request.user, 'expert_profile'):
#         expert_profile = request.user.expert_profile  # ดึงข้อมูลผู้เชี่ยวชาญ
#     elif profile.role == 'Seller' and hasattr(request.user, 'seller'):
#         seller_profile = request.user.seller  # ดึงข้อมูลผู้ขาย
    
#     # ส่งข้อมูลไปยัง Template
#     return render(request, 'user_profile.html', {
#         'profile': profile,
#         'expert_profile': expert_profile,
#         'seller_profile': seller_profile
#     })

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
    query = request.GET.get('q', '')  # ดึงค่าคำค้นหาจากฟอร์ม
    results = Product.objects.filter(name__icontains=query) if query else Product.objects.none()
    
    return render(request, 'products.html', {
        'products': results,  # ส่งผลลัพธ์ไปที่เทมเพลต
        'query': query,  # ส่งคำค้นไปเพื่อแสดงผล
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
            messages.error(request, 'ข้อมูลไม่ถูกต้อง กรุณาตรวจสอบข้อมูลอีกครั้ง')
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
    expert = Expert.objects.get(id=expert_id)
    if request.method == 'POST':
        expert.is_verified = True
        expert.save()
        return redirect('verify_expert_list')  # กลับไปยังรายการผู้เชี่ยวชาญ
    return render(request, 'verify_expert.html', {'expert': expert})

# ฟังก์ชันสำหรับรายการผู้ขายที่ต้องการการตรวจสอบ
@user_passes_test(lambda u: u.is_staff)  # เฉพาะแอดมินเท่านั้นที่สามารถเข้าได้
def verify_seller_list(request):
    sellers_to_verify = Seller.objects.filter(is_verified=False)  # ดึงข้อมูลผู้ขายที่ยังไม่ได้รับการตรวจสอบ
    return render(request, 'verify_seller_list.html', {'sellers_to_verify': sellers_to_verify})

# ฟังก์ชันสำหรับการตรวจสอบผู้ขาย
@user_passes_test(lambda u: u.is_staff)  # ให้สามารถเข้าถึงได้เฉพาะแอดมิน
def verify_seller(request, seller_id):
    seller = Seller.objects.get(id=seller_id)
    if request.method == 'POST':
        seller.is_verified = True
        seller.save()
        return redirect('verify_seller_list') # กลับไปยังรายการผู้ขาย
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
            Expert.objects.create(
                user=user,
                full_name=full_name,
                license_number=form.cleaned_data['license_number'],
                expertise=form.cleaned_data['expertise'],
                workplace=form.cleaned_data['workplace'],
                experience=form.cleaned_data['experience'],
                profile_image=form.cleaned_data['profile_image']
            )

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

        try:
            # ค้นหา Seller ที่มี email ตรงกัน
            seller = Seller.objects.get(user__email=email)
            user = authenticate(request, username=seller.user.username, password=password)
            if user is not None:
                login(request, user)  # ใช้ระบบล็อกอินของ Django
                request.session['seller_id'] = seller.id
                request.session['seller_email'] = seller.user.email
                request.session['seller_fullname'] = seller.full_name
                messages.success(request, "เข้าสู่ระบบสำเร็จ!")
                return redirect('home')
            else:
                messages.error(request, "รหัสผ่านไม่ถูกต้อง")
        except Seller.DoesNotExist:
            messages.error(request, "ไม่พบบัญชีผู้ขายในระบบ")

    return render(request, 'seller_login.html')

#ฟังก์ชันลงทะเบียนผู้ขาย
def register_seller(request):
    if request.method == 'POST':
        form = SellerRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
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
        if 'image' in request.FILES:  # ตรวจสอบว่ามีไฟล์ภาพในคำขอหรือไม่
            image = request.FILES['image']
            # อัปเดตหรือสร้างข้อมูล SkinUpload
            SkinUpload.objects.update_or_create(
                user=request.user,
                defaults={'skin_image': image}  # ต้องเปลี่ยนเป็นชื่อฟิลด์ในโมเดลที่ใช้เก็บภาพ
            )
            messages.success(request, "อัปโหลดภาพสำเร็จ!")
            return redirect('analysis')  # เปลี่ยนเป็นชื่อ URL หรือหน้าที่คุณต้องการเปลี่ยนไป
        else:
            messages.error(request, "กรุณาเลือกภาพเพื่ออัปโหลด")
    
    return render(request, 'upload_skin.html')

# ตรวจสอบว่าเป็น Expert หรือ Admin
def is_expert_or_admin(user):
    return user.is_staff or (hasattr(user, 'profile') and user.profile.role == 'Expert')

#ดูข้อมูลผิว
@login_required
def analysis_view(request):
    try:
        # ตรวจสอบ Role ของผู้ใช้
        profile = request.user.profile
        if profile.role == "Expert":
            user_role = "expert"
        elif profile.role == "User":
            user_role = "general"
            
        else:
            user_role = None  # กรณี Role อื่นๆ เช่น Admin
    except Profile.DoesNotExist:
        user_role = None  # กรณีที่ Profile ไม่มีในระบบ
    print(f"Debug: User Role = {user_role}")
        
    return render(request, 'analysis.html', {
        'user_role': user_role,  # ส่งค่า user_role ไปยัง Template

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
    

# ฟังก์ชันสำหรับแสดงข้อมูลผิวหน้าของผู้ใช้งาน
# @login_required
# @user_passes_test(is_expert_or_admin)
# def user_skin_data_view(request, user_id):
#     # ดึงข้อมูลผู้ใช้งานตาม ID
#     user = get_object_or_404(User, id=user_id)

#     # ดึงข้อมูลโปรไฟล์ที่เกี่ยวข้องกับผู้ใช้งาน
#     profile = get_object_or_404(Profile, user=user)

#     # ดึงข้อมูลภาพที่ผู้ใช้งานอัปโหลด
#     skin_upload = SkinUpload.objects.filter(user=user).first()

#     return render(request, 'user_skin_data.html', {
#         'user': user,
#         'profile': profile,
#         'skin_upload': skin_upload,
#     })


# # ฟังก์ชันสำหรับแสดงข้อมูลผิวหน้าของผู้ใช้งานพร้อมคำแนะนำจากผู้เชี่ยวชาญ
# # @login_required
# # @user_passes_test(is_expert_or_admin)
# # def expert_user_skin_data(request, user_id):
# #     # ดึงข้อมูลผู้ใช้งานและโปรไฟล์
# #     user = get_object_or_404(User, id=user_id)
# #     profile = get_object_or_404(Profile, user=user)
# #     skin_upload = SkinUpload.objects.filter(user=user).first()

# #     if request.method == "POST":
#         advice = request.POST.get('advice')
#         if advice:
#             # บันทึกคำแนะนำ (สามารถปรับเพิ่มฟิลด์ในโมเดลเพื่อจัดเก็บคำแนะนำได้)
#             messages.success(request, "ส่งคำแนะนำสำเร็จ!")
#             return redirect('expert_user_skin_data', user_id=user_id)

#     return render(request, 'expert_user_skin_data.html', {
#         'user': user,
#         'profile': profile,
#         'skin_upload': skin_upload,
#     })
    

    

# ฟังก์ชันข้อมูลโปรไฟล์ผู้เชี่ยวชาญ
# def expert_profile(request):
#     expert_data = {
#         "name": "ชื่อแพทย์ผู้เชี่ยวชาญ",
#         "license_number": "เลขใบอนุญาต",
#         "email": "อีเมลล์",
#         "specialty": "แพทย์ผิวหนัง",
#     }

#     # ส่งข้อมูลไปยังเทมเพลต
#     return render(request, 'expert_profile.html', {'expert_data': expert_data})

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
            return redirect('view_profile')
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

#ฟังก์ชันกรอกข้อมูลผิวหน้า
def skin_data_form(request):
    return render(request, 'skin_data_form.html')

#ฟังก์ชันสำหรับอัปโหลดผิวหน้า
def upload_skin_view(request):
    if request.method == 'POST' and request.FILES.get('skin_image'):
        uploaded_file = request.FILES['skin_image']
        # ตัวอย่าง: บันทึกไฟล์ลงในระบบหรือฐานข้อมูล
        # คุณสามารถเพิ่มการบันทึกไฟล์ลงใน media ได้โดย:
        with open(f'media/skin_uploads/{uploaded_file.name}', 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        return render(request, 'upload_success.html')  # หน้าเมื่ออัปโหลดสำเร็จ
    return render(request, 'upload_skin.html')  # หน้าแสดงฟอร์มอัปโหลด

#ฟังก์ชันสำหรับกรอกข้อมูลผิวหน้า
@login_required
def add_skin_profile(request):
    if request.method == 'POST':
        skin_type = request.POST.get('skin_type')
        concern = request.POST.get('concern')
        allergies = request.POST.get('allergies')
        current_products = request.POST.get('current_products')
        skincare_goal = request.POST.get('skincare_goal')

        SkinProfile.objects.create(
            user=request.user,
            skin_type=skin_type,
            concern=concern,
            allergies=allergies,
            current_products=current_products,
            skincare_goal=skincare_goal
        )
        return redirect('expert_view_page')  # เปลี่ยนเส้นทางไปหน้าแสดงข้อมูล
    return render(request, 'add_skin_profile.html')

# ฟังก์ชันสำหรับข้อมูลจากฟอร์มและบันทึกลงฐานข้อมูล
@login_required
def submit_skin_data(request):
    if request.method == "POST":
        form = SkinDataForm(request.POST, request.FILES)
        if form.is_valid():
            skin_data = form.save(commit=False)
            skin_data.user = request.user  # เชื่อมข้อมูลกับผู้ใช้งานที่ล็อกอิน
            try:
                skin_data.save()
                messages.success(request, "บันทึกข้อมูลผิวหน้าเรียบร้อยแล้ว!")
                return redirect('home')  # เปลี่ยนเป็นหน้า home หลังจากบันทึกข้อมูล
            except Exception as e:
                messages.error(request, "เกิดข้อผิดพลาดในการบันทึกข้อมูล")
        else:
            messages.error(request, "เกิดข้อผิดพลาดในการบันทึกข้อมูล กรุณาตรวจสอบข้อมูลอีกครั้ง")
    else:
        form = SkinDataForm()
    
    return render(request, 'skin-data.html', {'form': form})


# ตรวจสอบว่าผู้ใช้เป็นผู้เชี่ยวชาญหรือไม่
def is_expert(user):
    return user.groups.filter(name='Expert').exists()

# ฟังก์ชันสำหรับแสดงรายการข้อมูลผิวหน้าของผู้ใช้งานทั้งหมด
@login_required
@user_passes_test(is_expert)  # อนุญาตเฉพาะผู้เชี่ยวชาญ
def expert_view(request):
    # ดึงข้อมูลทั้งหมดจาก SkinData
    skin_data_list = SkinData.objects.all()
    return render(request, 'expert_view.html', {'skin_data_list': skin_data_list})

# ฟังก์ชันสำหรับดูรายละเอียดข้อมูลผิวหน้า
@login_required
@user_passes_test(is_expert)
def expert_view_detail(request, skin_data_id):
    # ดึงข้อมูล SkinData ที่ต้องการดูรายละเอียด
    skin_data = get_object_or_404(SkinData, id=skin_data_id)

    # ตรวจสอบว่ามีคำตอบจากผู้เชี่ยวชาญหรือไม่
    try:
        expert_response = skin_data.response
    except ExpertResponse.DoesNotExist:
        expert_response = None

    # จัดการ POST Request สำหรับการตอบกลับ
    if request.method == 'POST':
        response_text = request.POST.get('response_text', '').strip()
        if response_text:
            if expert_response:
                # อัปเดตคำตอบเดิม
                expert_response.response_text = response_text
                expert_response.save()
            else:
                # สร้างคำตอบใหม่
                ExpertResponse.objects.create(
                    skin_data=skin_data,
                    expert=request.user,
                    response_text=response_text
                )
            messages.success(request, "ตอบกลับสำเร็จ!")
            return redirect('expert_view_detail', skin_data_id=skin_data.id)

    return render(request, 'expert_view_detail.html', {
        'skin_data': skin_data,
        'expert_response': expert_response,
        
    })
    
    
    
# ฟังก์ชันสำหรับรีวิวผู้เชี่ยวชาญ
@login_required
def review_expert(request, expert_id):
    # ดึงข้อมูลผู้เชี่ยวชาญจาก ID
    expert = get_object_or_404(User, id=expert_id)

    # ตรวจสอบว่าผู้ใช้มีรีวิวอยู่แล้วหรือไม่
    existing_review = ExpertReview.objects.filter(expert=expert, user=request.user).first()

    if request.method == 'POST':
        form = ExpertReviewForm(request.POST, instance=existing_review)  # ใช้ instance ถ้ามีรีวิวเดิม
        if form.is_valid():
            review = form.save(commit=False)
            review.expert = expert
            review.user = request.user
            review.save()
            messages.success(request, "รีวิวของคุณถูกบันทึกเรียบร้อยแล้ว!")
            return redirect('general_advice')
    else:
        form = ExpertReviewForm(instance=existing_review)  # โหลดรีวิวเดิมถ้ามี

    # ส่งข้อมูลไปยังเทมเพลต
    return render(request, 'add-expert-review.html', {'form': form, 'expert': expert})


# ฟังก์ชันสำหรับลบรีวิว
@login_required
def delete_review(request, review_id):
    review = get_object_or_404(ExpertReview, id=review_id, user=request.user)
    review.delete()
    messages.success(request, "รีวิวของคุณถูกลบเรียบร้อยแล้ว!")
    return redirect('general_advice')


# ฟังก์ชันสำหรับแสดงข้อมูลผู้ใช้และรีวิวของผู้เชี่ยวชาญ
@login_required
def general_advice(request):
    # ดึงข้อมูลคำแนะนำจากผู้เชี่ยวชาญที่เกี่ยวข้องกับผู้ใช้งานปัจจุบัน
    expert_response = ExpertResponse.objects.filter(skin_data__user=request.user).first()

    # ตรวจสอบว่า ExpertResponse มีข้อมูลหรือไม่
    skin_data = expert_response.skin_data if expert_response else None
    reviews = ExpertReview.objects.filter(expert=expert_response.expert).order_by('-created_at') if expert_response else []

    # จัดการ POST Request สำหรับฟอร์มรีวิว
    if request.method == 'POST' and expert_response:
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        if rating and comment:
            # บันทึกรีวิว
            ExpertReview.objects.create(
                user=request.user,
                expert=expert_response.expert,
                rating=rating,
                comment=comment
            )
            messages.success(request, "รีวิวของคุณถูกบันทึกเรียบร้อยแล้ว!")
            return redirect('general_advice')  # ใช้ redirect เพื่อป้องกันการส่งข้อมูลซ้ำ
        else:
            messages.error(request, "กรุณากรอกคะแนนและความคิดเห็นให้ครบถ้วน")

    # ส่งข้อมูลไปยังเทมเพลต
    return render(request, 'general-advice.html', {
        'skin_data': skin_data,
        'expert_response': expert_response,
        'reviews': reviews
    })




@login_required
def view_expert_reviews(request, expert_id):
     expert = get_object_or_404(User, id=expert_id)
     reviews = ExpertReview.objects.filter(expert=expert)

     return render(request, 'expert_reviews.html', {'expert': expert, 'reviews': reviews})


    
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

# ฟังก์ชันตรวจสอบสิทธิ์ (Admin, Expert, หรือ Seller)
def is_expert_seller_or_admin(request):
    return request.user.is_staff or hasattr(request.user, 'expert_profile') or hasattr(request.user, 'seller')

# ฟังก์ชันหน้าผลิตภัณฑ์
#@login_required
def products_views(request):
    products = Product.objects.all()
    # ตรวจสอบสิทธิ์ว่าผู้ใช้งานสามารถแก้ไขได้หรือไม่
    can_edit = request.user.is_staff or hasattr(request.user, 'expert_profile') or hasattr(request.user, 'seller')
    return render(request, 'products.html', {'products': products, 'can_edit': can_edit})


# ตรวจสอบสิทธิ์ของผู้ใช้ (Admin, Expert, Seller)
def is_expert_seller_or_admin(user):
    return user.is_staff or user.groups.filter(name__in=['Expert', 'Seller']).exists()

# ฟังก์ชันสำหรับเพิ่มผลิตภัณฑ์
@login_required
@user_passes_test(is_expert_seller_or_admin)
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.added_by = request.user
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
@user_passes_test(is_expert_seller_or_admin)
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'แก้ไขผลิตภัณฑ์สำเร็จ!')
            return redirect('products')
    else:
        form = ProductForm(instance=product)
    return render(request, 'edit_product.html', {'form': form, 'product': product})

# ลบผลิตภัณฑ์
@login_required
@user_passes_test(is_expert_seller_or_admin)
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
        Review.objects.create(user=request.user, product=product, comment=comment)
        messages.success(request, 'เพิ่มรีวิวสำเร็จ!')
    return redirect('product_detail', product_id=product_id)

# ฟังก์ชันลบรีวิว
@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user) #ตรวจสอบว่าเป็นเจ้าของรีวิว
    if request.user == review.user:
        product_id = review.product.id
        review.delete()  #ลบรีวิว
        messages.success(request, 'ความคิดเห็นของคุณถูกลบแล้ว')
        return redirect('product_detail', product_id=product_id)
    else:
        messages.error(request, 'คุณไม่สามารถลบความคิดเห็นนี้ได้')
        return redirect('product_detail', product_id=review.product.id)
    
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