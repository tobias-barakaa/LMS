from django.shortcuts import render
from api.serializer import MyTokenObtainPairSerializer, RegisterSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from userauths.models import User, Profile
from rest_framework.permissions import AllowAny
from api.serializer import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

def generate_random_otp(length=6):
    import random
    otp = ''.join([str(random.randint(0, 9)) for _ in range(length)])
    return otp
    
class PasswordResetEmailVerifyAPIView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer
    
    def get_object(self):
        email = self.kwargs.get('email')
        try:
            user = User.objects.get(email=email)
            if user:
                
                uuidb64 = user.pk
                refresh = RefreshToken.for_user(user)
                refresh_token = str(refresh.access_token)
                user.refresh_token = refresh_token
                user.otp = generate_random_otp()
                user.save()
                
                
                
                link = f"http://localhost:5173/create-new-password/?otp={user.otp}&uuidb64={uuidb64}&refresh_token={refresh_token}"
                print(link, 'linkss')            
            return user
        except User.DoesNotExist:
            return None

class PasswordChangeAPIView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer
    
    def create(self, request, *args, **kwargs):
        data = request.data
        otp = data.get('otp')
        uuidb64 = data.get('uuidb64')
        refresh_token = data.get('refresh_token')
        password = data.get('password')
        password2 = data.get('password2')
        
        try:
            user = User.objects.get(pk=uuidb64)
            if user.otp == otp and user.refresh_token == refresh_token:
                if password == password2:
                    user.set_password(password)
                    user.save()
                    return user
                else:
                    return {'error': 'Password did not match'}
            else:
                return {'error': 'Invalid OTP or Refresh Token'}
        except User.DoesNotExist:
            return {'error': 'User does not exist'}
        
        return super().create(request, *args, **kwargs)