// copyright 2015 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
// contact http://www.logilab.fr -- mailto:contact@logilab.fr
//
// This program is free software: you can redistribute it and/or modify it under
// the terms of the GNU Lesser General Public License as published by the Free
// Software Foundation, either version 2.1 of the License, or (at your option)
// any later version.
//
// This program is distributed in the hope that it will be useful, but WITHOUT
// ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
// FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
// details.
//
// You should have received a copy of the GNU Lesser General Public License along
// with this program. If not, see <http://www.gnu.org/licenses/>.

// saem_ref.js may be loaded while jquery.ui isn't because we don't care of the widget below. Handle
// this nicely
if ($.ui !== undefined) {
    // Widget based on jquery.ui.autocomplete (see http://jqueryui.com/autocomplete/#default)
    $.widget("custom.check_similar_values", $.ui.autocomplete, {
        _renderMenu: function(ul, items) {
            var that = this, currentCategory = "";
            // Add a class ('similar_names-list') to the whole list, to be customised in the css file
            ul.addClass("similar_values-list")
            $.each(items, function(index, item) {
                var li;
                // display items categories (there may be various)
                // 'similar_names-category' => the 'category' won't be displayed the same way
                // as the other items, see css file.
                if (item.category != currentCategory) {
                    ul.append("<li class='similar_values-category'>" + item.category + "</li>");
                    currentCategory = item.category;
                }
                // display item
                li = that._renderItem(ul, item);
            });
        },
        _renderItem: function(ul, item) {
            // _renderItem overloaded so that item labels aren't put into <a>
            // markups, since we don't want them to be clickable
            return $("<li>")
                .append(item.label)
                .appendTo(ul);
        }
    });
}

