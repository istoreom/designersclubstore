# -*- coding: utf-8 -*-
import itertools
import json

from odoo import models, fields
from odoo.http import request


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def get_variant_count(self):
        for rec in self:
            valid_combination_list = []
            attribute_ids = []
            unavailable_variant_view_type = []
            attribute_display_types = {}

            all_empty = False
            try:
                iterable = rec.with_context(special_call=True)._get_possible_combinations()
                first = next(iterable)
            except StopIteration:
                all_empty = True
            if all_empty:
                for v in rec._get_possible_combinations():
                    val = []
                    for value in v:
                        val.append(value.id)
                        if value.attribute_id.id not in attribute_ids:
                            attribute_display_types.update({value.attribute_id.id: value.attribute_id.display_type})
                            attribute_ids.append(value.attribute_id.id)
                            unavailable_variant_view_type.append(value.attribute_id.unavailable_value_view_type)

            else:
                for v in rec.with_context(special_call=True)._get_possible_combinations():
                    val = []
                    for value in v:
                        val.append(value.id)
                        if value.attribute_id.id not in attribute_ids:
                            attribute_display_types.update({value.attribute_id.id: value.attribute_id.display_type})
                            attribute_ids.append(value.attribute_id.id)
                            unavailable_variant_view_type.append(value.attribute_id.unavailable_value_view_type)

                    valid_combination_list.append(tuple(val))
            valid_comb = set(valid_combination_list)
            value_count_per_attr = []
            attribute_line_ids = self.attribute_line_ids
            if attribute_line_ids:
                for line in attribute_line_ids:
                    value_count_per_attr.append(len(line.value_ids))

            j = 0
            available_variant_values_ids = {}
            all_val = []
            for item in list(valid_comb):
                all_val.extend(list(item))
                available_variant_values_ids[j] = (list(item))
                j += 1
            all_val = list(set(all_val))
            variant_val_child_dict = {}
            for i in range(len(all_val)):
                all_child_items = []
                for item in list(valid_comb):
                    items = list(item)
                    try:
                        offset = items.index(all_val[i])
                    except ValueError:
                        offset = -1
                    if offset == -1:
                        continue
                    child_item = []
                    for j in range(offset, len(items)):
                        child_item.append(items[j])
                    all_child_items.extend(child_item)
                child_list = list(set(all_child_items))
                variant_val_child_dict[all_val[i]] = child_list
            unavailable_variant_dict = {
                "attribute_ids": attribute_ids,
                "attribute_display_types": attribute_display_types,
                "unavailable_variant_view_type": unavailable_variant_view_type,
                "value_to_show": variant_val_child_dict,
                "value_to_show_tuple": list(valid_comb),
                "value_count_per_attr": value_count_per_attr
            }
            print('-------unavailable_variant_dict00000---', unavailable_variant_dict)
            return json.dumps(unavailable_variant_dict)

    def _get_first_possible_combination(self, parent_combination=None, necessary_values=None):
        """See `_get_possible_combinations` (one iteration).

        This method return the same result (empty recordset) if no
        combination is possible at all which would be considered a negative
        result, or if there are no attribute lines on the template in which
        case the "empty combination" is actually a possible combination.
        Therefore the result of this method when empty should be tested
        with `_is_combination_possible` if it's important to know if the
        resulting empty combination is actually possible or not.
        """
        com = next(self._get_possible_combinations(parent_combination, necessary_values),
                   self.env['product.template.attribute.value'])
        no_variant_attr_val = self.env['product.template.attribute.value']
        for ptav in com:
            if ptav.attribute_id.create_variant == "no_variant":
                no_variant_attr_val += ptav

        for combination in self._get_possible_combinations(parent_combination, necessary_values):
            org_combination = combination
            combination -= no_variant_attr_val
            # variant_id = self.product_variant_ids.filtered(
            #     lambda variant: variant.product_template_attribute_value_ids == combination)
            variant_id = self._get_variant_for_combination(combination)
            if variant_id:
                if variant_id.type == 'product' and self._context.get("special_call"):
                    free_qty = variant_id.sudo().with_context(
                        warehouse=request.website._get_warehouse_available()).free_qty
                    print ('=============free_qty============',free_qty)
                    if (free_qty <= 0):
                        pass
                    else:
                        print ('===================', org_combination)
                        return org_combination
                else:
                    print ('2========================', org_combination)
                    return org_combination

    def _is_combination_possible(self, combination, parent_combination=None, ignore_no_variant=False):
        result = super(ProductTemplate, self)._is_combination_possible(combination, parent_combination,
                                                                       ignore_no_variant)
        if result and self._context.get("special_call"):
            no_variant_attr_val = self.env['product.template.attribute.value']
            for ptav in combination:
                if ptav.attribute_id.create_variant == "no_variant":
                    no_variant_attr_val += ptav
            combination -= no_variant_attr_val
            # variant_id = self.product_variant_ids.filtered(
            #     lambda variant: variant.product_template_attribute_value_ids == combination)
            variant_id = self._get_variant_for_combination(combination)
            if variant_id and self._context.get("special_call"):
                free_qty = variant_id.sudo().with_context(
                    warehouse=request.website._get_warehouse_available()).free_qty
                if variant_id.type == 'product' and (free_qty <= 0):
                    return False
                else:
                    return True
        return result


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    unavailable_value_view_type = fields.Selection([('none', 'None'), ('cancel_out', 'Cancel Out'), ('hide', 'Hide')],
                                                   default='none', string='Unavailable Variant View Type')
