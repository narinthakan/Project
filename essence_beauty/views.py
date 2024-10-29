# essence_beauty/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import Products



def home(request):
    return render(request, 'home.html')  # เปลี่ยน 'home.html' เป็นชื่อไฟล์เทมเพลตของคุณ

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # เปลี่ยนเส้นทางไปยังหน้า home หลังจากเข้าสู่ระบบ
        else:
            return render(request, 'login.html', {'error': 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง'})
    else:
        return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

# ฟังก์ชันสำหรับการลงทะเบียนผู้ใช้
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'บัญชีของคุณถูกสร้างเรียบร้อยแล้ว คุณสามารถเข้าสู่ระบบได้เลย')
            return redirect('login')  # หลังจากลงทะเบียนเสร็จ กลับไปที่หน้าเข้าสู่ระบบ
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


# ฟังก์ชันสำหรับดึงสินค้ายอดนิยม
def popular_products(request):
    products = Products.objects.filter(popular=True)  # ดึงสินค้าที่เป็นสินค้ายอดนิยม
    return render(request, 'products.html', {'products': products})


