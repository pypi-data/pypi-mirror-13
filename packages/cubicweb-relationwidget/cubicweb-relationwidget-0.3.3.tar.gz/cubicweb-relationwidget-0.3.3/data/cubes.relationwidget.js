/* jshint strict: false, white: true */
/* global cw: false, Namespace: false, _: false */

cw.cubes.relationwidget = new Namespace('cw.cubes.relationwidget');

(function ($) {
    $.fn.relationwidget = function (options) {
        var $widget = $(this),
            widgetuid = $widget.attr('id'),
            defaultSettings = {
                editOptions: {
                    required: false,
                    multiple: true,
                    searchurl: '<required-option>'
                },
                dialogOptions: {
                }
            };
        if (options.onValidate) { onValidate = options.onValidate;}
        else {
            function onValidate(selected) {
                var $divgroup = $('#inputs-for-' + widgetuid);
                $divgroup.empty();
                var snippets = widgetuid.split('-');
                var inputname = snippets[1] + '-' + snippets[2] + ':' + snippets[3];
                for (var eid in selected) {
                    var label = selected[eid];
                    $divgroup.append(
                        $('<div />').append(
                            $('<label/>').html(' ' + label).prepend(
                                $('<input/>').attr({
                                    type: 'checkbox', checked: 'checked',
                                    name: inputname, value: eid,
                                    id: (inputname + '-' + eid),
                                    'data-html-label': label}
                                                  )
                            )
                        )
                    );
                }
            }
        }
        var editSettings = $.extend({}, defaultSettings.editOptions, options.editOptions),
            dialogSettings = $.extend({}, defaultSettings.dialogOptions, options.dialogOptions);

        function validate($modalDialog) {
            var $alert = $widget.find('.cw-relationwidget-alert');
            $alert.empty().addClass('hidden');
            var selected = getSelectedValues();
            if (editSettings.required && Object.keys(selected).length === 0) {
                $alert.text(_('required_error')).removeClass('hidden');
                return;
            }
            onValidate(selected);
            $modalDialog.modal('hide');
        }

        function initSelected() {
            // open entities link in new tab
            $widget.find('.cw-relationwidget-table table a').attr('target', '_blank');
            var $selected = $('#inputs-for-' + widgetuid + ' input');
            if ($selected.length === 0) {
                var label = $('<div/>').text(_('no selected entities'));
                $widget.find('.cw-relationwidget-linked-summary').append(label);
            } else {
                $selected.each(function (index, input) {
                    var $input = $(input);
                    if ($input.prop("checked")) {
                        var eid = $input.attr('value');
                        addOrUpdateCheckbox(eid, $input.data('html-label'), true);
                        $widget.find('.cw-relationwidget-table input[value='+eid+']').prop("checked", true);
                    }
                });
            }
        }

        function getSelectedValues() {
            var selected = {};
            $widget.find('.cw-relationwidget-linked-summary label').each(function () {
                var $this = $(this);
                var eid = $this.find('input:checked').attr('id');
                if (eid) {
                    selected[eid] = $('a', $this)[0].outerHTML;
                }
            });
            return selected;
        }

        function syncCheckboxes() {
            // syncCheckboxes MUST be called after each pagination on 'server-response'
            // which allows to know when to refresh this for the prev/next pages,
            // open entities link in new tab
            $widget.find('.cw-relationwidget-table table a').attr('target', '_blank');
            var selected = getSelectedValues();
            for (var eid in selected) {
                var $input = $widget.find('.cw-relationwidget-table input[value='+eid+']');
                if ($input.length === 1) {
                    // this input can be on another page
                    $input.prop('checked', 'checked');}
            }
        }

        function emptyData() {
            $widget.find('.cw-relationwidget-linked-summary').empty();
            var label = $('<div/>').text(_('no selected entities'));
            $widget.find('.cw-relationwidget-linked-summary').append(label);
        }

        function toggleRelatedCheckbox(eid, check) {
            var $input = $widget.find('.cw-relationwidget-table input[value='+eid+']');
            $input.prop("checked", check);
        }

        function addOrUpdateCheckbox(eid, htmlLabel, checked) {
            $widget.find('.cw-relationwidget-linked-summary div').hide();
            var $input = $('input#' + eid);
            if ($input.length === 0) {
                if (checked) {
                    $widget.find('.cw-relationwidget-linked-summary').append(
                        $('<li/>').addClass('add_related').append(
                            $('<label/>').html(' ' + htmlLabel).prepend(
                                $('<input type="checkbox" checked="checked">')
                                    .attr('id', eid)
                                    .click(function () {
                                        toggleRelatedCheckbox(eid, $(this).prop('checked'));
                                    })
                            )
                        )
                    );
                }
            }
            else {
                $input.prop("checked", checked);
            }
        }

        function created(result, formid, cbargs) {
            var $node = $('<div/>');
            var eid = result[2].eid;
            var params = {vid: 'incontext', eid: eid};
            $node.loadxhtml(AJAX_BASE_URL, ajaxFuncArgs('view', params))
                .addCallback(function() {
                    console.log('incontext result', $node.html());
                    addOrUpdateCheckbox(eid, $node.html(), true);
                    resetCreationForm();
                });
            var $wrapper = $widget.find('.cw-relationwidget-table .table-wrapper');
            params = {vid: 'select_related_entities_table',
                      rql: $wrapper.data('rql')};
            $wrapper.loadxhtml(AJAX_BASE_URL, ajaxFuncArgs('view', params));
        };
        cw.cubes.relationwidget.created = created;

        function creationFailed(result, formid, cbargs) {
            unfreezeFormButtons(formid);
            // Failures
            _clearPreviousErrors(formid);
            var descr = result[1];
            var errmsg;
            // Unknown structure
            if ( !cw.utils.isArrayLike(descr) || descr.length != 2 ) {
                errmsg = descr;
            } else {
                _displayValidationerrors(formid, descr[0], descr[1]);
                errmsg = _("please correct errors below");
            }
            var tpl = '<div class="alert alert-info">' +
                      '<button class="close" data-dismiss="alert" type="button">x</button>' +
                      errmsg + '</div>';
            var $creationForm = $widget.find('.rw-creation-form');
            $creationForm.find('.alert').remove();
            $creationForm.prepend($(tpl));
            return false;
        }
        cw.cubes.relationwidget.creationFailed = creationFailed;

        function setUpCreationForm() {
            $widget.find('.rw-creation-cancel').click(resetCreationForm);
        }

        function resetCreationForm() {
            $widget.find('.toggle-cw-relationwidget-table').tab('show');
            var $creationForm = $widget.find('.rw-creation-form');
            var params = {vid: 'rw-creation',
                          etype: $creationForm.data('etype')};
            $creationForm
                .loadxhtml(AJAX_BASE_URL, ajaxFuncArgs('view', params))
                .addCallback(setUpCreationForm);
        }

        // instantiate the dialog window and connect the validation button
        $widget.modal(dialogSettings);
        $widget.find('.modal-title').text(dialogSettings.title);
        $widget.find('button.save').click(function() {validate($widget);});
        $widget.one('hide.bs.modal', function() {
            $widget.off('click');
            $widget.off('server-response');
            $widget.find('button.save').off('click');
            $widget.find('.modal-body').empty();
        });

        var d = $widget.find('.modal-body').loadxhtml(editSettings.searchurl);
        d.addCallback(function () {
            setUpCreationForm();
            // bind the pagination response to synchronize the checked values
            // fixme should only do this on the pagination callback, but
            // this is not possible for the moment
            $widget.bind('server-response', function (e) {syncCheckboxes();});
            var checkboxesSelector = '.cw-relationwidget-table input[type=checkbox]';
            $widget.on('click', checkboxesSelector, function (e) {
                var $input = $(this);
                // uncheck other selected inputs
                if (!editSettings.multiple) {
                    $widget.find('.cw-relationwidget-table input[type=checkbox]:not([value=' + $input.attr('value') + '])').prop('checked', false);
                }
                var htmlLabel = $input.closest('tr').find('td[data-label-cell]').html();
                var checked = $input.prop('checked');
                if (!editSettings.multiple && checked) {
                    // only one value can be set on this relation
                    emptyData();
                }
                addOrUpdateCheckbox(this.value, htmlLabel, checked);
            });
            initSelected();
        });
    };
})(jQuery);
