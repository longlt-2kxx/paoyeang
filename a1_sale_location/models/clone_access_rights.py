from odoo import models, fields, api
from odoo.exceptions import UserError


class CloneAccessWizard(models.TransientModel):
    _name = 'clone.access.wizard'
    _description = 'Wizard to clone Access Rights between groups'

    group_from_id = fields.Many2one('res.groups', string="Source Group", required=True)
    group_to_id = fields.Many2one('res.groups', string="Target Group", required=True)

    def action_clone_access(self):
        if self.group_from_id.id == self.group_to_id.id:
            raise UserError("Source and target groups must be different.")

        access_model = self.env['ir.model.access']
        from_access = access_model.search([('group_id', '=', self.group_from_id.id)])

        created = 0
        skipped = 0

        for access in from_access:
            exists = access_model.search([
                ('group_id', '=', self.group_to_id.id),
                ('model_id', '=', access.model_id.id)
            ], limit=1)

            if not exists:
                access_model.create({
                    'name': f"access_{access.model_id.model.replace('.', '_')}_{self.group_to_id.id}",
                    'model_id': access.model_id.id,
                    'group_id': self.group_to_id.id,
                    'perm_read': access.perm_read,
                    'perm_write': access.perm_write,
                    'perm_create': access.perm_create,
                    'perm_unlink': access.perm_unlink,
                })
                created += 1
            else:
                skipped += 1

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Access Rights Cloned',
                'message': f"{created} created, {skipped} skipped",
                'sticky': False,
            }
        }
