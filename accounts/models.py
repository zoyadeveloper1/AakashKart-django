from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


# =====================================================
# Custom User Manager
# =====================================================
class MyAccountManager(BaseUserManager):

    def create_user(self, first_name, last_name, username, email, password=None):
        if not email:
            raise ValueError("User must have an email address")
        if not username:
            raise ValueError("User must have a username")

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)
        user.is_active = True
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, username, email, password=None):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superadmin = True
        user.is_active = True
        user.save(using=self._db)
        return user


# =====================================================
# Custom User Model
# =====================================================
class Account(AbstractBaseUser):

    # Basic Info
    first_name     = models.CharField(max_length=50)
    last_name      = models.CharField(max_length=50)
    username       = models.CharField(max_length=50, unique=True)
    email          = models.EmailField(max_length=100, unique=True)

    phone_number   = models.CharField(max_length=15, blank=True)

    # 🔥 Profile Fields (Edit Profile)
    address_line_1 = models.CharField(max_length=100, blank=True)
    address_line_2 = models.CharField(max_length=100, blank=True)
    city           = models.CharField(max_length=50, blank=True)
    state          = models.CharField(max_length=50, blank=True)
    country        = models.CharField(max_length=50, blank=True)

    profile_picture = models.ImageField(upload_to='users/', blank=True, null=True)

    # System Fields
    date_joined    = models.DateTimeField(auto_now_add=True)
    last_login     = models.DateTimeField(auto_now_add=True)

    is_admin       = models.BooleanField(default=False)
    is_staff       = models.BooleanField(default=False)
    is_active      = models.BooleanField(default=False)
    is_superadmin  = models.BooleanField(default=False)

    # Auth Settings
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = MyAccountManager()

    def __str__(self):
        return self.email

    # Permissions
    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True


# =====================================================
# Address Model (Multiple addresses support)
# =====================================================
class Address(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='addresses')

    full_name = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address_line = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)

    is_default = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name or "Address"

    class Meta:
        verbose_name = "User Address"
        verbose_name_plural = "User Addresses"