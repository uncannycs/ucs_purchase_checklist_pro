from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class PurchaseChecklistTemplate(models.Model):
    _name = 'purchase.checklist.template'
    _description = 'Purchase Checklist Template'

    name = fields.Char(string='Template Name', required=True)
    po_state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Apply on PO Status', required=True)
    item_ids = fields.One2many('purchase.checklist.template.item', 'template_id', string='Checklist Items', required=True)

    @api.constrains('po_state')
    def _check_po_state_unique(self):
        for record in self:
            if record.po_state:
                domain = [('po_state', '=', record.po_state), ('id', '!=', record.id)]
                if self.search_count(domain) > 0:
                    raise ValidationError(_("You can only create one checklist template per PO Status!"))

    @api.constrains('name', 'item_ids')
    def _check_item_ids(self):
        for record in self:
            if not record.item_ids:
                raise ValidationError(_("You must add at least one Checklist Item!"))


class PurchaseChecklistTemplateItem(models.Model):
    _name = 'purchase.checklist.template.item'
    _description = 'Purchase Checklist Template Item'

    template_id = fields.Many2one('purchase.checklist.template', string='Template', required=True, ondelete='cascade')
    name = fields.Char(string='Task Name', required=True)
    assignee_id = fields.Many2one('res.users', string='Assignee')
    notes = fields.Text(string='Notes')
    is_mandatory = fields.Boolean(string='Mandatory')
