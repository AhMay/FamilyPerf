import datetime

from django.shortcuts import render, HttpResponse, redirect
from django.core.exceptions import ObjectDoesNotExist
from . import models
from . import forms

# Create your views here.

def family_index(request):
    families = models.Family.objects.all()
    return render(request,'fpm/index.html',
                  {'families':families})

def member_perf(request, pk):
    '''成员绩效项目'''
    member = models.MemberInfo.objects.get(pk=pk)
    perfs = models.PerfItem.objects.filter(member=member)
    return render(request, 'fpm/member_perfitem.html',
                  {
                      'member':member,
                      'perfs': perfs})

def member_perfitem_add(request,pk):
    member = models.MemberInfo.objects.get(pk=pk)
    if request.method == 'POST':
        perfitemform = forms.PerfItemForm(request.POST)
        if perfitemform.is_valid():
            models.PerfItem.objects.create(name=perfitemform.cleaned_data['name'],
                                           score_up=perfitemform.cleaned_data['score_up'],
                                           score_down=perfitemform.cleaned_data['score_down'],
                                           active=perfitemform.cleaned_data['active'],
                                           member=member)
            return redirect('fpm:member_perf',pk=pk)

    else:
        perfitemform=forms.PerfItemForm()
        return render(request,'fpm/perfitem_component.html',{'form':perfitemform})

def member_perf_his(request, pk, year, month, day):
    member = models.MemberInfo.objects.get(pk=pk)
    day = datetime.date(year, month, day)
    pre_day_result = models.Result.objects.filter(member=member,day=day-datetime.timedelta(days=-1))
    if not pre_day_result:
        pre_sum = 0
    else:
        pre_sum = pre_day_result.score_sum
    day_result=''
    if request.method == 'POST':
        day = datetime.datetime.now().date()
        perfs = models.PerfItem.objects.filter(member=member, active=True)
        sum =0
        for perf in perfs:
            perf_value = request.POST.get(perf.name,0)
            sum += int(perf_value)
            perf_desc = request.POST.get(perf.name+"_desc")
            models.PerfRecord.objects.create(day=day,member=member,item=perf,score=perf_value,description=perf_desc)

        pre_result = models.Result.objects.filter(member=member,day=day-datetime.timedelta(days=-1))
        if not pre_result:
            pre_sum = 0
        else:
            pre_sum = pre_result[0].score_sum
        models.Result.objects.create(day=day,member=member,score=sum,score_sum=pre_sum+sum)
        return redirect('fpm:member_perf_his',pk=pk,year=day.year,month=day.month,day=day.day)
    else:
        #view
        records = models.PerfRecord.objects.filter(member=member, day=day)
        perfRecords = []
        if not records:
            day = datetime.datetime.now().date()
            perfs = models.PerfItem.objects.filter(member=member, active=True)
            if not perfs:
                return render(request, 'fpm/member_dayperf.html',{
                    'member': member,
                    'day': day,
                })
            disabled =""
            for perf in perfs:
                perf_record = forms.PerfRecordForm(data={
                    'name':perf.name,
                    'score_up':perf.score_up,
                    'score_down':perf.score_down,
                    'score':0,
                    'description':''
                })
                perfRecords.append(perf_record)
        else:
            day_result = models.Result.objects.get(member=member,day=day)
            disabled ="disabled"
            for record in records:
                perf_record = forms.PerfRecordForm(data={
                    'name': record.item.name,
                    'score_up': record.item.score_up,
                    'score_down': record.item.score_down,
                    'score': record.score,
                    'description': record.description
                })
                perfRecords.append(perf_record)
        return render(request, 'fpm/member_dayperf.html',
                      {
                          'member': member,
                          'day': day,
                          'perfRecords': perfRecords,
                          "disabled":disabled,
                          'day_result': day_result,
                          'pre_sum':pre_sum
                      })

def member_perflist(request,pk):
    member = models.MemberInfo.objects.get(pk=pk)
    records = models.PerfRecord.objects.filter(member=member).order_by('-day').values('day').distinct()
    results=[]
    for record in records:
        try:
            result = models.Result.objects.get(member=member,day=record['day'])
            obj ={
            'day':result.day,
            'score':result.score,
            'score_sum':result.score_sum
            }
            results.append(obj)
        except ObjectDoesNotExist:
            break;

    return render(request,'fpm/member_perflist.html',{
        'member':member,
        'results':results,
    })