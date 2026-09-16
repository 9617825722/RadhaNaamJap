from datetime import timedelta

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.db.models import Sum
from django.utils import timezone

from .models import JapRecord


def home(request):
    top_users = User.objects.annotate(
        total_jap=Sum('japrecord__count')
    ).filter(
        total_jap__gt=0
    ).order_by('-total_jap')[:3]

    return render(request, 'home.html', {
        'top_users': top_users
    })


def get_level_data(total_jap):

    level_1 = 10000000
    level_2 = 50000000
    level_3 = 70000000

    level_1_completed = total_jap >= level_1
    level_2_completed = total_jap >= level_2
    level_3_completed = total_jap >= level_3

    if total_jap < level_1:

        current_level = 1
        level_name = "Level 1"
        current_target = level_1
        previous_target = 0
        next_level = "Level 2"

    elif total_jap < level_2:

        current_level = 2
        level_name = "Level 2"
        current_target = level_2
        previous_target = level_1
        next_level = "Level 3"

    elif total_jap < level_3:

        current_level = 3
        level_name = "Level 3"
        current_target = level_3
        previous_target = level_2
        next_level = "Completed"

    else:

        current_level = 3
        level_name = "All 3 Levels Completed"
        current_target = level_3
        previous_target = level_2
        next_level = "Completed"

    if total_jap >= level_3:

        progress = 100

    else:

        progress = int(
            (
                (total_jap - previous_target)
                /
                (current_target - previous_target)
            ) * 100
        )

        progress = max(0, min(progress, 100))

    if level_3_completed:

        completion_message = "🏆 All 3 Levels Completed! Radha Naam Jap Yatra Complete! 🙏"

    elif level_2_completed:

        completion_message = "🎉 Level 2 Completed! Level 3 is now unlocked! 🪈"

    elif level_1_completed:

        completion_message = "🎉 Level 1 Completed! Level 2 is now unlocked! 🦚"

    else:

        completion_message = ""

    return {
        'current_level': current_level,
        'level_name': level_name,
        'current_target': current_target,
        'previous_target': previous_target,
        'progress': progress,
        'next_level': next_level,

        'level_1_target': level_1,
        'level_2_target': level_2,
        'level_3_target': level_3,

        'level_1_completed': level_1_completed,
        'level_2_completed': level_2_completed,
        'level_3_completed': level_3_completed,

        'level_2_unlocked': level_1_completed,
        'level_3_unlocked': level_2_completed,

        'completion_message': completion_message,

        'completed_levels': sum([
            level_1_completed,
            level_2_completed,
            level_3_completed
        ])
    }


def get_stats(user):

    today = timezone.localdate()

    record, created = JapRecord.objects.get_or_create(
        user=user,
        date=today
    )

    total_jap = JapRecord.objects.filter(
        user=user
    ).aggregate(
        total=Sum('count')
    )['total'] or 0

    history = JapRecord.objects.filter(
        user=user,
        count__gt=0
    ).order_by('-date')

    streak = 0
    check_date = today

    for item in history:

        if item.date == check_date:

            streak += 1
            check_date -= timedelta(days=1)

        elif item.date < check_date:

            break

    total_mala = total_jap // 108
    today_mala = record.count // 108

    return record, total_jap, streak, total_mala, today_mala


@never_cache
@login_required
def dashboard(request):

    record, total_jap, streak, total_mala, today_mala = get_stats(
        request.user
    )

    level_data = get_level_data(total_jap)

    today = timezone.localdate()

    stats = []

    for i in range(6, -1, -1):

        date = today - timedelta(days=i)

        count = JapRecord.objects.filter(
            user=request.user,
            date=date
        ).aggregate(
            total=Sum('count')
        )['total'] or 0

        stats.append({
            'date': date.strftime('%d %b'),
            'count': count
        })

    max_count = max(
        [item['count'] for item in stats],
        default=1
    )

    for item in stats:

        if item['count'] > 0:

            item['height'] = max(
                int((item['count'] / max_count) * 200),
                10
            )

        else:

            item['height'] = 5

    return render(request, 'dashboard.html', {
        'record': record,
        'total_jap': total_jap,
        'streak': streak,
        'stats': stats,

        'total_mala': total_mala,
        'today_mala': today_mala,

        'level_data': level_data
    })


@login_required
def set_target(request):

    if request.method == 'POST':

        target = request.POST.get('target')

        if target and target.isdigit() and int(target) > 0:

            record, created = JapRecord.objects.get_or_create(
                user=request.user,
                date=timezone.localdate()
            )

            record.target = int(target)
            record.save()

        return redirect('dashboard')

    return redirect('dashboard')


@login_required
def add_jap(request):

    if request.method == 'POST':

        record, created = JapRecord.objects.get_or_create(
            user=request.user,
            date=timezone.localdate()
        )

        record.count += 1
        record.save()

    return redirect('dashboard')


def register(request):

    if request.method == 'POST':

        name = request.POST.get('name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:

            messages.error(
                request,
                'Passwords do not match.'
            )

            return redirect('register')

        if User.objects.filter(username=username).exists():

            messages.error(
                request,
                'Username already exists.'
            )

            return redirect('register')

        User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=name
        )

        messages.success(
            request,
            'Registration successful! Please login.'
        )

        return redirect('login')

    return render(request, 'register.html')


