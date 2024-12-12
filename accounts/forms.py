from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile,Product,Expert  # ใช้ Profile จาก models.py


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

class ExpertLoginForm(forms.Form):
    nm = forms.CharField(label="ชื่อ", max_length=100, required=True)
    lp = forms.CharField(label="นามสกุล", max_length=100, required=True)
    codepce = forms.CharField(label="เลขใบประกอบวิชาชีพ", max_length=10, required=True)

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
    
    #ฟอร์มผู้เชี่ยวชาญ
class ExpertRegistrationForm(forms.Form):
    full_name = forms.CharField(max_length=100, required=True, label="ชื่อ-สกุล")
    username = forms.CharField(max_length=50, required=True, label="ชื่อผู้ใช้")
    email = forms.EmailField(required=True, label="อีเมล")
    password = forms.CharField(widget=forms.PasswordInput, required=True, label="รหัสผ่าน")
    license_number = forms.CharField(max_length=20, required=True, label="เลขใบประกอบวิชาชีพ")
    expertise = forms.CharField(max_length=100, required=True, label="ความเชี่ยวชาญ")
    workplace = forms.CharField(max_length=100, required=True, label="สถานที่ทำงานปัจจุบัน")
    experience = forms.CharField(widget=forms.Textarea, required=True, label="ประสบการณ์การทำงาน")
    profile_image = forms.ImageField(required=False, label="รูปโปรไฟล์") 
    
    
#ตรวจสอบผู้เชี่ยวชาญ
class ExpertVerificationForm(forms.ModelForm):
    class Meta:
        model = Expert
        fields = ['is_verified']

    
    



  
