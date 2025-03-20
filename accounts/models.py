from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Avg

# โมเดลสำหรับโปรไฟล์ผู้ใช้ทั่วไป
class Profile(models.Model):
    ROLE_CHOICES = [
        ('User', 'User'),
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


# Signals: สร้าง Profile อัตโนมัติเมื่อ User ใหม่ถูกสร้าง
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


# Signals: บันทึก Profile เมื่อ User ถูกอัปเดต
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

#โมเดลสำหรับอนุมันคำขอ
class ApprovalRequest(models.Model):
    REQUEST_TYPE_CHOICES = [
        ('Expert', 'Expert'),
        ('Seller', 'Seller'),
    ]
    STATUS_CHOICES = [
        ('รอดำเนินการ', 'รอดำเนินการ'),
        ('อนุมัติ', 'อนุมัติแล้ว'),
        ('ปฏิเสธ', 'ปฏิเสธ'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='approval_requests')  # ผู้ส่งคำขอ
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPE_CHOICES)  # ประเภทคำขอ
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')  # สถานะของคำขอ
    created_at = models.DateTimeField(auto_now_add=True)  # วันที่ส่งคำขอ

    def __str__(self):
        return f"{self.user.username} requests {self.request_type} ({self.status})"


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
    
    def __str__(self):
        return self.full_name


# โมเดลสำหรับผู้ขาย (Seller)
class Seller(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seller_profile', blank=True, null=True)
    full_name = models.CharField(max_length=100, verbose_name="ชื่อ-สกุล")
    business_name = models.CharField(max_length=255, verbose_name="ชื่อธุรกิจ")
    product_category = models.CharField(max_length=255, verbose_name="หมวดหมู่สินค้า")
    website = models.URLField(max_length=500, blank=True, null=True, verbose_name="เว็บไซต์/โซเชียลมีเดีย")
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name="เบอร์โทรศัพท์")
    profile_picture = models.ImageField(upload_to='seller_profiles/', blank=True, null=True, verbose_name="รูปโปรไฟล์")
    product_samples = models.ImageField(upload_to='seller_product_samples/', blank=True, null=True, verbose_name="ตัวอย่างสินค้า")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="วันที่สมัครสมาชิก")
    is_verified = models.BooleanField(default=False, verbose_name="ยืนยันแล้วหรือไม่")

    def __str__(self):
        return self.business_name


# หมวดหมู่สินค้า
# class Category(models.Model):
#     name = models.CharField(max_length=100, verbose_name="ชื่อหมวดหมู่")

#     def __str__(self):
#         return self.name


# โมเดลสำหรับสินค้า
class Product(models.Model):
    TYPE_CHOICES = [
        ('Cleansers', 'คลีนซิ่ง'),
        ('Toners', 'โทนเนอร์'),
        ('Serums', 'เซรั่ม'),
        ('Moisturizers', 'มอยส์เจอไรเซอร์'),
        ('Sunscreens', 'ครีมกันแดด'),
    ]
    name = models.CharField(max_length=200)  # ชื่อสินค้า
    description = models.TextField(blank=True, null=True)  # คำอธิบายสินค้า
    price = models.DecimalField(max_digits=10, decimal_places=2)  # ราคา
    image = models.ImageField(upload_to='products/', blank=True, null=True)  # รูปภาพสินค้า
    category = models.CharField(max_length=100, choices=TYPE_CHOICES)# หมวดหมู่สินค้า
    usage = models.TextField(blank=True, null=True)  # วิธีใช้
    link = models.URLField(max_length=500, blank=True, null=True)  # ลิงก์สำหรับซื้อสินค้า
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="products")  # ผู้เพิ่มสินค้า
    rating = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)  # คะแนนเฉลี่ย
    popular = models.BooleanField(default=False)  # เป็นสินค้ายอดนิยมหรือไม่
    created_at = models.DateTimeField(auto_now_add=True)  # วันที่สร้างสินค้า
    updated_at = models.DateTimeField(auto_now=True)  # วันที่แก้ไขสินค้า

    def __str__(self):
        return self.name
    

    # ฟังก์ชันคำนวณค่าเฉลี่ยเรตติ้งจากรีวิว
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return reviews.aggregate(Avg('rating'))['rating__avg']
        return 0



# โมเดลสำหรับรีวิวผลิตภัณฑ์
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # ผู้เขียนรีวิว
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')  # สินค้าที่ถูกรีวิว
    comment = models.TextField()  # ข้อความรีวิว
    rating = models.DecimalField(max_digits=2, decimal_places=1, null=True)  # คะแนนรีวิว
    created_at = models.DateTimeField(auto_now_add=True)  # วันที่สร้างรีวิว

    def __str__(self):
        return f'Review by {self.user.username} on {self.product.name}'