saem = {
    update_datepicker_minmax: function(domid, minmax, value) {
        if (/\d{2}\/\d{2}\/\d{4}/.test(value)) {
            cw.jqNode(domid).datepicker("option", minmax, value);
        }
    },

    // handle case of a autocompletion field to select concept coupled to a combo selecting the
    // vocabulary.
    initSchemeConceptFormField: function(masterSelectId, dependentSelectId) {
        var masterSelect = cw.jqNode(masterSelectId);
        // bind vocabulary select to update concept autocompletion input on value change
        masterSelect.change(function() {
            saem.updateCurrentSchemeEid(this);
            saem.resetConceptFormField(dependentSelectId);
        });
        // initialize currentSchemeEid by looking the value of the master field
        saem.updateCurrentSchemeEid(masterSelect);
        // also bind the autocompletion widget
        cw.jqNode(dependentSelectId+'Label')
            .autocomplete({
                source: function(request, response) {
                    if (saem.currentSchemeEid) {
                        var form = ajaxFuncArgs('keyword_concepts',
                                                {'q': request.term,
                                                 'scheme': saem.currentSchemeEid});
                        var d = loadRemote(AJAX_BASE_URL, form, 'POST');
                        d.addCallback(function (suggestions) { response(suggestions); });
                    }
                },
                focus: function( event, ui ) {
                    cw.jqNode(dependentSelectId+'Label').val(ui.item.label);
                    return false;
                },
                select: function(event, ui) {
                    cw.jqNode(dependentSelectId+'Label').val(ui.item.label);
                    cw.jqNode(dependentSelectId).val(ui.item.value);
                    return false;
                },
                'mustMatch': true,
                'limit': 100,
                'delay': 300})
            .tooltip({
                tooltipClass: "ui-state-highlight"
            });

        // add key press and focusout event handlers so that value which isn't matching a vocabulary
        // value will be erased
        resetIfInvalidChoice = function() {
            if (saem.currentSchemeEid) {
                var validChoices = $.map($('ul.ui-autocomplete li'),
                                         function(li) {return $(li).text();});
                var value = cw.jqNode(dependentSelectId + 'Label').val();
                if ($.inArray(value, validChoices) == -1) {
                    saem.resetConceptFormField(dependentSelectId);
                }
            }
        };
        cw.jqNode(dependentSelectId+'Label').keypress(function(evt) {
            if (evt.keyCode == $.ui.keyCode.ENTER || evt.keyCode == $.ui.keyCode.TAB) {
                resetIfInvalidChoice();
            }
        });
        cw.jqNode(dependentSelectId+'Label').focusout(function(evt) {
            resetIfInvalidChoice();
        });
    },
    updateCurrentSchemeEid: function(masterSelect) {
        saem.currentSchemeEid = $(masterSelect).val();
        if (saem.currentSchemeEid == '__cubicweb_internal_field__') {
            saem.currentSchemeEid = null;
        }
    },
    resetConceptFormField: function(dependentSelectId) {
        cw.jqNode(dependentSelectId+'Label').val('');
        cw.jqNode(dependentSelectId).val('');
    },

    toggleFormMetaVisibility: function(domid) {
        $node = cw.jqNode(domid);
        $node.toggleClass('hidden');
        $a = $node.parent().children('a');
        if ($a.attr('class') == 'icon-list-add') {
            $a.attr('class', 'icon-up-open');
        } else {
            $a.attr('class', 'icon-list-add');
        }
    },

    buildRelationValidate: function(eid, rtype, role, refresh_view) {
        var validate = function(selected) {
            var d = asyncRemoteExec('add_relations', eid, rtype, role, selected);
            d.addCallback(function() {
                $('#' + refresh_view + eid).loadxhtml(
                    AJAX_BASE_URL, ajaxFuncArgs('view', {eid: eid, vid: refresh_view}));
            });
        };
        return validate;
    },

    buildSedaImportValidate: function(eid) {
        var validate = function(selected) {
            for (var cloned_eid in selected) {
                document.location = BASE_URL + 'saem_ref.seda.doimport?eid=' + eid + '&cloned=' + cloned_eid;
            }
        };
        return validate;
    },

    relateWidget: function(domid, search_url, title, multiple, onValidate) {
        options = {'dialogOptions': {'title': title},
                   'editOptions': {'required': true,
                                   'multiple': multiple,
                                   'searchurl': search_url}
                  };
        options.onValidate = onValidate;
        cw.jqNode(domid).relationwidget(options);
    },

    sedaTree: function(domid, msg) {
        var $tree = cw.jqNode(domid);
        // tree display and basic controls.
        $tree.tree({
            dragAndDrop: true,
            autoOpen: 0,  // only open level-0
            selectable: false,
            autoEscape: false,
            closedIcon: $('<i class="glyphicon glyphicon-expand"></i>'),
            openedIcon: $('<i class="glyphicon glyphicon-collapse-down"></i>'),
            onCanMove: function(node) {
                return remoteExec('seda_movable', node.id);
            },
            onCanMoveTo: function(moved_node, target_node, position) {
                if ( target_node.id === undefined ) {
                    return false;
                }
                else {
                    return remoteExec('seda_may_set_parent', moved_node.id,
                                      target_node.id);
                }
            },
            onCreateLi: function(node, $li) {
                var selectedId = $tree.tree('getTree').children[0].selected;
                if ( selectedId !== null && node.id === selectedId ) {
                    // add "selected" CSS class so that the current element in
                    // the tree gets highlighted.
                    $li.find('.jqtree-title').addClass('selected');
                }
            }
        });
        // tree events bindings.
        $tree.bind(
            'tree.init',
            function() {
                var selectedId = $tree.tree('getTree').children[0].selected;
                var node = $tree.tree('getNodeById', selectedId);
                var parentNode = node.parent;
                while (parentNode !== null) {
                    $tree.tree('openNode', parentNode);
                    parentNode = parentNode.parent;
                }
            }
        );
        $tree.bind(
            'tree.move',
            function(event) {
                event.preventDefault();
                // do the move first, and then POST back.
                event.move_info.do_move();
                asyncRemoteExec('seda_reparent', event.move_info.moved_node.id,
                                event.move_info.target_node.id);
            }
        );
    },

    ajaxRemoveRelation: function (eid, relatedeid, rtype, role, refresh_view) {
        if (role == 'subject') {
            var d = asyncRemoteExec('delete_relation', rtype, eid, relatedeid);
        } else {
            var d = asyncRemoteExec('delete_relation', rtype, relatedeid, eid);
        }
        d.addCallback(function() {
            $('#' + refresh_view + eid).loadxhtml(
                AJAX_BASE_URL, ajaxFuncArgs('view', {eid: eid, vid: refresh_view}));
        });
    }

};


$(cw).one('server-response', function() {
    var elem = $('.truncate');
    if ( elem.length ) {
        elem.expander({
            slicePoint: 150,
            expandText: '[+]',
            moreClass: 'text-muted',
            userCollapseText: '[^]',
        });
    }
});
