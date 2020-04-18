from django.shortcuts import HttpResponse, get_object_or_404, render, HttpResponseRedirect, reverse, redirect
import pandas as pd
import re
import os
import numpy as np
from chart.models import (Chart, List, Instrument, ChartType, ChartOverlay, ChartIndicator)
from .forms import (ChartForm,  ListForm, InstrumentForm, ListDeleteForm, ChartDeleteForm,
                    ListNameModifyForm, InstrumentDeleteForm, )
from .choices import color_choice, position_choice

import json
from django.conf import settings


# Create your views here.


def view_chart(request):
    if request.user.is_authenticated == True:
        chart_settings = Chart.objects.all().filter(user_id=request.user)
        trace_datas = []
        chart_group = []
        active_ins_arr = []
        active_ins_name = ''
        chart_num = 0
        if chart_settings:
            chart_types = ChartType.objects.all()
            overlays = ChartOverlay.objects.all()
            indicators = ChartIndicator.objects.all()
            for setting in chart_settings:
                chart_num = chart_num + 1
                temp_list = []                
                ins_list = List.objects.filter(chart_id=setting.id)
                temp_list.append(ins_list)
                for i_list in ins_list:
                    instruments = Instrument.objects.filter(list_id=i_list.id)
                    for instrument in instruments:
                        if instrument.active is True:
                            active_ins_name = instrument.name
                            trace_datas = convert_trace_data(setting.id, instrument.name, setting.period)
                            active_ins_arr = Instrument.objects.filter(list_id=instrument.list_id)
                chart_colors = color_choice
                indicator_position = position_choice   
                chart = {
                    'chart_number': chart_num,
                    'ins_list': temp_list,
                    'trace': trace_datas['trace'],
                    'chart_id': setting.id,
                    'chart_name': setting.name,
                    'instrument_arr': active_ins_arr,
                    'active_instrument_name': active_ins_name,
                    'chart_type': trace_datas['type'],
                    'chart_types': chart_types,
                    'chart_period': trace_datas['period'],
                    'chart_colors': chart_colors,
                    'chart_position': indicator_position,
                    'd_color': setting.decreasing_color,
                    'i_color': setting.increasing_color,
                    'chart_overlays': setting.overlay.all(),
                    'chart_indicators': setting.indicator.all(),
                    'overlays': overlays,
                    'indicators': indicators,
                }
                chart_group.append(chart)
        context = {
            'chart_group': chart_group,
        }
        return render(request, 'chart/index.html', context)
    else:
        return render(request, 'account/login.html', {})


def convert_trace_data(chart_id, instrument_name, c_period):
    df = pd.read_csv('./Instruments/'+instrument_name+'.csv')
    data_list = df.values.tolist()
    x_list = []
    open_list = []
    close_list = []
    high_list = []
    low_list = []
    volum_list = []
    if c_period == 'w':
        data_set = get_weekly_data_set(data_list)
    else:
        data_set = data_list
    for data in data_set:
        match = re.search(r'\d{4}\d{2}\d{2}', str(data[0]))
        x_list.append(match.group(0)[:-4] + '-' + match.group(0)[4:-2] + '-' + match.group(0)[-2:])
        open_list.append(data[1])
        high_list.append(data[2])
        low_list.append(data[3])
        close_list.append(data[4])
        volum_list.append(data[5])

    open_list_fft = np.fft.fft(open_list)
    open_list_ifft = np.fft.ifft(open_list_fft)
    high_list_fft = np.fft.fft(high_list)
    high_list_ifft = np.fft.ifft(high_list_fft)
    low_list_fft = np.fft.fft(low_list)
    low_list_ifft = np.fft.ifft(low_list_fft)
    close_list_fft = np.fft.fft(close_list)
    close_list_ifft = np.fft.ifft(close_list_fft)
    volum_list_fft = np.fft.fft(volum_list)
    volum_list_ifft = np.fft.ifft(volum_list_fft)

    material_cnt = len(open_list_ifft)
    sample_cnt = 700
    step = material_cnt / sample_cnt

    idx = 0
    trace_data_arr = []
    for i in range(0, material_cnt):
        trace_data = []
        idx += 1
        if idx > step:
            idx = 0
            trace_data.append(x_list[i])
            trace_data.append(open_list_ifft[i].real)
            trace_data.append(high_list_ifft[i].real)
            trace_data.append(low_list_ifft[i].real)
            trace_data.append(close_list_ifft[i].real)
            trace_data.append(volum_list_ifft[i].real)
            trace_data_arr.append(trace_data)
    chart_type_color = Chart.objects.get(id=chart_id)
    data_dic = {
        'trace': trace_data_arr,
        'type': str(chart_type_color.type),
        'period': str(chart_type_color.period),
    }
    return data_dic


