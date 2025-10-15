from django.shortcuts import render, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta

from .forms import RegistrationForm, PollForm, ChoiceForm
from .forms import ProfileUpdateForm
from .models import Question, Choice, User, Vote
from django.template import loader
from django.urls import reverse
from django.views import generic

def registration(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return HttpResponseRedirect('/')
    else:
        form = RegistrationForm()

    return render(request, 'registration/registration.html', {'form': form})


@login_required
def profile_view(request):
    if request.method == 'POST':
        if 'delete_account' in request.POST:
            user = request.user
            user.delete()
            logout(request)
            return HttpResponseRedirect('/')
        else:
            form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
            if form.is_valid():
                form.save()
                return redirect('polls:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'polls/profile.html', {'form': form})


@login_required
def create_poll_view(request):
    if request.method == 'POST':
        poll_form = PollForm(request.POST, request.FILES)
        choice_form = ChoiceForm(request.POST)

        if poll_form.is_valid() and choice_form.is_valid():
            poll = poll_form.save(commit=False)
            poll.pub_date = timezone.now()
            poll.save()
            poll.expires_at = timezone.now() + timedelta(hours=12)
            poll.save()

            choices = choice_form.save(commit=False)
            for choice in choices:
                choice.question = poll
                choice.save()

            return redirect('polls:index')
    else:
        poll_form = PollForm()
        choice_form = ChoiceForm()

    return render(request, 'polls/create_poll.html', {
        'poll_form': poll_form,
        'choice_form': choice_form
    })


class PollsListView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Question.objects.order_by('-pub_date')
        else:
            return Question.objects.filter(expires_at__isnull=True).exclude(
                expires_at__lt=timezone.now()
            ).order_by('-pub_date')


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Question.objects.all()
        else:
            return Question.objects.filter(expires_at__isnull=True).exclude(
                expires_at__lt=timezone.now()
            )


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        question = self.get_object()
        choices = question.choice_set.all()
        total_votes = sum(choice.votes for choice in choices)

        choices_with_percent = []
        for choice in choices:
            if total_votes > 0:
                percent = (choice.votes / total_votes * 100)
            else:
                percent = 0
            choices_with_percent.append({
                'choice': choice,
                'votes': choice.votes,
                'percent': round(percent, 1)
            })

        user_choice_id = None
        try:
            vote = Vote.objects.get(user=self.request.user, question=question)
            user_choice_id = vote.choice.id
        except Vote.DoesNotExist:
            pass

        context['choices_with_percent'] = choices_with_percent
        context['user_choice_id'] = user_choice_id
        context['total_votes'] = total_votes

        return context


@login_required
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': 'вы не сделали выбор'
        })

    try:
        old_vote = Vote.objects.get(user=request.user, question=question)
        old_vote.choice.votes -= 1
        old_vote.choice.save()
        old_vote.delete()
    except Vote.DoesNotExist:
        pass

    selected_choice.votes += 1
    selected_choice.save()

    Vote.objects.create(user=request.user, question=question, choice=selected_choice)

    return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))