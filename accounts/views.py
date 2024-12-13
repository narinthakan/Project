from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test,  permission_required
from django.contrib import messages
from .forms import RegistrationForm, LoginForm, ProfileForm, ProductForm, ExpertLoginForm, ExpertVerificationForm, SellerRegistrationForm
from .models import Product, Profile, Review, Expert, Seller
from django.contrib.auth.models import User



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

# ตัวอย่างฟังก์ชันที่ต้องการการตรวจสอบบทบาทผู้ใช้
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


# ฟังก์ชันสำหรับการเข้าสู่ระบบผู้เชี่ยวชาญ
def expert_login(request):
    error_message = None  # ใช้สำหรับเก็บข้อความข้อผิดพลาด

    if request.method == 'POST':
        form = ExpertLoginForm(request.POST)
        if form.is_valid():
            # ตรวจสอบข้อมูลในระบบ (คุณสามารถเปลี่ยนแปลงเพื่อตรวจสอบข้อมูลในฐานข้อมูลได้)
            # ตัวอย่างนี้แสดงผลสำเร็จโดยไม่เชื่อมต่อ API
            messages.success(request, "เข้าสู่ระบบสำเร็จ")
            return redirect('expert_profile')  # เปลี่ยนไปที่หน้าโปรไฟล์ผู้เชี่ยวชาญ
        else:
            error_message = "กรุณาตรวจสอบข้อมูลที่กรอก"
    else:
        form = ExpertLoginForm()

    return render(request, 'expert_login.html', {'form': form, 'error_message': error_message})


# ฟังก์ชันสำหรับสมัครสมาชิกผู้เชี่ยวชาญ
def register_expert(request):
    if request.method == 'POST':
        # ประมวลผลข้อมูลที่กรอกในฟอร์ม
        form = ExpertLoginForm(request.POST)
        if form.is_valid():
            # เก็บข้อมูลในระบบหรือแสดงข้อความสำเร็จ
            messages.success(request, "สมัครสมาชิกผู้เชี่ยวชาญสำเร็จ!")
            return redirect('expert_login')  # เปลี่ยนเส้นทางกลับไปที่หน้าล็อกอิน
        else:
            messages.error(request, "กรุณาตรวจสอบข้อมูล")
    else:
        form = ExpertLoginForm()

    return render(request, 'register_expert.html', {'form': form})


# ฟังก์ชันข้อมูลโปรไฟล์ผู้เชี่ยวชาญ
def expert_profile(request):
    expert_data = {
        "name": "ชื่อแพทย์ผู้เชี่ยวชาญ",
        "license_number": "เลขใบอนุญาต",
        "email": "อีเมลล์",
        "specialty": "แพทย์ผิวหนัง",
    }

    # ส่งข้อมูลไปยังเทมเพลต
    return render(request, 'expert_profile.html', {'expert_data': expert_data})


# ฟังก์ชันจัดการข้อมูลโปรไฟล์เพิ่มเติม
@login_required
def submit_profile_view(request):
    if request.method == 'POST':
        profile = Profile.objects.create(
            user=request.user,
            phone_number=request.POST.get('phone'),
            address=request.POST.get('address'),
            skin_problem=request.POST.get('skin_problem'),
            age=request.POST.get('age'),
            gender=request.POST.get('gender')
        )
        messages.success(request, 'ลงทะเบียนโปรไฟล์สำเร็จ!')
        return redirect('user_home')
    return render(request, 'register_success.html')

# ฟังก์ชันแก้ไขโปรไฟล์สำหรับการอัปโหลดรูปภาพและอัปเดตข้อมูล
@login_required
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()

            user = request.user
            user.first_name = form.cleaned_data.get('first_name')
            user.last_name = form.cleaned_data.get('last_name')
            user.email = form.cleaned_data.get('email')
            user.save()

            messages.success(request, 'อัปเดตข้อมูลโปรไฟล์เรียบร้อยแล้ว!')
            return redirect('user_profile')
    else:
        form = ProfileForm(instance=profile)
    
    return render(request, 'edit_profile.html', {'form': form})

#ฟังก์ชันเข้าสู่ระบบSeller/ผู้ขาย
def register_seller(request):
    if request.method == 'POST':
        form = SellerRegistrationForm(request.POST, request.FILES)  # รองรับไฟล์อัปโหลด
        if form.is_valid():
            form.save()  # บันทึกข้อมูลลงฐานข้อมูล
            messages.success(request, "สมัครสมาชิกสำเร็จ!")
            return redirect('seller_login')  #หลังสมัครสำเร็จ ให้กลับไปหน้าล็อคอินผู้ขาย
        else:
            messages.error(request, "กรุณากรอกข้อมูลให้ถูกต้อง")
    else:
        form = SellerRegistrationForm()

    return render(request, 'register_seller.html', {'form': form})

def seller_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')  # รับอีเมลจากฟอร์ม
        password = request.POST.get('password')  # รับรหัสผ่านจากฟอร์ม

        # ตรวจสอบว่า Seller มีอยู่ในระบบหรือไม่
        try:
            seller = Seller.objects.get(email=email)
        except Seller.DoesNotExist:
            messages.error(request, "ไม่พบบัญชีผู้ขายในระบบ")
            return redirect('seller_login')

        # ตรวจสอบรหัสผ่าน (กำหนดรหัสผ่านในโมเดล Seller เองหรือใช้ระบบ Auth ของ Django)
        if seller and seller.phone_number == password:  # ใช้ phone_number เป็น password (ควรใช้ hashing แทน)
            request.session['seller_id'] = seller.id  # บันทึกข้อมูล session ของ Seller
            messages.success(request, "เข้าสู่ระบบสำเร็จ")
            return redirect('seller_dashboard')  # เปลี่ยนไปหน้า Dashboard
        else:
            messages.error(request, "อีเมลหรือรหัสผ่านไม่ถูกต้อง")
            return redirect('seller_login')

    return render(request, 'seller_login.html')


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
@login_required
def user_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, 'user_profile.html', {'profile': profile})

# ฟังก์ชันสำหรับหน้าแดชบอร์ด
@login_required
def user_dashboard(request):
    return render(request, 'user_dashboard.html')

# ฟังก์ชันหน้าสมาชิกหลัก
@login_required
def member_home(request):
    return render(request, 'user_home.html')

# ฟังก์ชันหน้าแรกของแอป
def home(request):
    return render(request, 'home.html')

# ฟังก์ชันหน้าผลิตภัณฑ์
def products_views(request):
    products = Product.objects.all()
    return render(request, 'products.html', {'products': products})

# เพิ่มผลิตภัณฑ์
@login_required
@user_passes_test(is_expert_or_admin)
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'เพิ่มผลิตภัณฑ์สำเร็จ!')
            return redirect('products')
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})

# แก้ไขผลิตภัณฑ์
@login_required
@user_passes_test(is_expert_or_admin)
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
@user_passes_test(is_expert_or_admin)
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
def analysis_view(request):
    return render(request, 'analysis.html')

def reviews_view(request):
    return render(request, 'reviews.html')







