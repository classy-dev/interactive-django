(function () {
    initTooltip('bottom');

    var chart = [];
    var plot = [];
    var $strokeSettings = $('#select-stroke-settings');
    var $colorPickerFill = $('.color-picker[data-color="fill"]');
    var $colorPickerStroke = $('.color-picker[data-color="stroke"]');
    var $annotationLabel;
    // var $markerSize = $('#select-marker-size');
    var $markerSize = $('.volume-btn[data-el-size="marker"]');
    var $fontSize = $('.volume-btn[data-el-size="label"]');
    var $markerSizeBtn = $('.select-marker-size');
    var $fontSettings = $('#select-font-style');

    var l = 0;
    var j = 0;
    var cnt = 0;

    var $labelMethod = $('[data-label-method]');

    $(function () {
        // page UI elements
        createPageColorPicker();

        // init selectpicker
        $('.selectpicker').selectpicker({
            iconBase: 'ac',
            tickIcon: 'ac-check'
        });

        // init volume bars
        // marker-size, font-size
        initVolumeBar();

        // data from https://cdn.anychart.com/csv-data/msft-daily-short.js
        // var data = get_msft_daily_short_data();
        for (j = 0; j < chart_id.length; j++) {
            // Create new chart object.
            chart[chart_id[j]] = anychart.stock();

            plot[chart_id[j]] = chart[chart_id[j]].plot(0);
            chart[chart_id[j]].contextMenu(false);

            // create data table
            var table = anychart.data.table(0);
            table.addData(trace[j]);

            // create data mappings
            mapping = table.mapAs();
            mapping.addField('open', 1, 'first');
            mapping.addField('high', 2, 'max');
            mapping.addField('low', 3, 'min');
            mapping.addField('close', 4, 'last');
            mapping.addField('value', 4, 'last');

            // create line series
            if (chart_type[j] === 'line') {
                var line_chart = plot[chart_id[j]].line(mapping);
                line_chart.name(chart_name[j]);
            }
            if (chart_type[j] === 'ohlc') {
                var ohlc_chart = plot[chart_id[j]].ohlc(mapping);
                ohlc_chart.name(chart_name[j]);
                ohlc_chart.fallingStroke(rise_color[j], 1.5, "6 2", "bevel");
                ohlc_chart.risingStroke(fall_color[j], 1.5, "6 2", "bevel");
            }
            if (chart_type[j] === 'candlestick') {
                var candle_chart = plot[chart_id[j]].candlestick(mapping);
                candle_chart.name(chart_name[j]);
                candle_chart.risingStroke(rise_color[j]);
                candle_chart.risingFill(rise_color[j]);
                candle_chart.fallingStroke(fall_color[j]);
                candle_chart.fallingFill(fall_color[j]);
            }

            // create date range
        var rangeSelector = anychart.ui.rangeSelector();
        var rangePicker = anychart.ui.rangePicker();

        // Set labels text.
        rangePicker.fromLabelText('Start');
        rangePicker.toLabelText('End');

        chart[chart_id[j]].selectRange('ytd');

        rangePicker.render(chart[chart_id[j]]);

        var customRanges = [
            {
                'text': '1 Month',
                'type': 'unit',
                'unit': 'month',
                'count': 1,
                'anchor': 'first-visible-date'
            },
            {
                'text': '3 Months',
                'type': 'unit',
                'unit': 'month',
                'count': 3,
                'anchor': 'range'
            },
            {
                'text': '6 Months',
                'type': 'unit',
                'unit': 'month',
                'count': 6,
                'anchor': 'range'
            },
            {
                'text': '1 Year',
                'type': 'unit',
                'unit': 'year',
                'count': 1,
                'anchor': 'range'
            },
            {
                'text': '2 Year',
                'type': 'unit',
                'unit': 'year',
                'count': 2,
                'anchor': 'range'
            },
            {
                'text': '3 Year',
                'type': 'unit',
                'unit': 'year',
                'count': 3,
                'anchor': 'range'
            },
            {
                'text': '5 Year',
                'type': 'unit',
                'unit': 'year',
                'count': 5,
                'anchor': 'range'
            },
            {
                'text': 'Full Range',
                'type': 'max'
            },
        ];

        // Set custom ranges for the range selector.
        rangeSelector.ranges(customRanges);
        rangeSelector.render(chart[chart_id[j]]);


            $.getJSON("../static/chart_annotations/"+active_ins_name[j]+".json", function(json) {
                annotationsAtServer = json; // this will show the info it in firebug console
                plot[chart_id[l]].annotations().fromJson(annotationsAtServer);
                l++;
            });

            // create ema indicator
            var settings = [mapping];
            if (overlay.length !== 0) {
                for (var k = 0; k < overlay[j].length; k++) {
                    settings.push(overlay[j][k][2]);
                    settings.push("line");
                    plot[chart_id[j]][overlay[j][k][0]].apply(plot[chart_id[j]], settings);
                }
                // adding extra Y axis to the right side
                plot[chart_id[j]].yAxis(1).orientation('right');
            }
            if (indicator[j].length !== 0){
                for (var n = 0; n < indicator[j].length; n++) {
                    var indicator_plot = chart[chart_id[j]].plot(n+1);
                    settings.push(indicator[j][n][2]);
                    // for slow/fast stochastic
                    if (~indicator[j][n][0].toLowerCase().indexOf('stochastic')) {
                        indicator[j][n][0] = 'stochastic';
                    }
                    indicator_plot[indicator[j][n][0]].apply(indicator_plot, settings);
                    indicator_plot.height("25%");
                    indicator_plot.yAxis(1).orientation('right');
                }
                // adding extra Y axis to the right side
            }

            // create scroller series
            chart[chart_id[j]].scroller().area(mapping)
                .color('#253992 0.3')
                .stroke('#253992');

            // set grid and axis settings
            chart[chart_id[j]].plot(0).yAxis(0).orientation('right');
            chart[chart_id[j]].plot(0).yAxis(1)
                .orientation('left')
                .ticks(false)
                .labels(false)
                .minorLabels(false);
            chart[chart_id[j]].plot()
                .xGrid(true)
                .yGrid(true);

            // set chart padding
            chart[chart_id[j]].padding()
                .right(35)
                .left(5)
                .top(10);

            // add annotation items in context menu
            chart[chart_id[j]].contextMenu().itemsFormatter(contextMenuItemsFormatter);

            // use annotation events to update application UI elements
            chart[chart_id[j]].listen('annotationDrawingFinish', onAnnotationDrawingFinish);
            chart[chart_id[j]].listen('annotationSelect', onAnnotationSelect);
            chart[chart_id[j]].listen('annotationUnSelect', function () {
                $colorPickerFill.removeAttr('disabled');
                // $markerSizeBtn.removeAttr('disabled');
                $('.drawing-tools-solo').find('.bootstrap-select').each(function () {
                    $(this).removeClass('open');
                })
            });
            chart[chart_id[j]].listen('chartDraw', function () {
                hidePreloader();

                var $body = $('body');
                var $textArea = '<textarea id="annotation-label"></textarea>';

                if (!$body.find('#annotation-label').length) {
                    $body.find('[data-annotation-type="label"]').length ?
                        $body.find('[data-annotation-type="label"]').after($textArea) :
                        $body.append($textArea);
                    $annotationLabel = $('#annotation-label');
                }
            });

            // add textarea for label annotation and listen events
            chart[chart_id[j]].listen('annotationDrawingFinish', function (e) {
                if (e.annotation.type === 'label') {
                    $annotationLabel.val(e.annotation.text())
                        .focus()
                        .on('change keyup paste', function (e) {
                            if (e.keyCode === 46) return;

                            try {
                                var annotation = chart[chart_id[cnt]].annotations().getSelectedAnnotation();
                                annotation.enabled();
                            } catch (err) {
                                annotation = null;
                            }

                            if (annotation) {
                                $(this).val() ? annotation.text($(this).val()) : annotation.text(' ') && $(this).val(' ');
                            }
                        });
                    chart[chart_id[cnt]].listen('annotationDrawingFinish', function (e) {
                        if (e.annotation.type === 'label') {
                            $annotationLabel.val(e.annotation.text())
                                .focus();
                        }
                    });

                    chart[chart_id[cnt]].listen('annotationSelect', function (e) {
                        if (e.annotation.type === 'label') {
                            $annotationLabel.val(e.annotation.text())
                                .focus();
                        }
                    });

                    chart[chart_id[cnt]].listen('annotationUnselect', function () {
                        if (e.annotation.type === 'label') {
                            $annotationLabel.val('');
                        }
                    });

                    cnt++;
                    if (cnt >= j)
                        cnt = 0;
                }
            });

            // set container id for the chart
            chart[chart_id[j]].container('chart-container_'+chart_id[j]);

            // initiate chart drawing
            chart[chart_id[j]].draw();
        }
    });

    function initVolumeBar() {
        $('.volume-btn').on('mouseenter', function () {
            var self = this;

            $(this).popover({
                placement: 'bottom',
                html: true,
                trigger: 'manual',
                content: function () {
                    return '<div id="volume-popover">\n' +
                        '     <div class="volume-bar-value text-center">' + $(this).attr('data-volume') + 'px' +
                        '     </div>\n' +
                        '     <input type="range" id="volume-bar" class="volume-bar" step="1" value="' + $(this).attr('data-volume') + '"' +
                        '      min="5" max="35">\n' +
                        '   </div>'
                }
            });

            $(this).popover('show');

            $(this).siblings('.popover').on('mouseleave', function () {
                setTimeout(function () {
                    if (!$('.popover:hover').length) {
                        $(self).popover('hide')
                    }
                }, 100);
            });
        }).on('mouseleave', function () {
            var self = this;

            setTimeout(function () {
                if (!$('.popover:hover').length) {
                    $(self).popover('hide')
                }
            }, 100);
        });
    }

    function createPageColorPicker() {
        var colorPicker = $('.color-picker');
        var strokeWidth;
        var STROKE_WIDTH = 1;
        colorPicker.colorpicker({
            'color': 'rgba(255,0,4,0.35)',
            'align': 'left'
        });

        colorPicker.on('create', function () {
            var color = $(this).data('color');

            if ($(this).find('.color-fill-icon[data-color]').length) {
                color = $(this).find('.color-fill-icon').attr('data-color');
            }

            $('.color-fill-icon', $(this)).css('background-color', color);
        });

        colorPicker.on('showPicker', function () {
            $(this).parent('div').find('.tooltip.in').tooltip('hide');
        });

        colorPicker.on('changeColor', function () {
            for(var k = 0; k < chart_id.length; k++) {
                var color = $(this).data('color');
                var annotation = chart[chart_id[k]].annotations().getSelectedAnnotation();
                var _annotation = annotation;

                if (annotation) {
                    if (annotation.type === 'label') {
                        $annotationLabel.focus();
                        annotation = annotation.background();
                    }

                    switch ($(this).attr('data-color')) {
                        case 'fill' :
                            annotation.fill(color);
                            break;
                        case 'stroke' :
                            strokeWidth = annotation.stroke().thickness || STROKE_WIDTH;
                            strokeDash = annotation.stroke().dash || '';
                            var settings = {
                                thickness: strokeWidth,
                                color: color,
                                dash: strokeDash
                            };

                            setAnnotationStrokeSettings(annotation, settings);
                            break;
                        case 'fontColor':
                            if (_annotation.type === 'label') _annotation.fontColor(color);
                            break;
                    }
                }

                if (color === null) {
                    $('.color-fill-icon', $(this)).addClass('colorpicker-color');
                } else {
                    $('.color-fill-icon', $(this)).removeClass('colorpicker-color')
                        .css('background-color', color);
                }
            }
        });
    }

    function removeSelectedAnnotation(chart_id) {
        var annotation = chart[chart_id].annotations().getSelectedAnnotation();
        if (annotation) chart[chart_id].annotations().removeAnnotation(annotation);

        return !!annotation;
    }

    function removeAllAnnotation(chart_id) {
        chart[chart_id].annotations().removeAllAnnotations();
    }

    function saveAnntation(chart_id, file_name){
      sendAnnotationsToServer(plot[chart_id].annotations().toJson(true), file_name);
    }

    function onAnnotationDrawingFinish() {
        setToolbarButtonActive(null);
    }

    function onAnnotationSelect(evt) {
        var annotation = evt.annotation;
        var colorFill;
        var colorStroke;
        var strokeWidth;
        var strokeDash;
        var strokeType;
        var markerSize;
        var fontColor;
        var fontSize;

        var $colorPickerFontColor = $('.color-picker[data-color="fontColor"]');

        var fontSettings = [];

        if (annotation.fill || annotation.background) {
            $colorPickerFill.removeAttr('disabled');
            colorFill = annotation.fill ? annotation.fill() : annotation.background().fill();
            colorStroke = annotation.stroke ? annotation.stroke() : annotation.background().stroke();
        } else {
            $colorPickerFill.attr('disabled', 'disabled');
        }

        if (annotation.type === 'label') {
            $annotationLabel.focus();

            fontSize = annotation.fontSize();

            $fontSize.attr('data-volume', fontSize);

            fontColor = annotation.fontColor();

            fontSettings = [];

            $labelMethod.each(function () {
                var method = $(this).data().labelMethod;

                fontSettings.push(annotation[method]());
            });

            // update font settings select
            $fontSettings.val(fontSettings).selectpicker('refresh');

            annotation = annotation.background();
        }

        if (annotation.fill && typeof annotation.fill() === 'function') {
            colorFill = $colorPickerFill.find('.color-fill-icon').css('background-color');
        }

        if (colorStroke !== 'none') {
            colorStroke = annotation.stroke().color;
            strokeWidth = annotation.stroke().thickness;
            strokeDash = annotation.stroke().dash;
        }

        if (annotation.type === 'marker') {
            markerSize = annotation.size();
            $markerSize.attr('data-volume', markerSize);
        } else {
            $markerSizeBtn.attr('disabled', 'disabled');
        }

        if (annotation.fill !== undefined) {
            annotation.fill(colorFill);
        }

        if (fontSize) {
            evt.annotation.fontSize(fontSize);
        }

        switch (strokeDash) {
            case '1 1' :
                strokeType = 7;
                break;
            case '10 5' :
                strokeType = 8;
                break;
            default :
                if (strokeWidth) {
                    strokeType = 6;
                }
                break;
        }

        $colorPickerFill.find('.color-fill-icon').css('background-color', colorFill);
        $colorPickerStroke.find('.color-fill-icon').css('background-color', colorStroke);
        $colorPickerFontColor.find('.color-fill-icon').css('background-color', fontColor);
        $strokeSettings.val([strokeWidth, strokeType]).selectpicker('refresh');
    }

    function contextMenuItemsFormatter(items) {
        // insert context menu item on 0 position
        items['annotations-remove-selected'] = {
            text: "Remove selected annotation",
            action: removeSelectedAnnotation,
            index: -10
        };

        // insert context menu item on 1 position
        items['annotations-remove-all'] = {
            text: "Remove all annotations",
            action: removeAllAnnotation,
            index: -5
        };

        items['annotations-save'] = {
            text: "Save annotations",
            action: saveAnntation,
            index: -5
        };

        // insert context menu separator
        items['annotations-separator'] = {
            index: -4
        };

        return items;
    }

    function setToolbarButtonActive(type, markerType) {
        var $buttons = $('.btn[data-annotation-type]');
        $buttons.removeClass('active');
        $buttons.blur();

        if (type) {
            var selector = '.btn[data-annotation-type="' + type + '"]';
            if (markerType) selector += '[data-marker-type="' + markerType + '"]';
            $(selector).addClass('active');
        }
    }

    function updatePropertiesBySelectedAnnotation(colorStroke, strokeWidth, strokeType) {
        var annotation = chart.annotations().getSelectedAnnotation();
        if (annotation === null) return;

        if (annotation.type === 'label') {
            $annotationLabel.focus();
            annotation = annotation.background();
        }

        switch (strokeType) {
            case '6' :
                strokeType = null;
                break;
            case '7' :
                strokeType = '1 1';
                break;
            case '8' :
                strokeType = '10 5';
                break;
        }

        var settings = {
            thickness: strokeWidth,
            color: colorStroke,
            dash: strokeType
        };

        setAnnotationStrokeSettings(annotation, settings);
    }

    function setAnnotationStrokeSettings(annotation, settings) {
        annotation.stroke(settings);
        if (annotation.hovered || annotation.selected) {
            annotation.hovered().stroke(settings);
            annotation.selected().stroke(settings);
        }
    }

    function hidePreloader() {
        $('#loader-wrapper').fadeOut('slow');
    }

    function initTooltip(position) {
        $(document).ready(function () {
            $('[data-toggle="tooltip"]').tooltip({
                'placement': position,
                'animation': false
            }).on('show.bs.tooltip', function () {
                if ($(this).hasClass('color-picker') && $('.colorpicker-visible').length) {
                    return false
                }
            })
        });
    }

    function normalizeFontSettings(val) {
        var fontMethods = {};

        $labelMethod.each(function () {
            fontMethods[$(this).data().labelMethod] = null;
        });

        val && val.forEach(function (item) {
            if (item) {
                $fontSettings.find('[data-label-method]').each(function () {
                    var $that = $(this);
                    var $el = $(this).find('option').length ? $(this).find('option') : $(this);

                    $el.each(function () {
                        if ($(this).val() === item) {
                            fontMethods[$that.attr('data-label-method')] = item;
                        }
                    });
                });
            }
        });

        return fontMethods
    }

    $(document).ready(function () {
        for (var j = 0; j < chart_id.length; j++) {
            $('select.choose-drawing-tools-'+chart_id[j]).change({chart_id: chart_id[j]}, changeAnnotations);
            $('select.choose-marker-'+chart_id[j]).change({chart_id: chart_id[j]}, changeAnnotations);
            $('[data-annotation-type_'+chart_id[j]+']').click({chart_id: chart_id[j]}, changeAnnotations);

            $('#annotation-label-autosize_'+chart_id[j]).click({chart_id: chart_id[j]}, labelAutosize);
        }
        function labelAutosize(event) {
            var annotation = chart[event.data.chart_id].annotations().getSelectedAnnotation();

            if (annotation && annotation.type === 'label') {
                annotation.width(null);
                annotation.height(null);
            }

            setToolbarButtonActive(null);

            $annotationLabel.focus();
        }
        function changeAnnotations(event) {
            var $that = $(this);

            setTimeout(function () {
                var $target = $that;
                var active = $target.hasClass('active');
                var markerSize = $markerSize.attr('data-volume');
                var fontSize = $fontSize.attr('data-volume');
                var fontColor = $('[data-color="fontColor"]').find('.color-fill-icon').css('background-color');

                var colorFill = $colorPickerFill.find('.color-fill-icon').css('background-color');
                var colorStroke = $colorPickerStroke.find('.color-fill-icon').css('background-color');

                var strokeType;
                var strokeWidth;
                var strokeDash;
                var STROKE_WIDTH = 1;

                if ($strokeSettings.val()) {
                    switch ($strokeSettings.val()[0]) {
                        case '6' :
                        case '7' :
                        case '8' :
                            strokeType = $strokeSettings.val()[0];
                            strokeWidth = $strokeSettings.val()[1] || STROKE_WIDTH;
                            break;
                        default :
                            strokeWidth = $strokeSettings.val()[0];
                            strokeType = $strokeSettings.val()[1];
                            break;
                    }
                }

                switch (strokeType) {
                    case '6' :
                        strokeDash = null;
                        break;
                    case '7' :
                        strokeDash = '1 1';
                        break;
                    case '8' :
                        strokeDash = '10 5';
                        break;
                }

                var strokeSettings = {
                    thickness: strokeWidth,
                    color: colorStroke,
                    dash: strokeDash
                };

                var fontSettings = normalizeFontSettings($fontSettings.val());

                if (active) {
                    chart[event.data.chart_id].annotations().cancelDrawing();
                    setToolbarButtonActive(null);
                } else {
                    var type = $target.attr("data-annotation-type_"+event.data.chart_id) || $target.find('option:selected').attr("data-annotation-type_"+event.data.chart_id);

                    if (!$target.attr("data-annotation-type_"+event.data.chart_id)) {
                        var markerType = $target.find('option:selected').data().markerType;
                    }

                    setToolbarButtonActive(type, markerType);

                    if (type) {

                        if (!$target.attr("data-annotation-type_"+event.data.chart_id)) {
                            var markerAnchor = $target.find('option:selected').data().markerAnchor;
                        }

                        var drawingSettings = {
                            type: type,
                            size: markerSize,
                            markerType: markerType,
                            anchor: markerAnchor,
                            fontSize: fontSize,
                            fontColor: fontColor
                        };

                        $.extend(drawingSettings, fontSettings);

                        if (type === 'label') {
                            drawingSettings.anchor = fontSettings.anchor;

                            drawingSettings.background = {
                                fill: colorFill,
                                stroke: strokeSettings
                            };
                            drawingSettings.hovered = {
                                background: {
                                    stroke: strokeSettings
                                }
                            };
                            drawingSettings.selected = {
                                background: {
                                    stroke: strokeSettings
                                }
                            };
                        } else {
                            drawingSettings.fill = colorFill;
                            drawingSettings.stroke = strokeSettings;
                            drawingSettings.hovered = {
                                stroke: strokeSettings
                            };
                            drawingSettings.selected = {
                                stroke: strokeSettings
                            };
                        }

                        chart[event.data.chart_id].annotations().startDrawing(drawingSettings);
                    }
                }

                var annotation = chart[event.data.chart_id].annotations().getSelectedAnnotation();

                if (annotation.fill || annotation.background) {
                    $colorPickerFill.removeAttr('disabled');
                } else {
                    $colorPickerFill.attr('disabled', 'disabled');
                }

                $target.val('');
            }, 1);
        }

        $('.btn[data-action-type]').click(function (evt) {
            for (var k = 0; k < chart_id.length; k++) {
                var annotation = chart[chart_id[k]].annotations().getSelectedAnnotation();
                var $target = $(evt.currentTarget);
                $target.blur();
                var type = $target.attr('data-action-type');

                switch (type) {
                    case 'removeAllAnnotations-'+chart_id[k]:
                        removeAllAnnotation(chart_id[k]);
                        break;
                    case 'removeSelectedAnnotation-'+chart_id[k] :
                        removeSelectedAnnotation(chart_id[k]);
                        break;
                    case 'saveAnnotations-'+chart_id[k] :
                        saveAnntation(chart_id[k], active_ins_name[k]);
                        break;
                    case 'unSelectedAnnotation' :
                        chart.annotations().unselect(annotation).cancelDrawing();
                        setToolbarButtonActive(null);
                        break;
                }
            }

        });

        $strokeSettings.on('change', function () {
            var strokeWidth;
            var strokeType;
            var STROKE_WIDTH = 1;
            var colorStroke = $colorPickerStroke.find('.color-fill-icon').css('background-color');

            if ($(this).val()) {
                switch ($(this).val()[0]) {
                    case '6' :
                    case '7' :
                    case '8' :
                        strokeType = $(this).val()[0];
                        strokeWidth = $(this).val()[1] || STROKE_WIDTH;
                        break;
                    default :
                        strokeType = $(this).val()[1];
                        strokeWidth = $(this).val()[0];
                        break;
                }

                updatePropertiesBySelectedAnnotation(colorStroke, strokeWidth, strokeType);
            }
        });

        $markerSize.on('change', function () {
            var annotation = chart.annotations().getSelectedAnnotation();

            if (annotation && annotation.type === 'marker') {
                annotation.size($(this).val());
            }
        });

        $('body').on('change', '.volume-bar', function () {
            for (var k = 0; k < chart_id.length; k++) {
                var annotation = chart[chart_id[k]].annotations().getSelectedAnnotation();

                var $popover = $(this).closest('.popover');

                $popover.prev('.volume-btn')
                    .attr('data-volume', $(this).val());

                $popover.find('.volume-bar-value').text($(this).val() + 'px');

                if (annotation && annotation.type === 'label' &&
                    $popover.prev('.volume-btn').attr('data-el-size') === 'label') {
                    annotation.fontSize($(this).val());
                    $annotationLabel.focus();
                } else if (annotation && annotation.type === 'marker' &&
                    $popover.prev('.volume-btn').attr('data-el-size') === 'marker') {
                    annotation.size($(this).val());
                }
            }
        });

        $fontSettings.on('change', function () {
            for(var k = 0; k < chart_id.length; k++) {
                var annotation = chart[chart_id[k]].annotations().getSelectedAnnotation();

                if (annotation && annotation.type === 'label') {

                    var fontSettings = normalizeFontSettings($(this).val());

                    $labelMethod.each(function () {
                        var method = $(this).data().labelMethod;

                        annotation[method](fontSettings[method]);
                    });

                    $annotationLabel.focus();
                }
            }
        });

        $('html').keyup(function (e) {
            if (e.keyCode === 46) {
                removeSelectedAnnotation();
            }
        });
    });
})();