from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Avg  # ใช้สำหรับการคำนวณค่าเฉลี่ยใน Product

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        permissions = [
            ("add_product", "Can add a product"),
            ("change_product", "Can change a product"),
            ("delete_product", "Can delete a product"),
            ("view_product", "Can view a product"),
        ]

#ตรวจสอบสถานะของผู้เชี่ยวชาญ
class Expert(models.Model):
    full_name = models.CharField(max_length=255)
    username = models.CharField(max_length=255, unique=True)
    license_number = models.CharField(max_length=255)
    expertise = models.CharField(max_length=255)
    workplace = models.CharField(max_length=255)
    experience = models.TextField()
    email = models.EmailField()
    password = models.CharField(max_length=255)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)  # สถานะการตรวจสอบ

    def __str__(self):
        return self.full_name

# โมเดลสำหรับข้อมูลสินค้า
class Product(models.Model):
    name = models.CharField(max_length=200)  # ชื่อสินค้า
    description = models.TextField(blank=True, null=True)  # คำอธิบาย
    price = models.DecimalField(max_digits=10, decimal_places=2)  # ราคา
    image = models.ImageField(upload_to='products/', blank=True, null=True)  # รูปสินค้า
    rating = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)  # คะแนนเรตติ้ง
    popular = models.BooleanField(default=False)  # เป็นสินค้ายอดนิยมหรือไม่
    category = models.CharField(max_length=255, default='Uncategorized')  # หมวดหมู่สินค้า

    def __str__(self):
        return self.name

    # ฟังก์ชันคำนวณคะแนนเฉลี่ยของรีวิว
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return reviews.aggregate(Avg('rating'))['rating__avg']  # คำนวณค่าเฉลี่ยจากฟิลด์ rating ใน Review
        return 0  # ถ้าไม่มีรีวิวใดๆ ให้ค่าเฉลี่ยเป็น 0

# โมเดลสำหรับข้อมูลโปรไฟล์ผู้ใช้ รวมฟิลด์ role เพื่อกำหนดสิทธิ์
class Profile(models.Model):
    ROLE_CHOICES = [
        ('User', 'User'),
        ('Member', 'Member'),
        ('Admin', 'Admin'),
        ('Expert', 'Expert'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')  # เชื่อมโยงกับ User
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='User')  # ระบุ Role ของผู้ใช้
    address = models.CharField(max_length=255, blank=True, null=True)  # ที่อยู่
    phone_number = models.CharField(max_length=20, blank=True, null=True)  # เบอร์โทรศัพท์
    skin_problem = models.TextField(blank=True, null=True)  # ปัญหาผิว
    image = models.ImageField(upload_to='profile_pics', blank=True, null=True)  # รูปโปรไฟล์
    age = models.IntegerField(blank=True, null=True)  # อายุ
    gender = models.CharField(max_length=10, blank=True, null=True)  # เพศ

    def __str__(self):
        return f'{self.user.username} Profile'

    # Methods สำหรับตรวจสอบบทบาท (Role) ของผู้ใช้
    def is_user(self):
        return self.role == 'User'

    def is_member(self):
        return self.role == 'Member'

    def is_admin(self):
        return self.role == 'Admin'

    def is_expert(self):
        return self.role == 'Expert'

# โมเดลสำหรับรีวิวที่เชื่อมโยงกับผู้ใช้ (User) และผลิตภัณฑ์ (Product)
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # ผู้ใช้ที่เขียนรีวิว
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')  # เชื่อมโยงกับผลิตภัณฑ์ที่รีวิว
    comment = models.TextField()  # ข้อความรีวิว
    rating = models.DecimalField(max_digits=2, decimal_places=1, null=True)  # คะแนนรีวิว
    created_at = models.DateTimeField(auto_now_add=True)  # เวลาที่สร้างรีวิว

    def __str__(self):
        return f'Review by {self.user.username} on {self.product.name}'

# สร้าง Profile อัตโนมัติเมื่อ User ใหม่ถูกสร้าง
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# บันทึก Profile เมื่อมีการอัปเดต User
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


#สำหรับเก็บข้อมูลผู้ขาย
class Seller(models.Model):
    full_name = models.CharField(max_length=255)  # ชื่อ-สกุล
    email = models.EmailField(unique=True)  # อีเมล
    phone_number = models.CharField(max_length=15, blank=True, null=True)  # เบอร์โทรศัพท์
    business_name = models.CharField(max_length=255)  # ชื่อธุรกิจ/แบรนด์
    product_category = models.CharField(max_length=255)  # หมวดหมู่สินค้า
    website = models.URLField(blank=True, null=True)  # ลิงก์เว็บไซต์หรือโซเชียลมีเดีย
    product_samples = models.ImageField(upload_to='seller_product_samples/', blank=True, null=True)  # ตัวอย่างสินค้า
    profile_picture = models.ImageField(upload_to='seller_profiles/', blank=True, null=True)  # รูปโปรไฟล์
    created_at = models.DateTimeField(auto_now_add=True)  # วันที่สมัคร

    def __str__(self):
        return self.business_name

    