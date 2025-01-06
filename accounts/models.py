from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Avg


# โมเดลสำหรับผู้เชี่ยวชาญ
class Expert(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='expert_profile', null=True)
    full_name = models.CharField(max_length=100, verbose_name="ชื่อ-สกุล")
    license_number = models.CharField(max_length=20, unique=True, verbose_name="เลขใบประกอบวิชาชีพ")
    expertise = models.CharField(max_length=100, verbose_name="ความเชี่ยวชาญ")
    workplace = models.CharField(max_length=100, verbose_name="สถานที่ทำงาน")
    experience = models.TextField(verbose_name="ประสบการณ์การทำงาน")
    profile_image = models.ImageField(upload_to="experts/profile_images", null=True, blank=True, verbose_name="รูปโปรไฟล์")
    is_verified = models.BooleanField(default=False, verbose_name="ยืนยันแล้ว")


# โมเดลสำหรับผู้ขาย
class Seller(models.Model):
    full_name = models.CharField(max_length=255)  # ชื่อ-สกุล
    email = models.EmailField(unique=True)  # อีเมล
    phone_number = models.CharField(max_length=15, blank=True, null=True)  # เบอร์โทรศัพท์
    business_name = models.CharField(max_length=255)  # ชื่อธุรกิจ
    product_category = models.CharField(max_length=255)  # หมวดหมู่สินค้า
    website = models.URLField(blank=True, null=True)  # เว็บไซต์หรือโซเชียลมีเดีย
    product_samples = models.ImageField(upload_to='seller_product_samples/', blank=True, null=True)  # ตัวอย่างสินค้า
    profile_picture = models.ImageField(upload_to='seller_profiles/', blank=True, null=True)  # รูปโปรไฟล์
    created_at = models.DateTimeField(auto_now_add=True)  # วันที่สมัครสมาชิก

    def __str__(self):
        return self.business_name


# โมเดลสำหรับสินค้า
class Product(models.Model):
    name = models.CharField(max_length=200)  # ชื่อสินค้า
    description = models.TextField(blank=True, null=True)  # คำอธิบายสินค้า
    price = models.DecimalField(max_digits=10, decimal_places=2)  # ราคา
    image = models.ImageField(upload_to='products/', blank=True, null=True)  # รูปสินค้า
    rating = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)  # คะแนนเฉลี่ยสินค้า
    popular = models.BooleanField(default=False)  # เป็นสินค้ายอดนิยมหรือไม่
    category = models.CharField(max_length=255, default='Uncategorized')  # หมวดหมู่สินค้า
    
    added_by = models.CharField(
        max_length=50,
        choices=[('Admin', 'Admin'), ('Expert', 'Expert'), ('Seller', 'Seller')],
        default='Admin'
    )

    def __str__(self):
        return self.name

    # ฟังก์ชันคำนวณค่าเฉลี่ยเรตติ้งจากรีวิว
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return reviews.aggregate(Avg('rating'))['rating__avg']
        return 0


# โมเดลสำหรับรีวิว
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # ผู้เขียนรีวิว
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')  # สินค้าที่ถูกรีวิว
    comment = models.TextField()  # ข้อความรีวิว
    rating = models.DecimalField(max_digits=2, decimal_places=1, null=True)  # คะแนนรีวิว
    created_at = models.DateTimeField(auto_now_add=True)  # วันที่สร้างรีวิว

    def __str__(self):
        return f'Review by {self.user.username} on {self.product.name}'


# โมเดลสำหรับโปรไฟล์ผู้ใช้ทั่วไป
class Profile(models.Model):
    ROLE_CHOICES = [
        ('User', 'User'),
        ('Member', 'Member'),
        ('Admin', 'Admin'),
        ('Expert', 'Expert'),
        ('Seller', 'Seller'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')  # เชื่อมกับ User
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='User')  # บทบาทของผู้ใช้
    address = models.CharField(max_length=255, blank=True, null=True)  # ที่อยู่
    phone_number = models.CharField(max_length=20, blank=True, null=True)  # เบอร์โทรศัพท์
    skin_problem = models.TextField(blank=True, null=True)  # ปัญหาผิว
    image = models.ImageField(upload_to='profile_pics/', blank=True, null=True)  # รูปโปรไฟล์
    age = models.IntegerField(blank=True, null=True)  # อายุ
    gender = models.CharField(max_length=10, blank=True, null=True)  # เพศ
    

    def __str__(self):
        return f'{self.user.username} Profile'

#สำหรับเก็บข้อมูลภาพผิวหน้า
class SkinUpload(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)  # เชื่อมโยงกับผู้ใช้
    image = models.ImageField(upload_to='skin_uploads/')      # เก็บใน media/skin_uploads/
    uploaded_at = models.DateTimeField(auto_now_add=True)     # เวลาที่อัปโหลด

    def __str__(self):
        return f"Upload by {self.user.username} on {self.uploaded_at}"
    

# Signals: สร้าง Profile อัตโนมัติเมื่อ User ใหม่ถูกสร้าง
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


# Signals: บันทึก Profile เมื่อ User ถูกอัปเดต
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
