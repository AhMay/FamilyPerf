import datetime

from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from . import models
from . import forms
from . import utilities

@method_decorator(login_required,name='dispatch')
class PerfItemIndexView(View):
    def get(self,request,*args,**kwargs):
        return render(request,'fpm/perfitems.html')

@method_decorator(login_required,name='dispatch')
class PerfItemView(View):
    def get(self,request, *args, **kwargs):
        member = models.MemberInfo.objects.get(pk=kwargs['pk'])
        perfitems = models.PerfItem.objects.filter(member=member)

        return render(request,'fpm/member_perfitems.html', {'member':member,'perfitems':perfitems})

@method_decorator(login_required,name='dispatch')
class PerfItemCreateView(CreateView):
    model = models.PerfItem
    template_name = 'fpm/member_perfitems.html'
    form_class = forms.PerfItemForm

    def form_valid(self, form):
        member = models.MemberInfo.objects.get(pk=self.kwargs['pk'])
        form.instance.member = member
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['member'] = models.MemberInfo.objects.get(pk=self.kwargs['pk'])
        return context

    def get_success_url(self):
        return reverse_lazy('fpm:member_perfitems', kwargs={'pk': self.kwargs['pk']})

@method_decorator(login_required,name='dispatch')
class PerfItemUpdateView(UpdateView):
    model = models.PerfItem
    template_name = 'fpm/member_perfitems.html'
    form_class = forms.PerfItemForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['member'] = models.PerfItem.objects.get(pk=self.kwargs['pk']).member
        return context

    def get_success_url(self):
        member = models.PerfItem.objects.get(pk=self.kwargs['pk']).member
        return reverse_lazy('fpm:member_perfitems', kwargs={'pk': member.id })

@method_decorator(login_required,name='dispatch')
class PerfItemDeleteView(DeleteView):
    model = models.PerfItem
    template_name = 'fpm/delete_comfirm.html'

    def get_success_url(self):
        member = models.PerfItem.objects.get(pk=self.kwargs['pk']).member
        return reverse_lazy('fpm:member_perfitems', kwargs={'pk': member.id})

@method_decorator(login_required,name='dispatch')
class PerfRecordIndexView(View):
    def get(self,request,*args,**kwargs):
        today = datetime.datetime.now().date()
        days = models.PerfRecord.objects.all().order_by('-day').values_list('day').distinct()
        days = [day[0] for day in list(days)]
        hasToday = today in days
        return render(request,'fpm/member_perfrecordindex.html',{
            'days':days,
            'hasToday': hasToday,
            'today':today
        })

class PerfRecordCreateView(View):
    def post(self,request,*args, **kwargs):
        #根据添加的post,返回json数据
        day = datetime.date(kwargs['year'], kwargs['month'], kwargs['day'])
        member = models.MemberInfo.objects.get(pk=kwargs['pk'])
        perf_item_name = request.POST.get('name') #name and memeber should be unie
        perf_item_scoreup = request.POST.get("score_up",0)
        perf_item_scoredown = request.POST.get("score_down", 0)
        perf_item_active =True if request.POST.get('active')=='on' else False
        record_score = request.POST.get('score')
        record_desc =request.POST.get('desc')
        perfitem = models.PerfItem.objects.filter(member=member,name=perf_item_name)
        if perfitem:
            if perfitem[0].active:
                return JsonResponse({'status':'fail','msg':'已经对有该绩效项'})
            else:
                perfitem = perfitem[0]
        else:
            #创建perfitem
            perfitem = models.PerfItem.objects.create(name=perf_item_name,score_up=int(perf_item_scoreup),
                                                      score_down=int(perf_item_scoredown),
                                                      active=perf_item_active,
                                                      member=member)
        # 创建record
        record = models.PerfRecord.objects.create(day=day, member=member, item=perfitem, score=int(record_score),
                                                  description=record_desc)
        result = models.Result.objects.filter(day=day, member=member)
        if not result:
            result = models.Result.objects.create(day=day, member=member, score=0, score_sum=0)
        else:
            result = result[0]
        result.score += int(record_score)
        result.score_sum += int(record_score)
        result.save()
        return JsonResponse({'status':'ok','item_name':record.item.name,'item_scoreup':record.item.score_up,
                             'item_scoredown':record.item.score_down,'score':record.score,'desc':record.description})
        #return redirect('fpm:member_perfrecords',year=day.year,month=day.month,day=day.day,pk=member.pk)

