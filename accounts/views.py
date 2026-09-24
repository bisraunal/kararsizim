from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegisterForm, UserLoginForm

def register_view(request):
    if request.user.is_authenticated:
        return redirect('poll_list')
        
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Hoş geldin @{user.username}! Hesabın başarıyla oluşturuldu.")
            return redirect('poll_list')
        else:
            messages.error(request, "Lütfen formu kontrol edip bilgileri eksiksiz doldurun.")
    else:
        form = UserRegisterForm()
        
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('poll_list')
        
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Tekrar hoş geldin @{user.username}!")
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('poll_list')
        else:
            messages.error(request, "Kullanıcı adı veya parola hatalı.")
    else:
        form = UserLoginForm()
        
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "Başarıyla çıkış yaptınız.")
    return redirect('poll_list')


@login_required
def profile_view(request):
    user = request.user
    # Fetch user's polls
    user_polls = user.polls.all().order_by('-created_at')
    total_polls = user_polls.count()
    total_votes_received = sum(poll.total_votes for poll in user_polls)
    
    context = {
        'username': user.username,
        'date_joined': user.date_joined,
        'polls': user_polls,
        'total_polls': total_polls,
        'total_votes_received': total_votes_received,
    }
    return render(request, 'accounts/profile.html', context)
