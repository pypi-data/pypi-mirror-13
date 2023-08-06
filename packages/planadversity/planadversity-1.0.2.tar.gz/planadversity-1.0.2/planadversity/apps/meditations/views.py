import json
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.views.generic import DetailView, ListView, View, TemplateView
from django.core import serializers
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string

from .models import Meditation, Response
from .forms import ResponseForm
from braces import views


class JsonView(views.CsrfExemptMixin,
               views.JsonRequestResponseMixin,
               views.JSONResponseMixin, View):
    pass


class MeditationDetailView(JsonView, DetailView):
    model = Meditation


class MeditationListJSONView(JsonView, ListView):
    model = Meditation
    json_dumps_kwargs = {u"indent": 2}

    def get(self, request, *args, **kwargs):
        context = serializers.serialize('json',
                                        self.get_queryset().all())

        return self.render_json_response(context)


class HomepageView(TemplateView):
    template_name = 'homepage.html'

    def get_context_data(self, *args, **kwargs):
        context = super(HomepageView, self).get_context_data(*args, **kwargs)
        meditation = None
        responded = None

        try:
            meditation = Meditation.objects.get(date=datetime.now().date())
        except:
            pass

        try:
            responded = Response.objects.filter(meditation=meditation,
                                                user=self.request.user.id)[0]
        except IndexError:
            pass

        context['todays_meditation'] = meditation
        context['responded'] = responded
        return context


class MeditationListView(JsonView, ListView):
    model = Meditation
    form_class = ResponseForm

    def get_context_data(self, *args, **kwargs):
        context = super(MeditationListView, self).get_context_data(*args, **kwargs)
        meditation = None
        responses = None

        # TODO: Cache this for one day, only refreshing it if the user asks for a new random
        # TODO: Should grab non-repsonded to meditations if possible
        try:
            meditation = Meditation.objects.get(date=datetime.now().date())
            responded = Response.objects.filter(meditation=meditation,
                                                user=self.request.user.id)
        except:
            pass

        context['responses'] = Response.objects.filter(user=self.request.user.id)
        context['meditation'] = meditation
        context['responded'] = responded
        return context


class ResponseDetailView(JsonView, views.LoginRequiredMixin,  DetailView):
    model = Response

    def get_queryset(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            return Response.objects.filter(user=self.request.user.id)
        return Response.objects.all()


class ResponseListView(JsonView, views.LoginRequiredMixin,  ListView):
    model = Response

    def get_queryset(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            return Response.objects.filter(user=self.request.user.id)
        return Response.objects.all()

class ResponseCreateView(JsonView, views.LoginRequiredMixin,  CreateView):
    model = Response
    form_class = ResponseForm


    def get_context_data(self, *args, **kwargs):
        context = super(ResponseCreateView, self).get_context_data(*args, **kwargs)
        meditation = None

        try:
            meditation = Meditation.objects.get(slug=self.request.GET.get('meditation'))
        except:
            pass

        context['meditation'] = meditation
        return context


    def get_success_url(self):
        return reverse('homepage', args=()) + '#about'

    def form_valid(self, form):
        form = form.save(commit=False)
        form.user = self.request.user
        form.save()
        return super(ResponseCreateView, self).form_valid(form)


'''
class MeditationJoinView(JsonView, views.LoginRequiredMixin):
    """ A view that checks the request object for an 
    authenticated user and, if found, adds them to the 
    project member group.
    """
    def get(self, request, *args, **kwargs):
        user = self.request.user
        html = ''
        fragments = {}
        success = False
        project = Meditation.objects.get(slug=kwargs['slug'])
        if user.is_authenticated() and not user in project.members.all():
            project.members.add(user)
            project.save()
            success = True
            html = "<p class='leave-button' ><a href='{0}' class='btn btn-danger ajax' data-replace='.leave-button'><i class='fa fa-times'></i> Leave project</a></p>".format(reverse('project-leave', args=[project.slug]))
            fragments['.member-thumbs'] = render_to_string('honey/_member_list.html', {'members': project.members.all()})
        return self.render_json_response(
            {'user': user.username, 'html': html, 'fragments': fragments})



class MeditationLeaveView(JsonView, views.LoginRequiredMixin):
    """ A view that checks the request object for an 
    authenticated user and, if found, adds them to the 
    project member group.
    """
    def get(self, request, *args, **kwargs):
        user = self.request.user
        html = ''
        fragments = {}
        success = False
        project = Meditation.objects.get(slug=kwargs['slug'])
        if user.is_authenticated() and user in project.members.all():
            project.members.remove(user)
            project.save()
            html = "<p class='join-button' ><a href='{0}' class='btn btn-success ajax' data-replace='.join-button'><i class='fa fa-plus'></i> Join project</a></p>".format(reverse('project-join', args=[project.slug]))
            success = True
            fragments['.member-thumbs'] = render_to_string('honey/_member_list.html', {'members': project.members.all()})
        return self.render_json_response(
            {'user': user.username, 'html': html, 'fragments': fragments})
'''

