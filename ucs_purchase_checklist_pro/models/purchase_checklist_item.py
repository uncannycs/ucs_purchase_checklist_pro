from odoo import models, fields, api
from odoo.fields import Datetime

class PurchaseChecklistItem(models.Model):
    _name = 'purchase.checklist.item'
    _description = 'Purchase Checklist Item'

    order_id = fields.Many2one('purchase.order', string='Purchase Order', required=True, ondelete='cascade')
    name = fields.Char(string='Task Name', required=True)
    assignee_id = fields.Many2one('res.users', string='Assignee')
    deadline = fields.Date(string='Deadline')
    notes = fields.Text(string='Notes')
    is_mandatory = fields.Boolean(string='Mandatory')
    is_done = fields.Boolean(string='Done')
    done_date = fields.Datetime(string='Done Date', readonly=True)
    done_by_id = fields.Many2one('res.users', string='Done By', readonly=True)

    @api.onchange('is_done')
    def _onchange_is_done(self):
        for rec in self:
            if rec.is_done:
                rec.done_date = Datetime.now()
                rec.done_by_id = self.env.user.id
            else:
                rec.done_date = False
                rec.done_by_id = False