def add_chart(request):
    form = ChartForm(request.POST or None,)
    if form.is_valid():
        new_chart = form.save()
        new_chart.user = request.user
        new_chart.save()
        list_form = ListForm()    
        ctx = {           
            'chart': new_chart,
            'chart_id': new_chart.id,
            'form': list_form
        }
        return render(request, 'chart/chart_config.html', ctx)
    ctx = {
        'form': form
    }
    return render(request, 'chart/add_chart.html', ctx)


def update_chart_settings(request):
    chart_id = request.POST.get('c_id')
    period = request.POST.get('c_period')
    c_type = request.POST.get('chart_type')
    d_color = request.POST.get('de_color')
    i_color = request.POST.get('in_color')
    Chart.objects.filter(id=chart_id).update(period=period, type=c_type, decreasing_color=d_color,
                                             increasing_color=i_color)
    return HttpResponse(json.dumps("success"))


def remove_chart_list(request):
    chart_list = Chart.objects.all()
    return render(request, 'chart/remove_chart_list.html', locals())


def remove_chart(request, chart_id):
    del_chart = get_object_or_404(Chart, id=chart_id)
    form = ChartDeleteForm(request.POST or None, instance=del_chart)
    if form.is_valid():
        chart = Chart.objects.filter(id=chart_id)
        chart.delete()
        return HttpResponseRedirect(reverse('chart:view_chart'))

    return render(request, 'chart/remove_chart_form.html', locals())


# def add_lists(request, chart_id):
#     instantiate = Lists(chart_id=chart_id)
#     form = ListsForm(request.POST or None, instance=instantiate)
#     chart = get_object_or_404(Chart, id=chart_id)
#     if form.is_valid():
#         new_lists = form.save()
#         list_form = ListForm()
#         return render(request, 'chart/chart_config.html', {'form': list_form, 'lists': new_lists, 'chart_id': chart_id})
#     return render(request, 'chart/chart_config.html', locals())


def add_list(request, chart_id):
    instantiate = List(chart_id=chart_id)
    form = ListForm(request.POST or None, instance=instantiate)
    chart = get_object_or_404(Chart, id=chart_id)
    if form.is_valid():
        new_list = form.save()
        load_file_list = []
        userpath = settings.USERS_DIRECTORY+str(request.user)
        with os.scandir(userpath+"/Universes") as entries:
            for entry in entries:
                if not entry.is_file():
                    continue
                filename, file_extension = os.path.splitext(entry.name)
                if file_extension.lower() != ".csv":
                    continue
                load_file_list.append(filename)
        ctx = {
            'load_file_list': load_file_list,
            'list': new_list, 
            'chart_id': chart_id
        }
        return render(request, 'chart/chart_config.html', ctx)
    ctx = {
        'form': form,
        'chart': chart
    }
    return render(request, 'chart/chart_config.html', ctx)

