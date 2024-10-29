from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import RegistrationForm, LoginForm, ProfileForm, ProductForm
from .models import Product, Profile, Review
from django.contrib.auth.models import User

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
    products = Product.objects.all()  # แสดงสินค้าทั้งหมดแทนที่จะเป็นสินค้ายอดนิยมเท่านั้น
    return render(request, 'products.html', {'products': products})

# เพิ่มผลิตภัณฑ์
@login_required
def add_product(request):
    if request.user.is_staff or request.user.profile.is_expert:
        if request.method == 'POST':
            form = ProductForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                return redirect('products')
        else:
            form = ProductForm()
        return render(request, 'add_product.html', {'form': form})
    else:
        return redirect('products')

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

# ฟังก์ชันสำหรับแสดงหน้ารายละเอียดสินค้า
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = Review.objects.filter(product=product)
    context = {
        'product': product,
        'reviews': reviews
    }
    return render(request, 'product_detail.html', context)

# ฟังก์ชันสำหรับเพิ่มรีวิว
@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        comment = request.POST.get('comment')
        Review.objects.create(user=request.user, product=product, comment=comment)
    return redirect('product_detail', product_id=product_id)

# ฟังก์ชันลบรีวิว
@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user == review.user:
        product_id = review.product.id
        review.delete()
        messages.success(request, 'ความคิดเห็นของคุณถูกลบแล้ว')
        return redirect('product_detail', product_id=product_id)
    else:
        messages.error(request, 'คุณไม่สามารถลบความคิดเห็นนี้ได้')
        return redirect('product_detail', product_id=review.product.id)
  
# แก้ไขผลิตภัณฑ์
@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.user.is_staff or request.user.profile.is_expert:  # ให้เฉพาะแอดมินและผู้เชี่ยวชาญเท่านั้นที่สามารถแก้ไขได้
        if request.method == 'POST':
            form = ProductForm(request.POST, request.FILES, instance=product)
            if form.is_valid():
                form.save()
                messages.success(request, 'แก้ไขผลิตภัณฑ์สำเร็จ!')
                return redirect('products')
        else:
            form = ProductForm(instance=product)
        return render(request, 'edit_product.html', {'form': form, 'product': product})
    else:
        messages.error(request, 'คุณไม่มีสิทธิ์ในการแก้ไขผลิตภัณฑ์นี้')
        return redirect('products')

# ลบผลิตภัณฑ์
@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.user.is_staff or request.user.profile.is_expert:  # ให้เฉพาะแอดมินและผู้เชี่ยวชาญเท่านั้นที่สามารถลบได้
        if request.method == 'POST':
            product.delete()
            messages.success(request, 'ลบผลิตภัณฑ์สำเร็จ!')
            return redirect('products')
    else:
        messages.error(request, 'คุณไม่มีสิทธิ์ในการลบผลิตภัณฑ์นี้')
        return redirect('products')







