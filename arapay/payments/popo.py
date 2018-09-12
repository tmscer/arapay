# Plain Old Python Objects


class InvoiceStats:

    def __init__(self, invoice_id, total_users):
        self.invoice_id = invoice_id
        self.total_users = total_users
        self.n_paid = 0
        self.n_unpaid = 0
        self.n_overpaid = 0
        self.amount_cents_paid = 0
        self.amount_cents_owed = 0

    @property
    def paid_percentage(self):
        if self.amount_cents_owed == 0:
            return 0
        else:
            return 100 * self.amount_cents_paid / self.amount_cents_owed

    def __repr__(self):
        return "InvoiceStats(invoice_id={}, total_users={}, n_paid={}, n_unpaid={}, n_overpaid={}, " \
               "amount_cents_paid={}, amount_cents_owed={})" \
            .format(self.invoice_id, self.total_users, self.n_paid, self.n_unpaid, self.n_overpaid,
                    self.amount_cents_paid, self.amount_cents_owed)

    def as_dict(self):
        self.__dict__.update(paid_percentage=self.paid_percentage)
        return self.__dict__