def add_universe(request, chart_id, list_id, f_name):
    instruments = []
    userpath = settings.USERS_DIRECTORY+str(request.user)
    df = pd.read_csv(userpath + '/Universes/'+f_name+'.csv')
    instrument_list = df.values.tolist()
    for instrument in instrument_list:
        instruments.append(instrument[0])
    ctx = {
        'chart_id': chart_id,
        'list_id': list_id,
        'f_name': f_name,
        'instrument_list': instruments
    }
    return render(request, 'chart/chart_config.html', ctx)

def add_instrument(request, chart_id, list_id, f_name):
    if request.POST:
        instrument_str = request.POST.getlist("instrument[]")
        for instrument in instrument_str: 
            chart_instrument = Instrument(name=instrument, list_id=list_id, chart_id=chart_id, universe=f_name)
            if Instrument.objects.filter(name=instrument, list_id=list_id).exists():
                continue
            chart_instrument.save()
        Instrument.objects.filter(name=instrument_str[0]).update(active=True)
        return redirect('chart:view_chart')
    return render(request, 'chart/chart_config.html', locals())


def modify_add_instrument(request, list_id, chart_id):
    instantiate = Instrument(list_id=list_id, chart_id=chart_id)
    form = InstrumentForm(request.POST or None, instance=instantiate)
    list_i = get_object_or_404(List, id=list_id)
    c_id = chart_id
    if form.is_valid():
        instrument_str = request.POST.get("name")
        instrument_arr = str(instrument_str).split(',')
        for instrument in instrument_arr:
            instrument = instrument.lstrip()
            chart_instrument = Instrument(name=instrument, list_id=list_id, chart_id=chart_id)
            if Instrument.objects.filter(name=instrument, list_id=list_id).exists():
                continue
            chart_instrument.save()
        return HttpResponseRedirect(reverse('chart:select_modify_mode', args=(list_id, chart_id)))
    return render(request, 'chart/add_instrument_form.html', locals())


def get_delete_instruments(request, list_id, chart_id):
    instrument_arr = Instrument.objects.filter(list_id=list_id, chart_id=chart_id)
    return render(request, 'chart/delete_instrument_list.html', {'instruments': instrument_arr,
                                                                 'l_id': list_id, 'c_id': chart_id})


def m_delete_instrument(request, list_id, chart_id, instrument_id):
    instrument = get_object_or_404(Instrument, id=instrument_id)
    instantiate = get_object_or_404(Instrument, id=instrument_id)
    form = InstrumentDeleteForm(request.POST or None, instance=instantiate)
    c_id = chart_id
    l_id = list_id
    if form.is_valid():
        del_instrument = Instrument.objects.filter(id=instrument_id)
        del_instrument.delete()
        return HttpResponseRedirect(reverse('chart:select_modify_mode', args=(list_id, chart_id)))
    return render(request, 'chart/delete_instrument_form.html', locals())


def get_instrument(request):
    list_id = request.POST['list_id']
    instruments = Instrument.objects.filter(list_id=list_id)
    instrument_list = []
    for instrument in instruments:
        instrument_dic = {
            'id': instrument.id,
            'name': instrument.name
        }
        instrument_list.append(instrument_dic)
    instrument_list = json.dumps(instrument_list)
    return HttpResponse(instrument_list)


def view_instrument(request):
    chart_id = request.POST['chart_id']
    ins_id = request.POST['instrument']
    Instrument.objects.filter(chart_id=chart_id).update(active=False)
    Instrument.objects.filter(id=ins_id).update(active=True)
    return HttpResponse("success")


def get_delete_list(request, chart_id):
    lists = List.objects.filter(chart_id=chart_id)
    return render(request, 'chart/delete_list.html', {'lists': lists, 'chart_id': chart_id})


def get_modify_list(request, chart_id):
    lists = List.objects.filter(chart_id=chart_id)
    return render(request, 'chart/modify_list.html', {'lists': lists, 'c_id': chart_id})


def select_modify_mode(request, list_id, chart_id):
    return render(request, 'chart/modify_mode.html', {'list_id': list_id, 'c_id': chart_id})


