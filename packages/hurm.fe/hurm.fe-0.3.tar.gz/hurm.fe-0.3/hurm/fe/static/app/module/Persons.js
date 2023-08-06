// -*- coding: utf-8 -*-
// :Project:   hurm -- Persons management windows
// :Created:   lun 01 feb 2016 20:33:10 CET
// :Author:    Lele Gaifax <lele@metapensiero.it>
// :License:   GNU General Public License version 3 or later
// :Copyright: © 2016 Lele Gaifax
//

/*jsl:declare Ext*/
/*jsl:declare _*/
/*jsl:declare MP*/
/*jsl:declare HuRM*/

Ext.define('HuRM.module.Persons.Actions', {
    extend: 'MP.action.StoreAware',

    uses: [
        'Ext.Action',
        'Ext.form.field.TextArea',
        'MP.form.Panel',
        'MP.window.Notification'
    ],

    statics: {
        EDIT_ACTION: 'edit_person',
        AVAILS_ACTION: 'person_avails',
        DUTIES_ACTION: 'person_duties',
        PRINT_DUTIES_ACTION: 'print_duties'
    },

    initActions: function() {
        var me = this;
        var ids = me.statics();

        me.callParent();

        me.editAction = me.addAction(new Ext.Action({
            itemId: ids.EDIT_ACTION,
            text: _('Modify'),
            tooltip: _('Edit selected person.'),
            iconCls: 'edit-record-icon',
            disabled: true,
            needsOneSelectedRow: true,
            handler: function() {
                var record = me.component.getSelectionModel().getSelection()[0];
                me.showEditWindow(record);
            }
        }));

        me.availsAction = me.addAction(new Ext.Action({
            itemId: ids.AVAILS_ACTION,
            text: _('Availabilities'),
            tooltip: _('Availability of the selected person.'),
            iconCls: 'persons-icon',
            disabled: true,
            needsOneSelectedRow: true,
            handler: function() {
                var record = me.component.getSelectionModel().getSelection()[0],
                    idperson = record.get('idperson'),
                    person = record.get('FullName');
                me.module.showAvailsWindow(idperson, person);
            }
        }));

        me.dutiesAction = me.addAction(new Ext.Action({
            itemId: ids.DUTIES_ACTION,
            text: _('Duties'),
            tooltip: _('Duties assigned to the selected person.'),
            iconCls: 'duties-icon',
            disabled: true,
            needsOneSelectedRow: true,
            handler: function() {
                var record = me.component.getSelectionModel().getSelection()[0],
                    idperson = record.get('idperson'),
                    person = record.get('FullName');
                me.module.showDutiesWindow(idperson, person);
            }
        }));

        me.printDutiesAction = me.addAction(new Ext.Action({
            itemId: ids.PRINT_DUTIES_ACTION,
            text: _('Duties'),
            tooltip: _('Print this person duties.'),
            iconCls: 'pdf-icon',
            disabled: true,
            needsOneSelectedRow: true,
            needsCleanStore: true,
            handler: function() {
                var record = me.component.getSelectionModel().getSelection()[0],
                    idperson = record.get('idperson');
                me.module.printDuties(idperson);
            }
        }));
    },

    attachActions: function() {
        var me = this;

        me.callParent();

        var tbar = me.component.child('#ttoolbar');

        tbar.add(2, ' ', me.editAction, me.availsAction, me.dutiesAction, {
            text: _('Printouts'),
            iconCls: 'print-icon',
            menu: { items: [me.printDutiesAction] }
        });

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
        var win = desktop.getWindow('edit-person-win');

        // If the window is already present, destroy and recreate it,
        // to reapply configuration and filters
        if(win) {
            win.destroy();
        }

        var metadata = me.module.config.metadata;
        var size = desktop.getReasonableWindowSize(1000, 480);
        var editors = metadata.editors({
            '*': {
                editor: MP.form.Panel.getDefaultEditorSettingsFunction('100%')
            },
            note: {
                editor: {
                    xtype: 'htmleditor'
                }
            }
        });
        var form = Ext.create('MP.form.Panel', {
            autoScroll: true,
            fieldDefaults: {
                labelWidth: 100,
                margin: '15 10 0 10'
            },
            items: [{
                xtype: 'container',
                layout: 'hbox',
                items: [{
                    xtype: 'container',
                    layout: 'anchor',
                    flex: 1,
                    items: [
                        editors.lastname,
                        editors.firstname,
                        editors.birthdate,
                        editors.password
                    ]
                }, {
                    xtype: 'container',
                    layout: 'anchor',
                    flex: 1,
                    items: [
                        editors.role,
                        editors.phone,
                        editors.mobile,
                        editors.email
                    ]
                }]
            }, editors.note
            ],
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
            id: 'edit-person-win',
            title: _('Edit person'),
            iconCls: 'edit-person-icon',
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


Ext.define('HuRM.module.Persons', {
    extend: 'MP.desktop.Module',

    requires: [
        'MP.grid.Panel'
    ],

    uses: [
        'HuRM.module.Persons.Actions'
    ],

    id: 'persons-win',
    iconCls: 'persons-icon',
    launcherText: _('Persons'),
    launcherTooltip: _('<b>Persons</b><br/>Persons management'),

    config: {
        xtype: 'editable-grid',
        pageSize: 23,
        autoShowAllEditors: false,
        clicksToEdit: 0,
        dataURL: '/data/persons',
        sorters: ['lastname', 'firstname'],
        stripeRows: true
    },

    getConfig: function(callback) {
        var me = this,
            config = me.config;

        if(!config.metadata) {
            MP.data.MetaData.fetch(config.dataURL, me, function(metadata) {
                var overrides = {
                    email: {
                        renderer: function(value) {
                            if(value && value !== '') {
                                value = '<a href="mailto:' + value + '" target="_top">'
                                    + value + '</a>';
                            }
                            return value;
                        }
                    }
                }, fields = metadata.fields(overrides);

                Ext.apply(config, {
                    metadata: metadata,
                    fields: fields,
                    columns: metadata.columns(overrides, false),
                    idProperty: metadata.primary_key,
                    totalProperty: metadata.count_slot,
                    successProperty: metadata.success_slot,
                    rootProperty: metadata.root_slot,
                    plugins: [
                        Ext.create('HuRM.module.Persons.Actions', { module: me }),
                    ]
                });
                callback(config);
                me.app.on('logout', function() { delete config.metadata; }, me, { single: true });
            });
        } else {
            callback(config);
        }
    },

    createOrShowWindow: function() {
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
                var size = desktop.getReasonableWindowSize(800, 640, "SW");

                win = desktop.createWindow({
                    id: me.id,
                    title: me.getLauncherText(),
                    x: size.x,
                    y: size.y,
                    width: size.width,
                    height: size.height,
                    iconCls: me.iconCls,
                    items: [me.config]
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
    },

    showAvailsWindow: function(idperson, fullname) {
        var me = this;

        HuRM.module.Editions.selectEdition(me.app, function(idedition, edition) {
            me.app.getModule('availabilities-win')
                .createOrShowWindow(idedition, edition, idperson, fullname);
        });
    },

    showDutiesWindow: function(idperson, fullname) {
        var me = this;

        HuRM.module.Editions.selectEdition(me.app, function(idedition, edition) {
            me.app.getModule('person-duties-win')
                .createOrShowWindow(idedition, edition, idperson, fullname);
        });
    },

    printDuties: function(idperson) {
        var me = this;

        HuRM.module.Editions.selectEdition(me.app, function(idedition, edition) {
            var url = '/pdf/duties/edition/' + idedition + '/person/' + idperson;
            window.open(url, "_blank");
        });
    }
});

var phoneNumberRE = /^\+?([0-9]+ ?[0-9]+)*$/;
Ext.apply(Ext.form.field.VTypes, {
    phone: function(val, field) {
        return phoneNumberRE.test(val);
    },
    phoneText: _('This field should be a telephone number in the format "+39 123 456 7890"'),
    phoneMask: /[+\d ]/
});
