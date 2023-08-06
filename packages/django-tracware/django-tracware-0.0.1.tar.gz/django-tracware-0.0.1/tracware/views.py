import json

from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from django.http import HttpResponseNotAllowed
from django.http import HttpResponse
from django.apps import apps

from toolware.utils.mixin import LoginRequiredMixin
from toolware.utils.mixin import CsrfProtectMixin
from toolware.utils.mixin import DeleteMixin

from .models import Trac
from . import signals
from . import utils as util
from . import defaults as defs


class TracDeleteAjaxView(LoginRequiredMixin, CsrfProtectMixin, DeleteMixin):
    """
    Trac Delete View.
    """
    model = Trac
    success_url = "/"  # ajax only, don't care

    def get_object(self, queryset=None):
        obj = super(TracDeleteAjaxView, self).get_object()
        if not (obj.user == self.request.user) or not self.request.is_ajax():
            raise Http404
        signals.trac_deleted.send(sender=Trac, request=self.request, trac=obj)
        return obj


class TracToggleAjaxView(LoginRequiredMixin, CsrfProtectMixin, TemplateView):
    """
    Trac Toggle View.
    """
    def invalid_access_method(self):
        messages.add_message(self.request, messages.WARNING, _("Invalid request. Method Not Allowed."))
        return HttpResponseNotAllowed(_('Method Not Allowed'))

    def invalid_operation(self, message=None):
        if not message:
            message = _('Invalid Operation. Missing directives.')
        json_data = {
            'status': 'failure',
            'message': message,
            'state': defs.TRACWARE_STATUS_INIT,
        }
        return HttpResponse(json.dumps(json_data), content_type="application/json")

    def get(self, request, *args, **kwargs):
        return self.invalid_access_method()

    def post(self, request, *args, **kwargs):
        if not request.is_ajax():
            return self.invalid_access_method()

        json_data = {
            'status': 'success',
            'state': defs.TRACWARE_STATUS_INIT
        }
        trac_obj = None

        try:
            pk = request.POST['trac-oid']
            app = request.POST['trac-app']
            ttype = request.POST['trac-type']
            klass = request.POST['trac-class']
            state = request.POST['trac-state']
        except KeyError:
            return self.invalid_operation()
        try:
            model = apps.get_model(app, klass)
        except ValueError:
            message = _("Model must be of the form 'app_label.model_name'")
            return self.invalid_operation(message)
        except LookupError:
            message = _("You must supply a valid app label and module name. Got '{}.{}'".format(app, klass))
            return self.invalid_operation(message)
        else:
            obj = get_object_or_404(model, id=pk)
            json_data['state'] = state
            if state == defs.TRACWARE_STATUS_INIT:
                if util.trac_exists(self.request.user, obj, ttype):
                    json_data['state'] = defs.TRACWARE_STATUS_ON
                else:
                    json_data['state'] = defs.TRACWARE_STATUS_OFF
            elif state == defs.TRACWARE_STATUS_OFF:
                trac_obj = util.trac_get_or_create(self.request.user, obj, ttype)
                if trac_obj:
                    signals.trac_created.send(sender=Trac, request=self.request, trac=trac_obj)
                    json_data['state'] = defs.TRACWARE_STATUS_ON
            elif state == defs.TRACWARE_STATUS_ON:
                trac_obj = util.trac_delete(self.request.user, obj, ttype)
                if trac_obj:
                    signals.trac_deleted.send(sender=Trac, request=self.request, trac=trac_obj)
                json_data['state'] = defs.TRACWARE_STATUS_OFF
            else:
                self.invalid_operation()
            if trac_obj:
                obj = get_object_or_404(model, id=pk)  # updated copy
            json_data['counters'] = util.trac_get_stats_for_obj(obj)
        return HttpResponse(json.dumps(json_data), content_type="application/json")
