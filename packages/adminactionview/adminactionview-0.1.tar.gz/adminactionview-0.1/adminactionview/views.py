from django.views.generic import View
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib import admin
from django.utils.decorators import classonlymethod


class IntermediateAdminView(View):

    short_description = "Action with intermediate view"
        
    def post(self, request, modeladmin, queryset):
        form = None
        
        if 'apply' in request.POST:
        
            form = self.Form(request.POST)

            if form.is_valid():
            
                count = 0
                for entry in queryset:
                    self.actionOnEntry(entry, form)
                    count += 1

                plural = False
                if count != 1:
                    plural = True

                modeladmin.message_user(request, "Successfully applied the action on %i %s" % (count, "entry" if not plural else "entries"))
                return HttpResponseRedirect(request.get_full_path())
                
        if not form:
            form = self.Form(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})

        context = {
            'queryset': queryset,
            'form': form,
            'action_name': self.action_name,
        }
        
        return render(request, self.template_name, context)
    
    @classonlymethod
    def as_admin_view(cls, **initkwargs):
        view = cls.as_view(**initkwargs)
        
        def admin_view(modeladmin, request, *args, **kwargs):
            return view(request, modeladmin, *args, **kwargs)
        admin_view.short_description = cls.short_description
        admin_view.__name__ = cls.action_name        
            
        return admin_view