def login(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            auth_login(request, user)

            return redirect('dashboard')

        messages.error(
            request,
            'Invalid username or password.'
        )

    return render(request, 'login.html')


def logout(request):

    auth_logout(request)

    return redirect('home')


@login_required
def jap_history(request):

    history = JapRecord.objects.filter(
        user=request.user
    ).order_by('-date')

    return render(request, 'jap_history.html', {
        'history': history
    })


@login_required
def achievements(request):

    record, total_jap, streak, total_mala, today_mala = get_stats(
        request.user
    )

    achievement_data = [
        {
            'icon': '📿',
            'title': 'First Jap',
            'description': 'Complete your first Naam Jap.',
            'unlocked': total_jap >= 1
        },
        {
            'icon': '🌸',
            'title': '108 Jap',
            'description': 'Complete 108 total Naam Jap.',
            'unlocked': total_jap >= 108
        },
        {
            'icon': '🪷',
            'title': '500 Jap',
            'description': 'Complete 500 total Naam Jap.',
            'unlocked': total_jap >= 500
        },
        {
            'icon': '🏆',
            'title': '1000 Jap',
            'description': 'Complete 1000 total Naam Jap.',
            'unlocked': total_jap >= 1000
        },
        {
            'icon': '🔥',
            'title': '3 Day Streak',
            'description': 'Maintain a 3-day Naam Jap streak.',
            'unlocked': streak >= 3
        },
        {
            'icon': '👑',
            'title': '7 Day Streak',
            'description': 'Maintain a 7-day Naam Jap streak.',
            'unlocked': streak >= 7
        }
    ]

    return render(request, 'achievements.html', {
        'achievements': achievement_data,
        'total_jap': total_jap,
        'streak': streak
    })


@login_required
def naam_jap_info(request):

    return render(request, 'naam_jap_info.html')


@login_required
def profile(request):

    record, total_jap, streak, total_mala, today_mala = get_stats(
        request.user
    )

    level_data = get_level_data(total_jap)

    return render(request, 'profile.html', {
        'total_jap': total_jap,
        'streak': streak,
        'total_mala': total_mala,
        'today_mala': today_mala,
        'level_data': level_data
    })


@login_required
def daily_goal(request):

    record, total_jap, streak, total_mala, today_mala = get_stats(
        request.user
    )

    if request.method == 'POST':

        target = request.POST.get('target')

        if target and target.isdigit() and int(target) > 0:

            record.target = int(target)
            record.save()

            messages.success(
                request,
                'Daily goal updated successfully.'
            )

            return redirect('daily_goal')

        messages.error(
            request,
            'Please enter a valid target.'
        )

    return render(request, 'daily_goal.html', {
        'record': record
    })


@login_required
def settings_view(request):

    if request.method == 'POST':

        action = request.POST.get('action')

        if action == 'profile':

            request.user.first_name = request.POST.get(
                'first_name',
                ''
            ).strip()

            request.user.email = request.POST.get(
                'email',
                ''
            ).strip()

            request.user.save()

            messages.success(
                request,
                'Profile settings updated successfully.'
            )

        elif action == 'password':

            current_password = request.POST.get(
                'current_password'
            )

            new_password = request.POST.get(
                'new_password'
            )

            confirm_password = request.POST.get(
                'confirm_password'
            )

            if not request.user.check_password(
                current_password
            ):

                messages.error(
                    request,
                    'Current password is incorrect.'
                )

            elif new_password != confirm_password:

                messages.error(
                    request,
                    'New passwords do not match.'
                )

            elif len(new_password) < 8:

                messages.error(
                    request,
                    'New password must be at least 8 characters.'
                )

            else:

                request.user.set_password(new_password)
                request.user.save()

                update_session_auth_hash(
                    request,
                    request.user
                )

                messages.success(
                    request,
                    'Password changed successfully.'
                )

        return redirect('settings')

    return render(request, 'settings.html')

@login_required
def level_1(request):

    record, total_jap, streak, total_mala, today_mala = get_stats(
        request.user
    )

    if total_jap < 10000000:
        return redirect('dashboard')

    return render(request, 'level_1.html', {
        'total_jap': total_jap,
        'total_mala': total_mala,
        'level_data': get_level_data(total_jap)
    })


@login_required
def level_2(request):

    record, total_jap, streak, total_mala, today_mala = get_stats(
        request.user
    )

    if total_jap < 10000000:
        return redirect('dashboard')

    return render(request, 'level_2.html', {
        'total_jap': total_jap,
        'total_mala': total_mala,
        'level_data': get_level_data(total_jap)
    })


@login_required
def level_3(request):

    record, total_jap, streak, total_mala, today_mala = get_stats(
        request.user
    )

    if total_jap < 50000000:
        return redirect('dashboard')

    return render(request, 'level_3.html', {
        'total_jap': total_jap,
        'total_mala': total_mala,
        'level_data': get_level_data(total_jap)
    })