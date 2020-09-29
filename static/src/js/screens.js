odoo.define('pricelist_product.screens', function (require) {
    "use strict";
    
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var Model = require("web.Model");
    var core = require('web.core');
    var _t = core._t;

    screens.ProductScreenWidget.include({
        click_product: function(product) {
            if(product.to_weight && this.pos.config.iface_electronic_scale){
                this.gui.show_screen('scale',{product: product});
            }else{
                this.pos.get_order().add_product(product);
            }
            
            var order_lines = this.pos.get_order().orderlines.models;
            var line = order_lines[order_lines.length-1]
            new Model('product.template')
                .query(['type_pricelist', 'total_one_'])
                .filter([['id', '=', product.id]])
                .all()
                .then(
                    function(product_tmp) {
                        switch (product_tmp[0].type_pricelist) {
                            case 'amount':
                                new Model('product.template.amount')
                                    .query(['price', 'product_tmpl_id', 'amount_from', 'amount_to'])
                                    .filter([['product_tmpl_id', '=', product.id], ['amount_from', '<=', line.quantity], ['amount_to', '>=', line.quantity]])
                                    .all()
                                    .then(
                                        function(amount_line) {
                                            var price = amount_line.length ? amount_line[0].price : 0
                                            line.set_unit_price(price)
                                        },
                                    );
                                break;
                            case 'one_':
                                var price = product_tmp[0].total_one_      
                                line.set_unit_price(price)
                                break;
                            case 'uom_price':
                                new Model('product.template.uom')
                                    .query(['price'])
                                    .filter([['product_tmpl_id', '=', product.id], ['uom_id', '=', line.product.uom_id[0]]])
                                    .all()
                                    .then(
                                        function(uom_line) {
                                            var price = uom_line.length ? uom_line[0].price : 0
                                            line.set_unit_price(price)
                                        },
                                    );
                                break;
                        }
                    },
                    function(err, event){
                        event.preventDefault();
                        console.error(err);
                    }
                );
        },
    });

    screens.OrderWidget.include({
        set_value: function(val) {
            var order = this.pos.get_order();
            if (order.get_selected_orderline()) {
                var line = order.get_selected_orderline()
                var mode = this.numpad_state.get('mode');
                if( mode === 'quantity'){
                    order.get_selected_orderline().set_quantity(val);
                    
                    if(val > 0){
                        new Model('product.template')
                            .query(['type_pricelist', 'total_one_'])
                            .filter([['id', '=', line.product.id]])
                            .all()
                            .then(
                                function(product_tmp) {
                                    if (product_tmp[0].type_pricelist == 'amount') {
                                        new Model('product.template.amount')
                                            .query(['price', 'product_tmpl_id', 'amount_from', 'amount_to'])
                                            .filter([['product_tmpl_id', '=', line.product.id], ['amount_from', '<=', val], ['amount_to', '>=', val]])
                                            .all()
                                            .then(
                                                function(amount_line) {
                                                    var price = amount_line.length ? amount_line[0].price : 0
                                                    line.set_unit_price(price)
                                                },
                                            );
                                    }
                                },
                                function(err, event){
                                    event.preventDefault();
                                    console.error(err);
                                }
                            );
                    }
                }else if( mode === 'discount'){
                    order.get_selected_orderline().set_discount(val);
                }else if( mode === 'price'){
                    order.get_selected_orderline().set_unit_price(val);
                }
            }
        },
    });

    screens.button_choice_uom.include({
        button_click: function () {
            var order = this.pos.get_order()
            if (order) {
                var selected_orderline = order.selected_orderline;
                if (selected_orderline) {
                    var product = selected_orderline.product;
                    var uom_items = this.pos.uoms_prices_by_product_tmpl_id[product.product_tmpl_id]
                    if (!uom_items) {
                        return this.pos.gui.show_popup('error', {
                            title: '!!! Warning !!!',
                            body: product['display_name'] + ' have ' + product['uom_id'][1] + ' only.'
                        });
                    }
                    var list = [];
                    for (var i = 0; i < uom_items.length; i++) {
                        var item = uom_items[i];
                        list.push({
                            'label': item.uom_id[1],
                            'item': item,
                        });
                    }
                    if (list.length) {
                        return this.gui.show_popup('selection', {
                            title: _t('Select Unit of measure'),
                            list: list,
                            confirm: function (item) {
                                new Model('product.template')
                                    .query(['type_pricelist', 'total_one_'])
                                    .filter([['id', '=', selected_orderline.product.id]])
                                    .all()
                                    .then(
                                        function(product_tmp) {
                                            if (product_tmp[0].type_pricelist == 'uom_price') {
                                                new Model('product.template.amount')
                                                    .query(['price', 'product_tmpl_id', 'amount_from', 'amount_to'])
                                                    .filter([['product_tmpl_id', '=', selected_orderline.product.id], ['uom_id', '=', item['uom_id'][0]]])
                                                    .all()
                                                    .then(
                                                        function(uom_line) {
                                                            var price = uom_line.length ? uom_line[0].price : 0
                                                            selected_orderline.set_unit_price(price)
                                                        },
                                                    );
                                            }
                                        },
                                        function(err, event){
                                            event.preventDefault();
                                            console.error(err);
                                        }
                                    );
                                selected_orderline.uom_id = item['uom_id'][0];
                                selected_orderline.trigger('change', selected_orderline);
                                selected_orderline.trigger('update:OrderLine');
                            }
                        });
                    } else {
                        return this.pos.gui.show_popup('error', {
                            title: '!!! Warning !!!',
                            body: product['display_name'] + ' have ' + product['uom_id'][1] + ' only.'
                        });
                    }
                } else {
                    return this.pos.gui.show_popup('error', {
                        title: '!!! Warning !!!',
                        body: 'Please select line want change unit of measure'
                    });
                }
            } else {
                return this.pos.gui.show_popup('error', {
                    title: '!!! Warning !!!',
                    body: 'Order null'
                });
            }

        }
    })


});