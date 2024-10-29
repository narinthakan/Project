from django.db import models
from django.contrib.auth.models import User

# Create your models here.

# models.py

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

# โมเดลสำหรับข้อมูลโปรไฟล์ผู้ใช้ รวมทุกฟิลด์ที่ต้องการไว้ในโมเดลเดียว
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')  # เชื่อมโยงกับ User
    address = models.CharField(max_length=255, blank=True, null=True)  # ที่อยู่
    phone_number = models.CharField(max_length=20, blank=True, null=True)  # เบอร์โทรศัพท์
    skin_problem = models.TextField(blank=True, null=True)  # ปัญหาผิว
    image = models.ImageField(upload_to='profile_pics', blank=True, null=True)  # รูปโปรไฟล์
    age = models.IntegerField(blank=True, null=True)  # อายุ
    gender = models.CharField(max_length=10, blank=True, null=True)  # เพศ

    def __str__(self):
        return f'{self.user.username} Profile'

# โมเดลสำหรับรีวิวที่เชื่อมโยงกับผู้ใช้ (User) และผลิตภัณฑ์ (Product)
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review by {self.user.username} on {self.product.name}'
    