# สำหรับเก็บข้อมูลภาพผิวหน้า
class SkinUpload(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name="skin_uploads")  # เชื่อมโยงกับผู้ใช้
    image = models.ImageField(upload_to='skin_uploads/')  # เก็บใน media/skin_uploads/
    uploaded_at = models.DateTimeField(auto_now_add=True)  # เวลาที่อัปโหลด

    def __str__(self):
        return f"Upload by {self.user.username} on {self.uploaded_at}"


# สำหรับข้อมูลผิวหน้าของผู้ใช้งาน
class SkinData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="skin_data")
    skin_type = models.CharField(max_length=50, blank=True, null=True)
    concern = models.TextField(blank=True, null=True)
    allergy_history = models.TextField(blank=True, null=True)
    current_products = models.TextField(blank=True, null=True)
    skincare_goal = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"SkinData of {self.user.username}"


class SkinImage(models.Model):
    skin_data = models.ForeignKey(SkinData, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="skin_images/")

    def __str__(self):
        return f"Image for {self.skin_data.user.username}"
    
# สำหรับข้อมูลคำตอบจากผู้เชี่ยวชาญ
class ExpertResponse(models.Model):
    skin_data = models.ForeignKey('SkinData', on_delete=models.CASCADE, related_name='responses')  # Many-to-One
    expert = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expert_responses')  # ผู้เชี่ยวชาญ
    response_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Response by {self.expert.username} for {self.skin_data.id}"

# สำหรับรีวิวผู้เชี่ยวชาญ
class ExpertReview(models.Model):
    expert = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')  # ผู้เชี่ยวชาญ
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_reviews')  # ผู้รีวิว
    rating = models.PositiveIntegerField()  # คะแนน (1-5 ดาว)
    comment = models.TextField(blank=True, null=True)  # ความคิดเห็น
    created_at = models.DateTimeField(auto_now_add=True)  # วันที่รีวิว

    def __str__(self):
        return f"Review by {self.user.username} for {self.expert.username}"

# สำหรับข้อมูลผิวหน้า
class SkinProfile(models.Model):
    SKIN_TYPE_CHOICES = [
        ('normal', 'ผิวธรรมดา'),
        ('oily', 'ผิวมัน'),
        ('dry', 'ผิวแห้ง'),
        ('combination', 'ผิวผสม'),
        ('sensitive', 'ผิวแพ้ง่าย'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skin_profiles')
    skin_type = models.CharField(max_length=20, choices=SKIN_TYPE_CHOICES)
    concern = models.TextField(blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    current_products = models.TextField(blank=True, null=True)
    skincare_goal = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.skin_type}"

# สำหรับบทความของผู้เชี่ยวชาญ
class ExpertArticle(models.Model):
    expert = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    image = models.ImageField(upload_to='articles/', null=True, blank=True)  # ฟิลด์สำหรับอัปโหลดรูป
    description = models.TextField(null=True, blank=True)  # ฟิลด์สำหรับคำอธิบาย
    how_to_check = models.TextField(null=True, blank=True)  # ฟิลด์สำหรับวิธีเช็ค

    def __str__(self):
        return self.title
    
# โมเดลสำหรับเก็บรีวิวของผู้เชี่ยวชาญ
# class ExpertReview(models.Model):
#     expert = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_reviews')
#     rating = models.PositiveIntegerField()  # คะแนน (1-5 ดาว)
#     comment = models.TextField(blank=True, null=True)  # ความคิดเห็น
#     created_at = models.DateTimeField(auto_now_add=True)  # วันที่รีวิว

#     def __str__(self):
#         return f"Review by {self.user.username} for {self.expert.username}"

# โมเดลสำหรับเกียรติบัตร
class Certificate(models.Model):
    expert = models.OneToOneField(User, on_delete=models.CASCADE, related_name="certificate")
    average_rating = models.FloatField()  # คะแนนเฉลี่ย
    total_reviews = models.PositiveIntegerField()  # จำนวนรีวิวทั้งหมด
    issue_date = models.DateField(auto_now_add=True)  # วันที่ออกใบเกียรติบัตร
    certificate_file = models.FileField(upload_to='certificates/', null=True, blank=True)  # สำหรับเก็บไฟล์ใบเกียรติบัตร PDF

    def __str__(self):
        return f"Certificate for {self.expert.username}"

    def is_eligible_for_certificate(self):
        # ตรวจสอบว่าได้รับคะแนนรีวิว 4-5 และจำนวนรีวิวขั้นต่ำ 30 รีวิว
        if self.average_rating >= 4 and self.total_reviews >= 30:
            return True
        return False