class PerfRecordView(View):
    def get_sum_result_obj(self,day,member):
        sum_result_obj = {}
        existing_results = models.Result.objects.order_by('-day')
        if not existing_results:
            # 如果没有任何记录，这是集的第一条绩效
            sum_result_obj['pre_sum'] = 0
            sum_result_obj['sum'] = 0
            sum_result_obj['pre_day'] = None
            sum_result_obj['cur_day'] = None
        else:
            day_result = existing_results.filter(day=day, member=member)
            if day_result:
                sum_result_obj['cur_day'] = day_result[0]
                sum_result_obj['sum'] = 0
            else:
                sum_result_obj['cur_day'] = None
                sum_result_obj['sum'] = 0
            pre_results = existing_results.filter(day__lt=day, member=member).order_by('-day')
            if pre_results:
                sum_result_obj['pre_day'] = pre_results[0]
                sum_result_obj['pre_sum'] = pre_results[0].score_sum
            else:
                sum_result_obj['pre_day'] = None
                sum_result_obj['pre_sum'] = 0
        return sum_result_obj
    def post(self,request, *args,**kwargs):
        day = datetime.date(kwargs['year'], kwargs['month'], kwargs['day'])
        member = models.MemberInfo.objects.get(pk=kwargs['pk'])
        keys = set([int(key.split('_')[0]) for key in request.POST.keys() if key != 'csrfmiddlewaretoken' and key !='result_desc'])
        result_desc = request.POST.get('result_desc','')
        sum_result_obj = self.get_sum_result_obj(day,member)
        for k in keys:
            desc = request.POST.get(str(k)+"_desc")
            score = request.POST.get(str(k)+"_score")
            perfitem = models.PerfItem.objects.get(id=k)
            models.PerfRecord.objects.create(day=day,member=member,item=perfitem,score=score,description=desc)
            sum_result_obj['sum'] +=int(score) #累计当前计分
        if sum_result_obj['cur_day']:
            sum_result_obj['cur_day'].score += sum_result_obj['sum']
            sum_result_obj['cur_day'].score_sum += sum_result_obj['sum']
            sum_result_obj['cur_day'].save()
        else:
            #创建新的记录
            score_sum = sum_result_obj['pre_sum'] +  sum_result_obj['sum']
            sum_result_obj['cur_day'] = models.Result.objects.create(day=day,
                                                                     member=member,
                                                                     score=sum_result_obj['sum'],
                                                                     score_sum=score_sum,
                                                                     description=result_desc)

        return redirect('fpm:member_perfrecords',year=day.year,month=day.month,day=day.day,pk=member.pk)
    def get(self,request, *args, **kwargs):
        today = datetime.datetime.now().date()
        day = datetime.date(kwargs['year'],kwargs['month'],kwargs['day'])
        member = models.MemberInfo.objects.get(pk=kwargs['pk'])
        records = models.PerfRecord.objects.filter(day=day,member=member)
        sum_result_obj = utilities.dict_to_object(self.get_sum_result_obj(day,member))
        if not records and today == day:
            #今天的没有记录 该显示 输入表
            items = models.PerfItem.objects.filter(member=member,active=True)
            return render(request, 'fpm/member_perfrecords_input.html',
                          {'member': member,
                           'day': day,
                           'items':items,
                           'sum_result_obj':sum_result_obj})
        elif records:
           # return render(request,'fpm/member_perfrecords.html')
           return render(request, 'fpm/member_perfrecords.html',
                         {'member': member,
                          'day': day,
                          'records':records,
                          'sum_result_obj':sum_result_obj})
        else:
            #return HttpResponse("not today and no record")
            return render(request, 'fpm/member_perfrecords.html',
                          {'member': member,
                           'day': day,
                           'sum_result_obj':sum_result_obj})
        return render(request, 'fpm/member_perfrecords.html',
                      {'member':member,
                       'day':day,
                       'sum_result_obj':sum_result_obj})

@method_decorator(login_required,name='dispatch')
class IndexView(View):
    def get(self,request,*args,**kwargs):
        return render(request,'fpm/dashboard.html')

class LoginView(View):
    def get(self, request, *args, **kwargs):
        return render(request,'login.html')

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username',None)
        password = request.POST.get('password',None)
        user = authenticate(username=username,password=password)
        if user:
            userprofile = models.UserProfile.objects.get(user=user)
            login(request,user)
            return  redirect(request.GET.get('next','fpm:family_index'))
        else:
            error_msg = "用户名或密码错误!"
        return render(request,'login.html',{'error_msg':error_msg})

@method_decorator(login_required,name='dispatch')
class LogoutView(View):
    def get(self,request):
        logout(request)
        return redirect('fpm:family_login')