def modify_change_name(request, list_id, chart_id):
    modify_list = get_object_or_404(List, id=list_id)
    form = ListNameModifyForm(request.POST or None, instance=modify_list)
    c_id = chart_id
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('chart:view_chart'))
    return render(request, 'chart/modify_name_form.html', locals())


def delete_list(request, list_id, chart_id):
    del_list = get_object_or_404(List, id=list_id)
    form = ListDeleteForm(request.POST or None, instance=del_list)
    if form.is_valid():
        i_list = List.objects.filter(id=list_id)
        i_list.delete()
        if not List.objects.filter(chart_id=chart_id).exists():
            del_chart = get_object_or_404(Chart, id=chart_id)
            del_chart.delete()
        return HttpResponseRedirect(reverse('chart:view_chart'))
    ctx = {
        'del_list': del_list,
        'chart_id': chart_id,
        'form': form
    }
    return render(request, 'chart/delete_list_form.html', ctx)


def write_json(request):
    json_data = request.POST['json_data']
    file_name = request.POST['f_name']
    with open('static/chart_annotations/'+file_name+'.json', 'w') as outfile:
        json.dump(json_data, outfile)
    return_msg = "success"
    return HttpResponse(json.dumps(return_msg))


def update_overlay(request):
    c_id = request.POST['chart_id']
    chart = get_object_or_404(Chart, id=c_id)
    o_id = request.POST['overlay_id']
    o_param = request.POST['overlay_param']
    old_o_id = request.POST['old_overlay_id']
    if old_o_id != '':
        chart.overlay.remove(ChartOverlay.objects.get(id=old_o_id))
    ChartOverlay.objects.filter(id=o_id).update(param=o_param)
    chart.overlay.add(ChartOverlay.objects.get(id=o_id))
    return HttpResponse(json.dumps("success"))


def update_indicator(request):
    c_id = request.POST['chart_id']
    chart = get_object_or_404(Chart, id=c_id)
    i_id = request.POST['indicator_id']
    i_param = request.POST['indicator_param']
    # i_pos = request.POST['indicator_pos']
    old_i_id = request.POST['old_indicator_id']
    if old_i_id != '':
        chart.indicator.remove(ChartIndicator.objects.get(id=old_i_id))
    ChartIndicator.objects.filter(id=i_id).update(param=i_param)
    chart.indicator.add(ChartIndicator.objects.get(id=i_id))
    return HttpResponse(json.dumps("success"))


def delete_overlay(request, chart_id, overlay_id):
    chart = get_object_or_404(Chart, id=chart_id)
    chart.overlay.remove(ChartOverlay.objects.get(id=overlay_id))
    return HttpResponse(json.dumps("success"))


def delete_indicator(request, chart_id, indicator_id):
    chart = get_object_or_404(Chart, id=chart_id)
    chart.indicator.remove(ChartIndicator.objects.get(id=indicator_id))
    return HttpResponse(json.dumps("success"))


def get_weekly_data_set(data_set):
    o_arr = []
    h_arr = []
    l_arr = []
    c_arr = []
    v_arr = []
    data_count = 1
    weekly_data = []
    weekly_data_set = []
    for data in data_set:
        o_arr.append(data[1])
        h_arr.append(data[2])
        l_arr.append(data[3])
        c_arr.append(data[4])
        v_arr.append(data[5])
        data_count = data_count + 1
        if data_count == 7:
            weekly_data.append(data[0])
            max_o_val = max(o_arr)
            weekly_data.append(max_o_val)
            max_h_val = max(h_arr)
            weekly_data.append(max_h_val)
            max_l_val = max(l_arr)
            weekly_data.append(max_l_val)
            max_c_val = max(c_arr)
            weekly_data.append(max_c_val)
            max_v_val = max(v_arr)
            weekly_data.append(max_v_val)
            weekly_data_set.append(weekly_data)
            o_arr = []
            h_arr = []
            l_arr = []
            c_arr = []
            v_arr = []
            weekly_data = []
            data_count = 1

    return weekly_data_set
