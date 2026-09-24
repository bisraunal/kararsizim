import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Count, Q
from django.db import transaction, IntegrityError
from django.contrib import messages
from .models import Poll, Option, Vote
from .forms import PollCreateForm

def _get_session_key(request):
    """Ensures a session exists and returns the session_key."""
    if not request.session.session_key:
        request.session.save()
    return request.session.session_key


def poll_list_view(request):
    filter_type = request.GET.get('filter', 'latest')
    category = request.GET.get('category', '')
    query = request.GET.get('q', '').strip()

    polls = Poll.objects.filter(is_active=True).select_related('user').prefetch_related('options', 'votes')

    if category:
        polls = polls.filter(category=category)

    if query:
        polls = polls.filter(
            Q(question__icontains=query) | Q(description__icontains=query)
        )

    if filter_type == 'popular':
        polls = polls.annotate(num_votes=Count('votes')).order_by('-num_votes', '-created_at')
    else:
        polls = polls.order_by('-created_at')

    session_key = _get_session_key(request)
    user = request.user if request.user.is_authenticated else None

    # Attach voter state to each poll for fast rendering
    poll_list_data = []
    for poll in polls:
        user_voted = False
        voted_option_id = None
        user_vote = poll.get_user_vote(user=user, session_key=session_key)
        if user_vote:
            user_voted = True
            voted_option_id = user_vote.option_id

        total_v = poll.total_votes
        options_data = []
        for opt in poll.options.all():
            opt_count = opt.votes.count()
            pct = round((opt_count / total_v * 100), 1) if total_v > 0 else 0
            options_data.append({
                'id': opt.id,
                'text': opt.text,
                'vote_count': opt_count,
                'percentage': pct,
                'is_chosen': (opt.id == voted_option_id),
            })

        poll_list_data.append({
            'poll': poll,
            'user_voted': user_voted,
            'voted_option_id': voted_option_id,
            'total_votes': total_v,
            'options': options_data,
        })

    categories = Poll.CATEGORY_CHOICES

    context = {
        'polls_data': poll_list_data,
        'current_filter': filter_type,
        'current_category': category,
        'search_query': query,
        'categories': categories,
    }
    return render(request, 'polls/poll_list.html', context)


def poll_detail_view(request, pk):
    poll = get_object_or_404(Poll.objects.select_related('user').prefetch_related('options', 'votes'), pk=pk)
    session_key = _get_session_key(request)
    user = request.user if request.user.is_authenticated else None

    user_voted = False
    voted_option_id = None
    user_vote = poll.get_user_vote(user=user, session_key=session_key)
    if user_vote:
        user_voted = True
        voted_option_id = user_vote.option_id

    total_v = poll.total_votes
    options_data = []
    for opt in poll.options.all():
        opt_count = opt.votes.count()
        pct = round((opt_count / total_v * 100), 1) if total_v > 0 else 0
        options_data.append({
            'id': opt.id,
            'text': opt.text,
            'vote_count': opt_count,
            'percentage': pct,
            'is_chosen': (opt.id == voted_option_id),
        })

    context = {
        'poll': poll,
        'user_voted': user_voted,
        'voted_option_id': voted_option_id,
        'total_votes': total_v,
        'options': options_data,
    }
    return render(request, 'polls/poll_detail.html', context)


@login_required
def poll_create_view(request):
    if request.method == 'POST':
        form = PollCreateForm(request.POST)
        option_texts = [text.strip() for text in request.POST.getlist('options[]') if text.strip()]
        
        # Fallback for plain named inputs
        if not option_texts:
            for key in sorted(request.POST.keys()):
                if key.startswith('option_') and request.POST[key].strip():
                    option_texts.append(request.POST[key].strip())

        if len(option_texts) < 2:
            messages.error(request, "En az 2 seçenek belirtmelisiniz.")
        elif len(option_texts) > 5:
            messages.error(request, "En fazla 5 seçenek ekleyebilirsiniz.")
        elif form.is_valid():
            with transaction.atomic():
                poll = form.save(commit=False)
                poll.user = request.user
                poll.save()

                for index, opt_text in enumerate(option_texts, start=1):
                    Option.objects.create(
                        poll=poll,
                        text=opt_text,
                        order=index
                    )

            messages.success(request, "Kararsızlığın başarıyla paylaşıldı! Bakalım topluluk ne diyecek.")
            return redirect('poll_detail', pk=poll.pk)
    else:
        form = PollCreateForm()
        option_texts = ['', '']

    return render(request, 'polls/poll_create.html', {
        'form': form,
        'initial_options': option_texts,
    })


@require_POST
def vote_api_view(request, pk):
    poll = get_object_or_404(Poll, pk=pk)

    if not poll.is_active:
        return JsonResponse({'success': False, 'message': 'Bu anket artık oylamaya kapalı.'}, status=400)

    session_key = _get_session_key(request)
    user = request.user if request.user.is_authenticated else None

    # Check if already voted (Strict Single-Vote policy)
    if poll.user_has_voted(user=user, session_key=session_key):
        return JsonResponse({'success': False, 'message': 'Bu ankete daha önce oy verdiniz. Oylama kesindir.'}, status=400)

    # Get option ID from POST data (JSON or Form)
    option_id = request.POST.get('option_id')
    if not option_id and request.body:
        try:
            body_data = json.loads(request.body)
            option_id = body_data.get('option_id')
        except Exception:
            pass

    if not option_id:
        return JsonResponse({'success': False, 'message': 'Geçerli bir seçenek seçilmedi.'}, status=400)

    option = get_object_or_404(Option, pk=option_id, poll=poll)

    try:
        with transaction.atomic():
            Vote.objects.create(
                poll=poll,
                option=option,
                user=user,
                session_key=session_key if not user else None
            )
    except IntegrityError:
        return JsonResponse({'success': False, 'message': 'Bu ankete daha önce oy verdiniz.'}, status=400)

    # Calculate latest stats
    total_votes = poll.total_votes
    options_data = []
    for opt in poll.options.all():
        count = opt.votes.count()
        pct = round((count / total_votes * 100), 1) if total_votes > 0 else 0
        options_data.append({
            'id': opt.id,
            'text': opt.text,
            'votes': count,
            'percentage': pct,
            'is_chosen': (opt.id == option.id),
        })

    return JsonResponse({
        'success': True,
        'message': 'Oyunuz başarıyla kaydedildi!',
        'poll_id': poll.id,
        'total_votes': total_votes,
        'chosen_option_id': option.id,
        'options': options_data,
    })


@login_required
@require_POST
def toggle_poll_status_view(request, pk):
    poll = get_object_or_404(Poll, pk=pk, user=request.user)
    poll.is_active = not poll.is_active
    poll.save()
    status_text = "açıldı" if poll.is_active else "kapatıldı"
    messages.success(request, f"Anket başarıyla oylamaya {status_text}.")
    return redirect(request.META.get('HTTP_REFERER', 'profile'))


@login_required
@require_POST
def delete_poll_view(request, pk):
    poll = get_object_or_404(Poll, pk=pk, user=request.user)
    poll.delete()
    messages.success(request, "Anket başarıyla silindi.")
    return redirect('profile')
