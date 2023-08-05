
from __future__ import absolute_import, unicode_literals

from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from horizon.utils import memoized
from leonardo import messages
from leonardo.views import *

from ..models import Page
from .forms import (WidgetDeleteForm, WidgetSelectForm, WidgetUpdateForm,
                    get_widget_create_form, get_widget_update_form)
from .tables import WidgetDimensionTable
from .utils import get_widget_from_id


class WidgetViewMixin(object):

    def handle_dimensions(self, obj):
        """save dimensions
        """
        from .tables import WidgetDimensionFormset
        from ..models import WidgetDimension
        formset = WidgetDimensionFormset(
            self.request.POST, prefix='dimensions')
        for form in formset.forms:
            if form.is_valid():
                if 'id' in form.cleaned_data:
                    form.save()
            else:
                # little ugly
                data = form.cleaned_data
                data['widget_type'] = \
                    ContentType.objects.get_for_model(obj)
                data['widget_id'] = obj.id
                data.pop('DELETE', None)
                wd = WidgetDimension(**data)
                wd.save()
        # optionaly delete dimensions
        if formset.is_valid():
            formset.save(commit=False)
            # delete objects
            for obj in formset.deleted_objects:
                obj.delete()
        return True

    def _get_moda_size(self):
        '''try get form_size attribute form form or widget'''
        form_class = self.get_form_class()
        return getattr(form_class,
                       'form_size',
                       getattr(self.model, 'form_size', 'md'))

    @memoized.memoized_method
    def get_page(self):
        return Page.objects.get(id=self.kwargs['page_id'])

    def get_form_kwargs(self):
        kwargs = super(WidgetViewMixin, self).get_form_kwargs()
        kwargs.update({
            'request': self.request,
        })
        return kwargs


class WidgetUpdateView(WidgetViewMixin, UpdateView):

    template_name = 'leonardo/common/modal.html'

    form_class = WidgetUpdateForm

    def get_context_data(self, **kwargs):
        context = super(WidgetUpdateView, self).get_context_data(**kwargs)
        context['modal_size'] = self._get_moda_size()
        return context

    def get_form_class(self):
        if not hasattr(self, '_form_class'):
            self._form_class = get_widget_update_form(**self.kwargs)
        return self._form_class

    def get_form(self, form_class):
        """Returns an instance of the form to be used in this view."""

        kwargs = self.get_form_kwargs()
        return form_class(**kwargs)

    def form_valid(self, form):
        response = super(WidgetUpdateView, self).form_valid(form)
        obj = self.object
        self.handle_dimensions(obj)
        return response


class WidgetCreateView(WidgetViewMixin, CreateView):

    template_name = 'leonardo/common/modal.html'

    def get_label(self):
        form = self.get_form(self.get_form_class())
        return ugettext("Add new {} to {}".format(
            form._meta.model._meta.verbose_name,
            self.get_page()))

    def get_form_class(self):
        if not hasattr(self, '_form_class'):
            self._form_class = get_widget_create_form(**self.kwargs)
        return self._form_class

    def get_form(self, form_class):
        kwargs = self.get_form_kwargs()
        return form_class(**kwargs)

    def get_context_data(self, **kwargs):
        context = super(WidgetCreateView, self).get_context_data(**kwargs)
        context['table'] = WidgetDimensionTable(self.request, data=[])
        # add extra context for template
        context['url'] = reverse("widget_create_full", kwargs=self.kwargs)
        context['modal_size'] = self._get_moda_size()
        return context

    def form_valid(self, form):
        try:
            obj = form.save(commit=False)
            obj.save(created=False)
            self.handle_dimensions(obj)
            obj.parent.save()
            success_url = self.get_success_url()
            response = HttpResponseRedirect(success_url)
            response['X-Horizon-Location'] = success_url
        except Exception as e:
            raise e

        return response

    def get_initial(self):
        return self.kwargs


class WidgetPreCreateView(CreateView, WidgetViewMixin):

    form_class = WidgetSelectForm

    template_name = 'leonardo/common/modal.html'

    def get_label(self):
        return ugettext("Add new Widget to {}".format(self.get_page()))

    def get_context_data(self, **kwargs):
        context = super(WidgetPreCreateView, self).get_context_data(**kwargs)
        context['modal_size'] = 'md'
        context['form_submit'] = _('Continue')
        return context

    def get_form(self, form_class):
        """Returns an instance of the form to be used in this view."""
        kwargs = self.kwargs
        kwargs.update(self.get_form_kwargs())
        kwargs.update({
            'request': self.request,
            'next_view': WidgetCreateView
        })
        return form_class(**kwargs)


