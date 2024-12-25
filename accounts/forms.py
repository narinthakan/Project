from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Profile, Product, Expert, Seller, SkinUpload


# ฟอร์มสำหรับการลงทะเบียนผู้ใช้ (User)
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


# ฟอร์มเข้าสู่ระบบ (User)
class LoginForm(forms.Form):
    username = forms.CharField(label="ชื่อผู้ใช้", max_length=100)
    password = forms.CharField(widget=forms.PasswordInput, label="รหัสผ่าน")


# ฟอร์มเข้าสู่ระบบผู้เชี่ยวชาญ (Expert Login)
class ExpertLoginForm(forms.Form):
    nm = forms.CharField(label="อีเมล์", max_length=100, required=True)
    lp = forms.CharField(label="รหัสผ่าน", max_length=100, required=True)



# ฟอร์มลงทะเบียนผู้เชี่ยวชาญ (Expert Registration)
class ExpertRegistrationForm(forms.Form):
    full_name = forms.CharField(max_length=100, required=True, label="ชื่อ-สกุล")
    username = forms.CharField(max_length=50, required=True, label="ชื่อผู้ใช้")
    email = forms.EmailField(required=True, label="อีเมล")
    password = forms.CharField(widget=forms.PasswordInput, required=True, label="รหัสผ่าน")
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=True, label="ยืนยันรหัสผ่าน")
    license_number = forms.CharField(max_length=20, required=True, label="เลขใบประกอบวิชาชีพ")
    expertise = forms.CharField(max_length=100, required=True, label="ความเชี่ยวชาญ")
    workplace = forms.CharField(max_length=100, required=True, label="สถานที่ทำงาน")
    experience = forms.CharField(widget=forms.Textarea, required=True, label="ประสบการณ์การทำงาน")
    profile_image = forms.ImageField(required=False, label="รูปโปรไฟล์")

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("รหัสผ่านและยืนยันรหัสผ่านไม่ตรงกัน")
        return cleaned_data



# ฟอร์มตรวจสอบผู้เชี่ยวชาญ (Expert Verification)
class ExpertVerificationForm(forms.ModelForm):
    class Meta:
        model = Expert
        fields = ['is_verified']


# ฟอร์มลงทะเบียนผู้ขาย (Seller Registration)
class SellerRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        label="รหัสผ่าน",
        widget=forms.PasswordInput(attrs={'placeholder': 'รหัสผ่าน', 'class': 'form-control'}),
        required=True
    )
    confirm_password = forms.CharField(
        label="ยืนยันรหัสผ่าน",
        widget=forms.PasswordInput(attrs={'placeholder': 'ยืนยันรหัสผ่าน', 'class': 'form-control'}),
        required=True
    )

    class Meta:
        model = Seller
        fields = [
            'full_name',
            'email',
            'phone_number',
            'business_name',
            'product_category',
            'website',
            'product_samples',
            'profile_picture',
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'ชื่อ-สกุล', 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'placeholder': 'อีเมล', 'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'เบอร์โทรศัพท์', 'class': 'form-control'}),
            'business_name': forms.TextInput(attrs={'placeholder': 'ชื่อธุรกิจ', 'class': 'form-control'}),
            'product_category': forms.TextInput(attrs={'placeholder': 'หมวดหมู่สินค้า', 'class': 'form-control'}),
            'website': forms.URLInput(attrs={'placeholder': 'เว็บไซต์/โซเชียลมีเดีย', 'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("รหัสผ่านและยืนยันรหัสผ่านไม่ตรงกัน")
        return cleaned_data


# ฟอร์มสำหรับสินค้า (Product Form)
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'image', 'rating', 'popular', 'category']


# ฟอร์มแก้ไขโปรไฟล์ผู้ใช้ (Profile)
class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, label="ชื่อ")
    last_name = forms.CharField(max_length=30, required=True, label="สกุล")
    email = forms.EmailField(required=True, label="อีเมล")

    class Meta:
        model = Profile
        fields = ['image', 'phone_number', 'address', 'skin_problem', 'age', 'gender']

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        # ตั้งค่าเริ่มต้นสำหรับข้อมูลจาก User
        self.fields['first_name'].initial = self.instance.user.first_name
        self.fields['last_name'].initial = self.instance.user.last_name
        self.fields['email'].initial = self.instance.user.email

    def save(self, *args, **kwargs):
        user = self.instance.user
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.email = self.cleaned_data.get('email')
        user.save()
        return super().save(*args, **kwargs)
    
#สำหรับอัพโหลดภาพ
class SkinUploadForm(forms.ModelForm):
    class Meta:
        model = SkinUpload
        fields = ['image']    # ฟิลด์ที่ต้องการให้ผู้ใช้อัปโหลด
    
#การจัดการรูปภาพ
def validate_image(image):
    if not image.name.endswith(('.png', '.jpg', '.jpeg')):
        raise ValidationError("กรุณาอัปโหลดไฟล์รูปภาพ (png, jpg, jpeg) เท่านั้น")
       