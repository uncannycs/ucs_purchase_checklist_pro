from odoo import models, fields, api
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    checklist_item_ids = fields.One2many('purchase.checklist.item', 'order_id', string='Checklist Items')
    checklist_progress = fields.Float(string='Checklist Progress', compute='_compute_checklist_progress', store=True)

    @api.depends('checklist_item_ids.is_done')
    def _compute_checklist_progress(self):
        for po in self:
            total_items = len(po.checklist_item_ids)
            done_items = len(po.checklist_item_ids.filtered(lambda i: i.is_done))
            po.checklist_progress = (done_items / total_items * 100.0) if total_items > 0 else 0.0

    def _check_mandatory_checklist(self):
        for po in self:
            incomplete = po.checklist_item_ids.filtered(lambda i: i.is_mandatory and not i.is_done)
            if incomplete:
                task_names = ", ".join(incomplete.mapped('name'))
                raise UserError(f"You cannot proceed. The following mandatory tasks are incomplete: {task_names}")

    def button_confirm(self):
        self._check_mandatory_checklist()
        return super(PurchaseOrder, self).button_confirm()

    def button_approve(self):
        self._check_mandatory_checklist()
        return super(PurchaseOrder, self).button_approve()

    def button_done(self):
        self._check_mandatory_checklist()
        return super(PurchaseOrder, self).button_done()

    def action_create_invoice(self):
        self._check_mandatory_checklist()
        return super(PurchaseOrder, self).action_create_invoice()

    def write(self, vals):
        if 'state' in vals and vals['state'] != 'cancel':
            for po in self:
                incomplete_mandatory = po.checklist_item_ids.filtered(lambda i: i.is_mandatory and not i.is_done)
                if incomplete_mandatory:
                    raise UserError("You cannot change the state of this Purchase Order because there are incomplete mandatory checklist tasks.")
                    
        res = super(PurchaseOrder, self).write(vals)
        if 'state' in vals:
            for po in self:
                po._apply_checklist_template(vals['state'])
        return res

    @api.model_create_multi
    def create(self, vals_list):
        records = super(PurchaseOrder, self).create(vals_list)
        for record in records:
            record._apply_checklist_template(record.state)
        return records

    def _apply_checklist_template(self, state):
        templates = self.env['purchase.checklist.template'].search([('po_state', '=', state)])
        for template in templates:
            existing_items = self.checklist_item_ids.mapped('name')
            for item in template.item_ids:
                if item.name not in existing_items:
                    self.env['purchase.checklist.item'].create({
                        'order_id': self.id,
                        'name': item.name,
                        'assignee_id': item.assignee_id.id,
                        'notes': item.notes,
                        'is_mandatory': item.is_mandatory,
                    })

    def action_apply_status_checklist(self):
        for po in self:
            po._apply_checklist_template(po.state)

    def action_clear_checklist(self):
        for po in self:
            po.checklist_item_ids.unlink()
