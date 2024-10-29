from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile,Product  # ใช้ Profile จาก models.py

# ฟอร์มสำหรับการลงทะเบียน
class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
    
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'image', 'rating', 'popular', 'category']    

# ฟอร์มเข้าสู่ระบบ
class LoginForm(forms.Form):
    username = forms.CharField(label="Username")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")

# ฟอร์มแก้ไขโปรไฟล์ รวมทั้งการอัปโหลดรูปภาพและข้อมูลอื่น ๆ
class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, label="ชื่อ")
    last_name = forms.CharField(max_length=30, required=True, label="สกุล")
    email = forms.EmailField(required=True, label="อีเมล")

    class Meta:
        model = Profile  # อ้างอิง Profile จาก models.py
        fields = ['image', 'phone_number', 'address', 'skin_problem', 'age', 'gender']

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        # ตั้งค่าเริ่มต้นให้กับฟิลด์ที่อยู่ในโมเดล User
        self.fields['first_name'].initial = self.instance.user.first_name
        self.fields['last_name'].initial = self.instance.user.last_name
        self.fields['email'].initial = self.instance.user.email

    # ฟังก์ชันนี้เพื่อบันทึกข้อมูลลงในโมเดล User และ Profile
    def save(self, *args, **kwargs):
        user = self.instance.user  # ดึงข้อมูล User ที่เกี่ยวข้อง
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.email = self.cleaned_data.get('email')
        user.save()  # บันทึกข้อมูลของ User
        return super().save(*args, **kwargs)


  
