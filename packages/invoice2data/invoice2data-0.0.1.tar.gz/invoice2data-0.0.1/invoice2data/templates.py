# -*- coding: utf-8 -*-

# TODO: replace with mighty AI, when ready.

templates = [
                {'keyword': 'QualityHosting',
                 'data': [
                         ('amount', r'Total EUR\s+(\d+,\d+)'),
                         ('amount_untaxed', r'Total EUR\s+(\d+,\d+)'),
                         ('invoice_number', r'Rechnungsnr\.\s+(\d+)'),
                         ('date', r'\s{2,}(\d+\. .+ \d{4})\s{2,}'),
                         ('vat', r'(DE 232 446 240)'),
                        ]
                },
                {'keyword': 'Nodisto',
                 'data': [
                         ('amount', r'Amount.*\n.*\$(\d+\.\d+) USD'),
                         ('invoice_number', r'Invoice #(\d+)'),
                         ('date', r'Invoice Date:\s+(\d+/\d+/\d+)'),
                        ]
                },
                {'keyword': 'Envato',
                 'data': [
                         ('amount', r'Invoice Total: \$(\d+.\d{2})'),
                         ('amount_untaxed', r'Invoice Total: \$(\d+.\d{2})'),
                         ('invoice_number', r'Invoice No. (\d+)'),
                         ('date', r'Order date: (\d+ \w+ \d+)'),
                         ('partner_name', r'(Envato)'),
                        ]
                },
                {'keyword': 'Amazon Web Services',
                 'data': [
                         ('amount', r'TOTAL AMOUNT DUE ON.*\$(\d+\.\d+)'),
                         ('amount_untaxed', r'TOTAL AMOUNT DUE ON.*\$(\d+\.\d+)'),
                         ('invoice_number', r'Invoice Number:\s+(\d+)'),
                         ('date', r'Invoice Date:\s+([a-zA-Z]+ \d+ , \d+)'),
                         ('partner_name', r'(Amazon Web Services, Inc\.)'),
                        ]
                },
                {'keyword': 'Amazon EU',  # TODO : adapt for Odoo import
                                          # TODO fix keyword to match only DE
                 'data': [
                         ('amount', r'EUR (\d+,\d+)\n\nMit dieser Warenlieferung'),
                         ('invoice_number', r'Rechnungsnr\. ([A-Z0-9\-]+)'),
                         ('date', r'Lieferdatum/Rechnungsdatum.*(\d{1,2}\. \w+ \d{4})'),
                        ]
                },
                {'keyword': 'FR58512277450',  # https://www.captaintrain.com/ TODO in progress
                 'data': [
                         ('invoice_number', r'Billet ([A-Z]+)'),
                         ('amount', r'(\d+,\d{2})'),
                         ('amount_untaxed', r'(\d+,\d{2})'),
                         ('date', r'\d+,\d{2}\D+(\d+\s.+\s\d{4})'),
                         ('description', r'Billet [A-Z]+ − ([^\s{5}])'),
                        ]
                },
                {'keyword': 'FR 71 343059564',  # http://www.sfr.fr/ Mobile phone
                 'data': [
                         ('invoice_number', r'N° facture : ([A-Z0-9\-]+)'),
                         ('date', r'Date de facture : (\d{2}/\d{2}/\d{4})'),
                         ('amount', r'(\d+,\d{2}) € TTC'),
                         ('amount_untaxed', r'(\d+,\d{2}) € HT'),
                         ('description', r'(abonnements, forfaits et options du \d{2}/\d{2} au \d{2}/\d{2})'),
                         ('vat', r'(FR 71 343059564)'),
                        ]
                },
                {'keyword': 'FR 71 343 059 564',  # http://www.sfr.fr/ xDSL/Fiber access
                 'data': [
                         ('invoice_number', r'N° de Facture\s:\s(\d+)'),
                         ('date', r'Facture du (\d{2}/\d{2}/\d{4})'),
                         ('amount', r'Total facturé pour l’ensemble de votre compte\s+\d+,\d{2}\s+\d+,\d{2}\s+(\d+,\d{2})'),
                         ('amount_untaxed', r'Total facturé pour l’ensemble de votre compte\s+(\d+,\d{2})'),
                         ('vat', r'(FR 71 343 059 564)'),
                        ]
                },
                {'keyword': '792 377 731',  # http://www.akretion.com/
                 'data': [
                        ('amount', r'Total TTC :\s+(\d+,\d{2})'),
                        ('amount_untaxed', r'Total HT :\s+(\d+,\d{2})'),
                        ('invoice_number', r'Facture (\w+)'),
                        ('date', r'(\d{2}/\d{2}/\d{4})'),
                        ('date_due', r'\d{2}/\d{2}/\d{4}.+(\d{2}/\d{2}/\d{4})'),
                        ('siren', r'(792 377 731)'),
                        ]
                },
                {'keyword': 'FR25499247138',  # Free mobile
                 'data': [
                    ('vat', r'(FR25499247138)'),
                    ('amount_untaxed', r'Total de la facture HT\s+(\d+.\d{2})'),
                    ('amount', r'Somme à payer TTC\*\s+(\d+.\d{2})'),
                    ('date', r'Facture no \d+ du (\d+ .+ \d{4})'),
                    ('invoice_number', r'Facture no (\d+)'),
                    ]
                },
                {'keyword': 'FR 604 219 388 61',  # Free SAS (xDSL/Fiber)
                 'data': [
                    ('vat', r'(FR 604 219 388 61)'),
                    ('amount_untaxed', r'Total facture\s+(\d+.\d{2})'),
                    ('amount', r'Total facture\s+\d+.\d{2}\s+\d+.\d{2}\s+(\d+.\d{2})'),
                    ('date', r'Facture n°\d+ du (\d+ .+ \d{4})'),
                    ('date_due', r'Date limite de paiement le (\d+ .+ \d{4})'),
                    ('invoice_number', r'Facture n°(\d+)'),
                    ]
                },
                {'keyword': 'FR 74 397 480 930',  # http://www.bouyguestelecom.fr/
                'data': [
                    ('vat', r'(FR 74 397 480 930)'),
                    ('amount_untaxed', r'Montant de la facture soumis à TVA\s+(\d+,\d{2})'),
                    ('amount', r'Montant de la facture soumis à TVA\s+\d+,\d{2}\s+(\d+,\d{2})'),
                    ('date', r'Date de facture\s+:\s+(\d{2}/\d{2}/\d{4})'),
                    ('invoice_number', r'N° de facture\s+:\s+(\d+)'),
                    ]
                },
                {'keyword': 'sosh.fr',  # Sosh.fr (tested with an invoice of 2013)
                                        # I can't use the SIREN as keyword because
                                        # Orange SA has too many different invoice layouts
                'data': [
                    ('siren', r'(380\s?129\s?866)'),
                    ('invoice_number', r'facture n°\s*(\d+)'),
                    ('date', r'émise le (\d{2}/\d{2}/\d{4})'),
                    ('amount_untaxed', r'total facture\s+(\d+,\d{2})'),
                    ('amount', r'total facture\s+\d+,\d{2}\s+(\d+,\d{2})'),
                    ]
                },
                {'keyword': 'Orange - service clients La fibre',  # Orange fibre
                'data': [
                    ('siren', r'(380\s?129\s?866)'),
                    ('invoice_number', r'n° de facture\s+:\s+(.+)'),
                    ('date', r'date de facture\s+:\s+(\d{2}/\d{2}/\d{2})'),
                    ('amount_untaxed', r'total auprès d\'Orange\s+(\d+,\d{2})'),
                    ('amount', r'total auprès d\'Orange\s+\d+,\d{2}\s+(\d+,\d{2})'),
                    ]
                },
]
