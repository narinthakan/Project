from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Profile, Product, Expert, Seller, SkinUpload, SkinProfile, ExpertResponse,SkinData,ExpertReview,ExpertArticle


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

class SellerProfileForm(forms.ModelForm):
    email = forms.EmailField(required=True, label="อีเมล")  # ดึงจาก User

    class Meta:
        model = Seller
        fields = ['full_name', 'business_name', 'product_category', 'website', 'phone_number', 'profile_picture']

    def __init__(self, *args, **kwargs):
        super(SellerProfileForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        seller = super().save(commit=False)
        if self.cleaned_data.get('email'):
            seller.user.email = self.cleaned_data['email']
            seller.user.username = self.cleaned_data['email']  # Sync username = email
            seller.user.save()
        if commit:
            seller.save()
        return seller


# ฟอร์มสำหรับสินค้า (Product Form)
# class ProductForm(forms.ModelForm):
#     category = forms.ModelChoiceField(
#         queryset=Category.objects.all(),  # ดึงข้อมูลหมวดหมู่จากฐานข้อมูล
#         empty_label="เลือกหมวดหมู่",  # ตัวเลือกเริ่มต้นใน Dropdown
#         required=True,
#         widget=forms.Select(attrs={'class': 'form-select'}),
#         label='หมวดหมู่สินค้า'
#     )
# category_choice=[
    
# ]

    # class Meta:
    #     model = Product
    #     fields = ['name', 'description', 'price', 'image', 'category', 'usage', 'link', 'rating', 'popular']
    #     labels = {
    #         'name': 'ชื่อสินค้า',
    #         'description': 'คำอธิบายสินค้า',
    #         'price': 'ราคา (บาท)',
    #         'image': 'ภาพสินค้า',
    #         'category': 'หมวดหมู่สินค้า',
    #         'usage': 'วิธีการใช้งาน',
    #         'link': 'ลิงก์สำหรับซื้อสินค้า',
    #         'rating': 'คะแนนสินค้า (0-5)',
    #         'popular': 'สินค้ายอดนิยม',
    #     }
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'image', 'category', 'usage', 'link', 'rating', 'popular']
        labels = {
            'name': 'ชื่อสินค้า',
            'description': 'คำอธิบายสินค้า',
            'price': 'ราคา (บาท)',
            'image': 'ภาพสินค้า',
            'category': 'หมวดหมู่สินค้า',
            'usage': 'วิธีการใช้งาน',
            'link': 'ลิงก์สำหรับซื้อสินค้า',
            'rating': 'คะแนนสินค้า (0-5)',
            'popular': 'สินค้ายอดนิยม',
        }
        widgets = {
            'category': forms.Select(choices=Product.TYPE_CHOICES),
            'price': forms.NumberInput(attrs={'step': '0.01'}),
            'rating': forms.NumberInput(attrs={'min': '0', 'max': '5'}),
            'popular': forms.CheckboxInput(),
        }

    def save(self, commit=True, user=None):
        product = super().save(commit=False)
        product.user = user  # ใช้ user ที่ส่งมาจาก views.py
        if commit:
            product.save()
        return product

      

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
    
# ฟังก์ชันตรวจสอบว่ามีอัปโหลดภาพอย่างน้อย 2 ภาพ
def validate_image_count(images):
    if len(images) < 2:
        raise ValidationError("❌ กรุณาอัปโหลดหรือถ่ายภาพอย่างน้อย 2 ภาพ")


# Custom Widget สำหรับอัปโหลดหลายไฟล์
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

    def value_from_datadict(self, data, files, name):
        if hasattr(files, 'getlist'):
            return files.getlist(name)
        return files.get(name)

# ฟอร์มกรอกข้อมูลผิวหน้า
class SkinDataForm(forms.ModelForm):
    class Meta:
        model = SkinData
        fields = ['skin_type', 'concern', 'allergy_history', 'current_products', 'skincare_goal']
        widgets = {
            'concern': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'allergy_history': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'current_products': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'skincare_goal': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }
        labels = {
            'skin_type': 'ประเภทผิว',
            'concern': 'ปัญหาผิวที่กังวล',
            'allergy_history': 'ประวัติการแพ้',
            'current_products': 'ผลิตภัณฑ์ที่ใช้อยู่ในปัจจุบัน',
            'skincare_goal': 'เป้าหมายการดูแลผิว'
        }

class SkinImageForm(forms.Form):
    images = forms.FileField(
        widget=MultipleFileInput(attrs={
            'multiple': True,
            'class': 'form-control',
            'accept': 'image/*'
        }),
        required=False,
        label='รูปภาพผิวหน้า'
    )

    def clean_images(self):
        images = self.files.getlist('images')
        if not images:
            raise forms.ValidationError("❌ กรุณาอัปโหลดรูปภาพ")
        if len(images) < 2:
            raise forms.ValidationError("❌ กรุณาอัปโหลดอย่างน้อย 2 ภาพ")
        
        # ตรวจสอบประเภทไฟล์
        for image in images:
            if not image.content_type.startswith('image/'):
                raise forms.ValidationError("❌ กรุณาอัปโหลดไฟล์รูปภาพเท่านั้น")
            
            # ตรวจสอบขนาดไฟล์ (ไม่เกิน 5MB)
            if image.size > 5 * 1024 * 1024:  # 5MB in bytes
                raise forms.ValidationError("❌ ขนาดไฟล์แต่ละไฟล์ต้องไม่เกิน 5MB")
        
        return images


#สำหรับผู้เชี่ยวชาญตอบปัญหาผิวหน้า
class ExpertResponseForm(forms.ModelForm):
    class Meta:
        model = ExpertResponse
        fields = ['response_text']  # ระบุเฉพาะฟิลด์ response_text
        widgets = {
            'response_text': forms.Textarea(attrs={'rows': 4, 'placeholder': 'เขียนคำตอบที่นี่...'}),
        }    
        
#สำหรับรีวิวผู้เชี่ยวชาญ
class ExpertReviewForm(forms.ModelForm):
    class Meta:
        model = ExpertReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5, 'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'เขียนความเห็นของคุณ'}),
        }
        
#สำหรับเพิ่มหรือแก้ไขบทความผู้เชี่ยวชาญ
class ExpertArticleForm(forms.ModelForm):
    class Meta:
        model = ExpertArticle
        fields = ['title', 'description', 'content', 'image' ]
        

#สำหรับแก้ไขชื่อในใบเกียรติบัตร
class ExpertNameEditForm(forms.ModelForm):
    class Meta:
        model = Expert
        fields = ['full_name']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'กรุณากรอกชื่อใหม่'})
        }