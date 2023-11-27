import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from stdimage.models import StdImageField

def get_file_path(_instance, filename):
    ext = filename.split('.')[-1]
    filename = f'image_users/{uuid.uuid4()}.{ext}'
    return filename

def user_directory_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'image_users/{uuid.uuid4()}.{ext}'
    return filename

class UsuarioManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('O e-mail é obrigatório')
        email = self.normalize_email(email)
        user = self.model(email=email, username=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)
    
    def create_superuser(self, email, password=None, **extra_fields): #cria um super usuário, que por padrão deve ter True em is_superuser e is_staff
        extra_fields.setdefault('is_superuser', True) #poderia setar true depois de confirmar e-mail
        extra_fields.setdefault('is_staff', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser precisa ter is_superuser=True')
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser precisa ter is_staff=True')

        return self._create_user(email, password, **extra_fields) 

class CustomUser(AbstractUser):
    email = models.EmailField(verbose_name='E-mail', unique=True, help_text='E-mail', db_column='email')
    is_staff = models.BooleanField(verbose_name='Member', default=True)
    #image = StdImageField('Imagem', upload_to=get_file_path, variations={'thumb': {'width': 480, 'height': 480, 'crop': True}})
    image = models.ImageField(verbose_name='Imagem', default='image_users/default.png', upload_to=user_directory_path, db_column='image')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    def __str__(self):
        return self.email
    
    def get_image(self):
        return self.image
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_email(self):
        return self.email

    objects = UsuarioManager()