class WidgetInfoView(UpdateView, WidgetViewMixin):

    template_name = 'leonardo/common/modal.html'

    form_class = WidgetUpdateForm

    def get(self, request, cls_name, id):

        widget = self.object

        widget_info = """
            <ul>
                <li><span><b>widget:</b>&nbsp;{name}&nbsp({id})</span></li>
                <li><span><b>parent:</b>&nbsp;{parent}&nbsp({parent_id})</span></li>
                <li><span><b>region:</b>&nbsp;{region}</span></li>
                <li><span><b>ordering:</b>&nbsp;{ordering}</span></li>
            </ul>""".format(**{
            'name': widget.__class__.__name__,
            'id': widget.id,
            'region': widget.region,
            'parent': widget.parent,
            'parent_id': widget.parent.pk,
            'ordering': widget.ordering,
        })

        messages.info(request, mark_safe(widget_info))

        return HttpResponse(mark_safe(widget_info))


class SuccessUrlMixin(object):

    def get_success_url(self):
        if self.request.META.get("HTTP_REFERER") != \
                self.request.build_absolute_uri():
            return self.request.META.get('HTTP_REFERER')

        try:
            success_url = self.object.parent.get_absolute_url()
        except:
            pass
        else:
            return success_url

        return super(WidgetActionMixin, self).get_success_url()


class WidgetDeleteView(SuccessUrlMixin, ModalFormView,
                       ContextMixin, ModelFormMixin):

    form_class = WidgetDeleteForm

    template_name = 'leonardo/common/modal.html'

    def get_label(self):
        return ugettext("Delete {}".format(self.object._meta.verbose_name))

    def get_context_data(self, **kwargs):
        context = super(WidgetDeleteView, self).get_context_data(**kwargs)

        # add extra context for template
        context['url'] = self.request.build_absolute_uri()
        context['modal_header'] = self.get_header()
        context['title'] = self.get_header()
        context['form_submit'] = self.get_label()
        context['heading'] = self.get_header()
        context['help_text'] = self.get_help_text()
        return context

    def form_valid(self, form):
        obj = self.object
        try:
            parent = obj.parent
            obj.delete()
            # invalide page cache
            parent.invalidate_cache()
            success_url = self.get_success_url()
            response = HttpResponseRedirect(success_url)
            response['X-Horizon-Location'] = success_url
        except Exception as e:
            raise e

        return response

    def get_initial(self):
        return self.kwargs


class WidgetActionMixin(SuccessUrlMixin):

    template_name = 'leonardo/common/modal.html'
    form_class = WidgetUpdateForm
    success_url = "/"

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)


class WidgetSortView(WidgetActionMixin, ModalFormView):

    '''Simple handle jquery sortable'''

    def post(self, *args, **kwargs):

        widgets = self.request.POST.getlist('widgets[]', [])

        widget_list = []

        try:
            for widget_id in widgets:
                widget = get_widget_from_id(widget_id)
                if widget:
                    widget_list.append(widget)
        except:
            messages.error(
                self.request, _('Error occured while sorting widgets.'))

        i = 0

        for widget in widget_list:
            widget.ordering = i
            widget.save()
            i += 1

        messages.success(self.request, _('Widget sorting success.'))

        return HttpResponse('ok')


class WidgetReorderView(WidgetActionMixin, ModalFormView, ModelFormMixin):

    '''Handle reorder 0 = first, 1 = last'''

    def post(self, *args, **kwargs):

        widget = self.object

        ordering = self.kwargs.get('ordering')

        if int(ordering) == 0:

            widget.ordering = 0
            widget.save()

            widgets = getattr(widget.parent.content, widget.region)
            widgets = [w for w in widgets if w.id != widget.id]

            for i, _widget in enumerate(widgets):
                _widget.ordering = i + 1
                _widget.save()

        elif int(ordering) == -1:
            next_ordering = widget.ordering - 1
            widgets = getattr(widget.parent.content, widget.region)
            for w in widgets:
                if w.ordering == next_ordering:
                    w.ordering = widget.ordering
                    w.save()
                    widget.ordering = next_ordering
                    widget.save()
        elif int(ordering) == 1:

            next_ordering = widget.ordering + 1
            widgets = getattr(widget.parent.content, widget.region)
            for w in widgets:
                if w.ordering == next_ordering:
                    w.ordering = widget.ordering
                    w.save()
                    widget.ordering = next_ordering
                    widget.save()

        else:
            widget.ordering = widget.next_ordering
            widget.save()
            widgets = getattr(widget.parent.content, widget.region)
            widgets = [w for w in widgets if w.id != widget.id]
            widgets.sort(key=lambda w: w.ordering)

            for i, _widget in enumerate(widgets):
                _widget.ordering = i
                _widget.save()

        messages.success(self.request, _('Widget was successfully moved.'))

        success_url = self.get_success_url()
        response = HttpResponseRedirect(success_url)
        response['X-Horizon-Location'] = success_url
        return response


class WidgetCopyView(WidgetReorderView):

    '''Create widget copy.'''

    def post(self, *args, **kwargs):

        widget = self.object
        widget.pk = None
        widget.save()

        messages.success(self.request, _('Widget was successfully cloned.'))

        # TODO try HTTP_REFERER
        success_url = self.get_success_url()
        response = HttpResponseRedirect(success_url)
        response['X-Horizon-Location'] = success_url
        return response
