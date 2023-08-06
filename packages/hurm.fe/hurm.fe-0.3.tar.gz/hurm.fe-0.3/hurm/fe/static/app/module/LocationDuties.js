// -*- coding: utf-8 -*-
// :Project:   hurm -- Location duties
// :Created:   sab 13 feb 2016 20:15:04 CET
// :Author:    Lele Gaifax <lele@metapensiero.it>
// :License:   GNU General Public License version 3 or later
// :Copyright: © 2016 Lele Gaifax
//

/*jsl:declare Ext*/
/*jsl:declare HuRM*/
/*jsl:declare MP*/
/*jsl:declare _*/
/*jsl:declare ngettext*/

Ext.define('HuRM.module.LocationDuties.Actions', {
    extend: 'MP.action.StoreAware',

    uses: [
        'Ext.Action',
        'Ext.form.field.TextArea',
        'MP.form.Panel',
        'MP.window.Notification'
    ],

    statics: {
        EDIT_ACTION: 'edit_duty'
    },

    initActions: function() {
        var me = this;
        var ids = me.statics();

        me.callParent();

        me.editAction = me.addAction(new Ext.Action({
            itemId: ids.EDIT_ACTION,
            text: _('Modify'),
            tooltip: _('Edit selected duty.'),
            iconCls: 'edit-record-icon',
            disabled: true,
            needsOneSelectedRow: true,
            handler: function() {
                var record = me.component.getSelectionModel().getSelection()[0];
                me.showEditWindow(record);
            }
        }));
    },

    attachActions: function() {
        var me = this;

        me.callParent();

        var tbar = me.component.child('#ttoolbar');

        tbar.add(2, ' ', me.editAction);

        me.component.on({
            itemdblclick: function() {
                if(!me.editAction.isDisabled())
                    me.editAction.execute();
            }
        });

        me.component.store.on({
            add: function(store, records) {
                //jsl:unused store
                var record = records[0];
                me.showEditWindow(record);
            }
        });
    },

    showEditWindow: function(record) {
        var me = this;
        var desktop = me.module.app.getDesktop();
        var win = desktop.getWindow('edit-duty-win');

        // If the window is already present, destroy and recreate it,
        // to reapply configuration and filters
        if(win) {
            win.destroy();
        }

        var metadata = me.module.config.metadata,
            size = desktop.getReasonableWindowSize(1000, 440),
            orig_url,
            editors = metadata.editors({
                '*': {
                    editor: MP.form.Panel.getDefaultEditorSettingsFunction('100%')
                },
                'Person': {
                    editor: {
                        listeners: {
                            beforequery: function(event) {
                                var store = event.combo.store,
                                    idtask = record.get('idtask');
                                if(!orig_url)
                                    orig_url = store.proxy.url;
                                store.proxy.url = Ext.String.urlAppend(orig_url,
                                                                       'idtask='+idtask);
                                delete event.combo.lastQuery;
                            }
                        }
                    }
                },
                'note': {
                    editor: {
                        xtype: 'htmleditor'
                    }
                }
            }),
            form = Ext.create('MP.form.Panel', {
                autoScroll: true,
                fieldDefaults: {
                    labelWidth: 100,
                    margin: '15 10 0 10'
                },
                items: [editors.Person,
                        editors.starttime,
                        editors.endtime,
                        editors.note],
                buttons: [{
                    text: _('Cancel'),
                    handler: function() {
                        if(record.phantom) {
                            record.store.deleteRecord(record);
                        }
                        win.close();
                    }
                }, {
                    text: _('Confirm'),
                    formBind: true,
                    handler: function() {
                        if(form.isValid()) {
                            form.updateRecord(record);
                            win.close();
                            Ext.create("MP.window.Notification", {
                                position: 't',
                                width: 260,
                                title: _('Changes have been applied…'),
                                html: _('Your changes have been applied <strong>locally</strong>.<br/><br/>To make them permanent you must click on the <blink>Save</blink> button.'),
                                iconCls: 'info-icon'
                            }).show();
                        }
                    }
                }]
            });

        win = desktop.createWindow({
            id: 'edit-duty-win',
            title: _('Edit duty'),
            iconCls: 'edit-duty-icon',
            width: size.width,
            height: size.height,
            modal: true,
            items: form,
            closable: false,
            minimizable: false,
            maximizable: false,
            resizable: false
        });

        form.loadRecord(record);

        win.show();
    }
});


Ext.define('HuRM.module.LocationDuties', {
    extend: 'MP.desktop.Module',

    requires: [
        'MP.grid.Panel'
    ],

    uses: [
        'HuRM.module.LocationDuties.Actions'
    ],

    id: 'location-duties-win',
    iconCls: 'person-duties-icon',
    launcherText: null,
    launcherTooltip: null,

    config: {
        xtype: 'editable-grid',
        pageSize: 15,
        autoShowAllEditors: false,
        clicksToEdit: 0,
        dataURL: '/data/location_duties',
        sorters: ['Task_date', 'Task_starttime', 'starttime'],
        stripeRows: true
    },

    getConfig: function(callback) {
        var me = this,
            config = me.config;

        if(!config.metadata) {
            MP.data.MetaData.fetch(config.dataURL, me, function(metadata) {
                var overrides = {},
                    fields = metadata.fields(overrides);

                Ext.apply(config, {
                    metadata: metadata,
                    fields: fields,
                    columns: metadata.columns(overrides, false),
                    idProperty: metadata.primary_key,
                    totalProperty: metadata.count_slot,
                    successProperty: metadata.success_slot,
                    rootProperty: metadata.root_slot,
                    plugins: [
                        Ext.create('HuRM.module.LocationDuties.Actions', { module: me }),
                    ]
                });
                callback(config);
                me.app.on('logout', function() { delete config.metadata; }, me, { single: true });
            });
        } else {
            callback(config);
        }
    },

    createOrShowWindow: function(idedition, edition, idlocation, location) {
        var me = this,
            desktop = me.app.getDesktop(),
            win = desktop.getWindow(me.id);

        // If the window is already present, destroy and recreate it,
        // to reapply configuration and filters
        if(win) {
            win.destroy();
        }

        me.configure(
            [me.getConfig],
            function(done) {
                var size = desktop.getReasonableWindowSize(800, 400),
                    config = Ext.apply({
                        stickyFilters: [{
                            id: 'edition',
                            property: 'idedition',
                            value: idedition
                        }, {
                            id: 'location',
                            property: 'idlocation',
                            value: idlocation
                        }]
                    }, me.config);

                win = desktop.createWindow({
                    id: me.id,
                    title: Ext.String.format(
                        // TRANSLATORS: this is the title of the location duties
                        // window, params are location description and edition.
                        _("Duties at location “{0}” in edition “{1}”"),
                        location, edition),
                    width: size.width,
                    height: size.height,
                    iconCls: me.iconCls,
                    items: [config]
                });

                var grid = win.child('editable-grid');

                // Fetch the first page of records, and when done show
                // the window
                grid.store.load({
                    params: {start: 0, limit: me.pageSize},
                    callback: function() {
                        win.on({show: done, single: true});
                        win.show();
                    }
                });
            });
    }
});
