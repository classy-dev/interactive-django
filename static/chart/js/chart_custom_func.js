function chart_setting(csrf_token, c_id) {
    var period = $('#period_'+c_id).val();
    var c_type = $('#chart_type_'+c_id).val();
    var d_color = $('#d_color_'+c_id).val();
    var i_color = $('#i_color_'+c_id).val();
    window.CSRF_TOKEN = csrf_token;
    $.ajax({
        url: 'update_chart_settings',
        type: 'POST',
        data: {csrfmiddlewaretoken: window.CSRF_TOKEN, c_id: c_id, c_period: period, chart_type: c_type, de_color: d_color, in_color: i_color},
        dataType: 'json',
        success: function(msg) {
            if (msg === "success"){
                location.reload(true);
            }
        }
    });
}

function overlay_update(csrf_token, c_id, o_id = '') {
    window.CSRF_TOKEN = csrf_token;
    var o_param;
    var old_o_id;
    if (o_id === '') {
        old_o_id = '';
        o_id = $('#overlay_add_' + c_id + ' option:selected').val();
        o_param = $('#param_id_add_' + c_id).val();
    }else {
        old_o_id = o_id;
        o_param = $('#param_id_' + o_id).val();
        o_id = $('#overlay_' + o_id + ' option:selected').val();
    }
    $.ajax({
        url: 'update_overlay',
        type: 'POST',
        data: {csrfmiddlewaretoken: window.CSRF_TOKEN, chart_id: c_id, overlay_id: o_id, overlay_param: o_param, old_overlay_id: old_o_id},
        dataType: 'json',
        success: function(msg) {
            console.log(msg);
            if (msg === "success"){
                location.reload(true);
            }
        }
    });
}

function indicator_update(csrf_token, c_id, i_id = '') {
    window.CSRF_TOKEN = csrf_token;
    var i_param;
    var old_i_id;
    var i_position;
    if (i_id === '') {
        old_i_id = '';
        i_id = $('#indicator_add_' + c_id + ' option:selected').val();
        i_param = $('#i_param_id_add_' + c_id).val();
        // i_position = $('#i_pos_add_' + c_id + ' option:selected').val();
    }else {
        old_i_id = i_id;
        i_param = $('#i_param_id_' + i_id).val();
        i_id = $('#indicator_' + i_id + ' option:selected').val();
        // i_position = $('#i_pos_' + old_i_id + ' option:selected').val();
    }
    $.ajax({
        url: 'update_indicator',
        type: 'POST',
        data: {csrfmiddlewaretoken: window.CSRF_TOKEN, chart_id: c_id, indicator_id: i_id, indicator_param: i_param, old_indicator_id: old_i_id},
        dataType: 'json',
        success: function(msg) {
            console.log(msg);
            if (msg === "success"){
                location.reload(true);
            }
        }
    });
}

function delete_overlay(c_id, o_id) {
    if (confirm("Are you sure?") === true) {
        $.ajax({
            url: 'delete_overlay/'+c_id+'/'+o_id,
            type: 'GET',
            dataType: 'json',
            success: function(msg) {
                console.log(msg);
                if (msg === "success"){
                    location.reload(true);
                }
            }
        });
    }
}


function delete_indicator(chart_id, i_id) {
    if (confirm("Are you sure?") === true) {
        $.ajax({
            url: 'delete_indicator/'+chart_id+'/'+i_id,
            type: 'GET',
            dataType: 'json',
            success: function(msg) {
                console.log(msg);
                if (msg === "success"){
                    location.reload(true);
                }
            }
        });
    }
}