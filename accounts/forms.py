from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Profile, Product, Expert, Seller, SkinUpload, SkinProfile, ExpertResponse,Category,SkinData


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
    email = forms.CharField(label="อีเมล์", max_length=100, required=True)
    password = forms.CharField(label="รหัสผ่าน", max_length=100, required=True)

class ExpertProfileForm(forms.ModelForm):
    class Meta:
        model = Expert
        fields = ['full_name', 'license_number', 'expertise', 'workplace', 'experience', 'profile_image']


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
        
# ฟอร์มตรวจสอบผู้ขาย (Seller Registration)
class SellerLoginForm(forms.Form):
    class Meta:
        model = Seller
        fields = ['is_verified']


# ฟอร์มลงทะเบียนผู้ขาย (Seller Registration)
class SellerRegistrationForm(forms.ModelForm):
    # ฟิลด์ที่เกี่ยวข้องกับ User
    email = forms.EmailField(required=True, label="อีเมล", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(required=True, label="รหัสผ่าน", widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Seller
        fields = ['full_name', 'business_name', 'product_category', 'website', 'phone_number', 'profile_picture', 'product_samples']

    def save(self, commit=True):
        # สร้าง User ก่อน
        user = User.objects.create_user(
            username=self.cleaned_data['email'],  # ใช้ email เป็น username
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password']
        )
        if commit:
            user.save()

        # สร้าง Seller และเชื่อมโยงกับ User
        seller = super().save(commit=False)
        seller.user = user
        if commit:
            seller.save()

        return seller



# ฟอร์มสำหรับสินค้า (Product Form)
class ProductForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label="เลือกหมวดหมู่",  # ข้อความเริ่มต้น
        required=True  # ต้องกรอก
    )

    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'image', 'category', 'usage', 'link', 'rating', 'popular']
        

# ฟอร์มแก้ไขโปรไฟล์ผู้ใช้ (Profile Form)
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
    
#สำหรับผู้ใช้งานกรอกข้อมูลผิวหน้า
class SkinDataForm(forms.ModelForm):
    class Meta:
        model = SkinData
        fields = ['skin_type', 'concern', 'allergy_history', 'current_products', 'skincare_goal', 'skin_image']
        widgets = {
            'concern': forms.Textarea(attrs={'rows': 4}),
            'allergy_history': forms.Textarea(attrs={'rows': 4}),
            'current_products': forms.Textarea(attrs={'rows': 4}),
            'skincare_goal': forms.Textarea(attrs={'rows': 4}),
        }

#สำหรับผู้เชี่ยวชาญตอบปัญหาผิวหน้า
class ExpertResponseForm(forms.ModelForm):
    class Meta:
        model = ExpertResponse
        fields = ['response']
        labels = {'response': 'คำตอบจากผู้เชี่ยวชาญ'}
        widgets = {
            'response': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }      