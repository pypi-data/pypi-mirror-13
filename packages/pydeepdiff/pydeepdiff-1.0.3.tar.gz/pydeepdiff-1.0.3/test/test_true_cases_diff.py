"""
    Test of get_diff with true cases
"""

from pydeepdiff.diff import get_diff


def test_case_one():
    diff = []

    obj_a = {
        'tags': ['742'],
        'id': 'la francaise',
        'janus': {
            'dedupkey': 'b90e6e2ffca41f216dfd9566a93aa2ff',
            'tags': ['742'],
            'status': None,
            'doc_version': '742',
            'request': None
        },
        'tech': {
            'api_response': {
                'status_code': 200
            },
            'delphes': {
                'ok': 'true',
                'dateADNc': '2016-01-08 23:09:48-00:00',
                'schemaADNc': 'adncprod',
                'version': '200',
                'date': '2016-01-12 01:14:43-00:00',
                'versionDelphes': '6.3.2',
                'commentaire': '',
                'versionADNc': '742'
            }
        },
        'creation_date': '2016-01-12T02:04:05.665307+00:00',
        'reponse': {
            'ambiguite': True,
            'typologie': 'QUI',
            'business_key': '4542836c6a2b086f4c50b9187f6788b2',
            'mots_signifiants': ['la', 'francaise'],
            'blocs_reponses': [{
                'activites_affichage_immediat': [{
                    'scoring_qui_quoi': 'INCONNU',
                    'identifiant': 'ac0',
                    'machine_learning_etat': 'valide',
                    'ordre': 1,
                    'libelle': 'la francaise',
                    'machine_learning_source': 'RR',
                    'type_bloc_activite': 'IMMEDIAT',
                    'expressions': [{
                        'formes_brutes': ['la', 'francaise'],
                        'type_crc': '',
                        'code': 'la francaise',
                        'libelle': 'la francaise',
                        'type_expression': 'ALPHA',
                        'chaine_saisie': 'la francaise'
                    }]
                }, {
                    'scoring_qui_quoi': 'INCONNU',
                    'identifiant': 'ac0',
                    'machine_learning_etat': 'valide',
                    'ordre': 1,
                    'rubriques': [],
                    'machine_learning_source': 'RR',
                    'type_bloc_activite': 'IMMEDIAT',
                    'libelle': 'la francaise',
                    'expressions': [{
                        'formes_brutes': ['la', 'francaise'],
                        'type_crc': '',
                        'code': 'la francaise',
                        'libelle': 'la francaise',
                        'type_expression': 'ALPHA',
                        'chaine_saisie': 'la francaise'
                    }]
                }],
                'type_interpretation': 'QUI',
                'identifiant_de_bloc': 'ac0'
            }, {
                'activites_affichage_immediat': [{
                    'scoring_qui_quoi': 'MOYEN',
                    'ordre': 1,
                    'forme_canonique': 'français',
                    'correction': False,
                    'expressions': [{
                        'formes_brutes': ['francaise'],
                        'type_expression': 'RESTRICTION_FAIBLE',
                        'code': 'ObjetCrc_français_24307-319900-238600-319170-319780-319130-372900_Principale',
                        'formes_normales': ['COURS :: FRANCAIS'],
                        'rubriques': [{
                            'libelle_rubrique': '',
                            'code_an8': '319900',
                            'code_an9': '64055100'
                        }, {
                            'libelle_rubrique': '',
                            'code_an8': '319170',
                            'code_an9': '64051300'
                        }, {
                            'libelle_rubrique': '',
                            'code_an8': '372900',
                            'code_an9': '64101300'
                        }, {
                            'libelle_rubrique': '',
                            'code_an8': '238600',
                            'code_an9': '64050500'
                        }, {
                            'libelle_rubrique': '',
                            'code_an8': '319780',
                            'code_an9': '64053000'
                        }, {
                            'libelle_rubrique': '',
                            'code_an8': '319130',
                            'code_an9': '64056100'
                        }],
                        'rubriques_fines': [{
                            'libelle_rubrique': '',
                            'code_an8': '000598',
                            'code_an9': '00000598'
                        }],
                        'type_crc': 'C',
                        'libelle': 'français',
                        'chaine_saisie': 'francaise'
                    }],
                    'suggestion_editoriale': False,
                    'rubriques': [{
                        'libelle_rubrique': 'enseignement supérieur public',
                        'code_an8': '319900',
                        'code_an9': '64055100'
                    }, {
                        'libelle_rubrique': 'cours de langues',
                        'code_an8': '319170',
                        'code_an9': '64051300'
                    }, {
                        'libelle_rubrique': 'formation continue',
                        'code_an8': '372900',
                        'code_an9': '64101300'
                    }, {
                        'libelle_rubrique': 'soutien scolaire, cours particuliers',
                        'code_an8': '238600',
                        'code_an9': '64050500'
                    }, {
                        'libelle_rubrique': 'enseignement supérieur privé',
                        'code_an8': '319780',
                        'code_an9': '64053000'
                    }, {
                        'libelle_rubrique': 'cours par correspondance, enseignement à distance',
                        'code_an8': '319130',
                        'code_an9': '64056100'
                    }],
                    'identifications_bloc_reponse_activite': [{
                        'identifiant_bloc_reponse': '37027',
                        'origine_bloc_reponse': 'MANUEL'
                    }],
                    'machine_learning_etat': 'valide',
                    'identifiant': 'ac1_2',
                    'faible_pertinence': True,
                    'libelle': 'COURS DE FRANÇAIS',
                    'machine_learning_source': 'rr',
                    'type_bloc_activite': 'IMMEDIAT'
                }],
                'type_interpretation': 'QUOI',
                'identifiant_de_bloc': 'ac1'
            }]
        },
        'requete': {
            'tx_fragile': '0.15008058',
            'frequence': 36,
            'libelle': 'la francaise'
        }
    }

    obj_b = {
        'tags': ['743'],
        'id': 'la francaise',
        'tech': {
            'api_response': {
                'status_code': 200
            },
            'delphes': {
                'ok': 'true',
                'dateADNc': '2016-01-12 01:07:42-00:00',
                'schemaADNc': 'adncprod',
                'version': '27',
                'date': '2016-01-13 01:15:24-00:00',
                'versionDelphes': '6.3.2',
                'commentaire': '',
                'versionADNc': '743'
            }
        },
        'reponse': {
            'ambiguite': True,
            'typologie': 'QUI',
            'blocs_reponses': [{
                'activites_affichage_immediat': [{
                    'ordre': 1,
                    'identifiant': 'ac0',
                    'machine_learning_etat': 'valide',
                    'type_bloc_activite': 'IMMEDIAT',
                    'scoring_qui_quoi': 'INCONNU',
                    'machine_learning_source': 'RR',
                    'expressions': [{
                        'formes_brutes': ['la', 'francaise'],
                        'type_expression': 'ALPHA',
                        'code': 'la francaise',
                        'chaine_saisie': 'la francaise',
                        'type_crc': '',
                        'libelle': 'la francaise'
                    }],
                    'libelle': 'la francaise'
                }, {
                    'ordre': 1,
                    'identifiant': 'ac0',
                    'machine_learning_etat': 'valide',
                    'type_bloc_activite': 'IMMEDIAT',
                    'scoring_qui_quoi': 'INCONNU',
                    'libelle': 'la francaise',
                    'machine_learning_source': 'RR',
                    'expressions': [{
                        'formes_brutes': ['la', 'francaise'],
                        'type_expression': 'ALPHA',
                        'code': 'la francaise',
                        'chaine_saisie': 'la francaise',
                        'type_crc': '',
                        'libelle': 'la francaise'
                    }],
                    'rubriques': []
                }],
                'type_interpretation': 'QUI',
                'identifiant_de_bloc': 'ac0'
            }, {
                'activites_affichage_immediat': [{
                    'scoring_qui_quoi': 'MOYEN',
                    'identifications_bloc_reponse_activite': [{
                        'identifiant_bloc_reponse': '37027',
                        'origine_bloc_reponse': 'MANUEL'
                    }],
                    'forme_canonique': 'français',
                    'correction': False,
                    'expressions': [{
                        'formes_brutes': ['francaise'],
                        'type_expression': 'RESTRICTION_FAIBLE',
                        'code': 'ObjetCrc_français_24307-319900-238600-319170-319780-319130-372900_Principale',
                        'formes_normales': ['COURS :: FRANCAIS'],
                        'rubriques': [{
                            'libelle_rubrique': '',
                            'code_an8': '319900',
                            'code_an9': '64055100'
                        }, {
                            'libelle_rubrique': '',
                            'code_an8': '319170',
                            'code_an9': '64051300'
                        }, {
                            'libelle_rubrique': '',
                            'code_an8': '372900',
                            'code_an9': '64101300'
                        }, {
                            'libelle_rubrique': '',
                            'code_an8': '238600',
                            'code_an9': '64050500'
                        }, {
                            'libelle_rubrique': '',
                            'code_an8': '319780',
                            'code_an9': '64053000'
                        }, {
                            'libelle_rubrique': '',
                            'code_an8': '319130',
                            'code_an9': '64056100'
                        }],
                        'rubriques_fines': [{
                            'libelle_rubrique': '',
                            'code_an8': '000598',
                            'code_an9': '00000598'
                        }],
                        'type_crc': 'C',
                        'libelle': 'français',
                        'chaine_saisie': 'francaise'
                    }],
                    'suggestion_editoriale': False,
                    'libelle': 'COURS DE FRANÇAIS',
                    'identifiant': 'ac1_2',
                    'ordre': 1,
                    'machine_learning_etat': 'valide',
                    'faible_pertinence': True,
                    'rubriques': [{
                        'libelle_rubrique': 'enseignement supérieur public',
                        'code_an8': '319900',
                        'code_an9': '64055100'
                    }, {
                        'libelle_rubrique': 'cours de langues',
                        'code_an8': '319170',
                        'code_an9': '64051300'
                    }, {
                        'libelle_rubrique': 'formation continue',
                        'code_an8': '372900',
                        'code_an9': '64101300'
                    }, {
                        'libelle_rubrique': 'soutien scolaire, cours particuliers',
                        'code_an8': '238600',
                        'code_an9': '64050500'
                    }, {
                        'libelle_rubrique': 'enseignement supérieur privé',
                        'code_an8': '319780',
                        'code_an9': '64053000'
                    }, {
                        'libelle_rubrique': 'cours par correspondance, enseignement à distance',
                        'code_an8': '319130',
                        'code_an9': '64056100'
                    }],
                    'machine_learning_source': 'rr',
                    'type_bloc_activite': 'IMMEDIAT'
                }],
                'type_interpretation': 'QUOI',
                'identifiant_de_bloc': 'ac1'
            }],
            'mots_signifiants': ['la', 'francaise'],
            'business_key': '4542836c6a2b086f4c50b9187f6788b2'
        },
        'creation_date': '2016-01-13T02:11:53.402000+00:00',
        'requete': {
            'tx_fragile': '0.15008058',
            'frequence': 36,
            'libelle': 'la francaise'
        },
        'janus': {
            'dedupkey': 'b90e6e2ffca41f216dfd9566a93aa2ff',
            'tags': ['743'],
            'status': None,
            'doc_version': '743',
            'request': {
                'comments': [],
                'tags': [],
                'user': None,
                'raw_query': 'la francaise'
            }
        }
    }

    mapping = [{'path': '', 'id': 'id'}, {'path': 'reponse.blocs_reponses', 'id': 'identifiant_de_bloc'}, {'path': 'reponse.blocs_reponses.activites_affichage_immediat', 'id': 'identifiant'}, {'path': 'reponse.blocs_reponses.activites_affichage_immediat.rubriques', 'id': 'code_an8'}]
    ignored_fields = ['creation_date', 'auto_state', 'user', 'status', 'comments', 'requete', 'tags', 'janus', 'tech']

    diff = get_diff(obj_a, obj_b, [], mapping, ignored_fields)

    expected_diff = [{'kind': 'M', 'path_to_object': 'reponse.blocs_reponses.[0].activites_affichage_immediat', 'filter': 'reponse.blocs_reponses.activites_affichage_immediat'}, {'kind': 'D', 'path_to_object': 'reponse.blocs_reponses.[0].activites_affichage_immediat.[0].rubriques', 'filter': 'reponse.blocs_reponses.activites_affichage_immediat.rubriques'}, {'kind': 'M', 'path_to_object': 'reponse.blocs_reponses.[0].activites_affichage_immediat', 'filter': 'reponse.blocs_reponses.activites_affichage_immediat'}, {'kind': 'N', 'path_to_object': 'reponse.blocs_reponses.[0].activites_affichage_immediat.[1].rubriques', 'filter': 'reponse.blocs_reponses.activites_affichage_immediat.rubriques'}, {'rhs_idx': 1, 'kind': 'N', 'path_to_object': 'reponse.blocs_reponses.[0].activites_affichage_immediat', 'rhs': {'machine_learning_etat': 'valide', 'scoring_qui_quoi': 'INCONNU', 'expressions': [{'libelle': 'la francaise', 'type_expression': 'ALPHA', 'chaine_saisie': 'la francaise', 'formes_brutes': ['la', 'francaise'], 'type_crc': '', 'code': 'la francaise'}], 'libelle': 'la francaise', 'machine_learning_source': 'RR', 'type_bloc_activite': 'IMMEDIAT', 'rubriques': [], 'ordre': 1, 'identifiant': 'ac0'}, 'filter': 'reponse.blocs_reponses.activites_affichage_immediat'}]

    assert diff == expected_diff


def test_case_two():

    obj_a = {
            'reponse': {
                'mots_signifiants': ['poele', 'a', 'pellet'],
                'business_key': '3abc507ff306e857b9d16ffa01f3bbe6',
                'typologie': 'QUOI',
                'ambiguite': True,
                'blocs_reponses': [{
                    'type_interpretation': 'QUOI',
                    'identifiant_de_bloc': 'ac2',
                    'activites_affichage_immediat': [{
                        'suggestion_editoriale': False,
                        'machine_learning_source': 'rr',
                        'type_bloc_activite': 'IMMEDIAT',
                        'libelle': 'POÊLES À GRANULÉS',
                        'forme_canonique': 'poêles à pellets',
                        'scoring_qui_quoi': 'FORT',
                        'expressions': [{
                            'type_crc': 'C',
                            'code': 'ObjetCrc_poêles à pellets_7548-632350-167560-172000_Principale',
                            'type_expression': 'RESTRICTION_FAIBLE',
                            'chaine_saisie': 'poele a pellet',
                            'libelle': 'poêle à granulés',
                            'rubriques': [{
                                'libelle_rubrique': '',
                                'code_an9': '30202300',
                                'code_an8': '167560'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '24301500',
                                'code_an8': '632350'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '30202500',
                                'code_an8': '172000'
                            }],
                            'formes_brutes': ['poele', 'a', 'pellet'],
                            'formes_normales': ['POELE :: GRANULE'],
                            'rubriques_fines': [{
                                'libelle_rubrique': '',
                                'code_an9': '00850083',
                                'code_an8': '850083'
                            }]
                        }],
                        'identifications_bloc_reponse_activite': [{
                            'origine_bloc_reponse': 'MANUEL',
                            'identifiant_bloc_reponse': '85417'
                        }],
                        'machine_learning_etat': 'valide',
                        'ordre': 1,
                        'correction': False,
                        'identifiant': 'ac2_2',
                        'rubriques': [{
                            'libelle_rubrique': 'vente, installation de chauffage',
                            'code_an9': '30202300',
                            'code_an8': '167560'
                        }, {
                            'libelle_rubrique': 'poêles, poêles à bois',
                            'code_an9': '24301500',
                            'code_an8': '632350'
                        }, {
                            'libelle_rubrique': 'cheminées, accessoires',
                            'code_an9': '30202500',
                            'code_an8': '172000'
                        }]
                    }]
                }]
            },
            'tags': ['744'],
            'id': 'poele a pellet',
            'requete': {
                'tx_fragile': '0.16654322',
                'libelle': 'poele a pellet',
                'frequence': 51
            },
            'creation_date': '2016-01-14T02:34:47.196955+00:00',
            'janus': {
                'request': {
                    'comments': [],
                    'tags': [],
                    'raw_query': 'poele a pellet',
                    'user': None
                },
                'status': None,
                'doc_version': '744',
                'dedupkey': '151c9ec75c2eee2c25b06b54adf26a68',
                'tags': ['744']
            },
            'tech': {
                'api_response': {
                    'status_code': 200
                },
                'delphes': {
                    'versionDelphes': '6.3.2',
                    'versionADNc': '744',
                    'dateADNc': '2016-01-12 23:28:03-00:00',
                    'version': '202',
                    'ok': 'true',
                    'schemaADNc': 'adncprod',
                    'date': '2016-01-14 01:15:00-00:00',
                    'commentaire': ''
                }
            }
        }

    obj_b = {
            'reponse': {
                'mots_signifiants': ['poele', 'a', 'pellet'],
                'business_key': '57ef8d5c49af3b6ff3df071b421ea3c8',
                'typologie': 'QUOI',
                'ambiguite': False,
                'blocs_reponses': [{
                    'type_interpretation': 'QUOI',
                    'identifiant_de_bloc': 'ac3',
                    'activites_affichage_immediat': [{
                        'suggestion_editoriale': False,
                        'correction': False,
                        'type_bloc_activite': 'IMMEDIAT',
                        'libelle': 'POÊLES, POÊLES À BOIS',
                        'forme_canonique': 'poêle a pellet',
                        'scoring_qui_quoi': 'FORT',
                        'expressions': [{
                            'type_crc': '',
                            'type_expression': 'MOT_RESIDUEL',
                            'chaine_saisie': 'a pellet',
                            'libelle': 'a pellet',
                            'code': 'a pellet',
                            'formes_brutes': ['a', 'pellet'],
                            'rubriques_fines': []
                        }, {
                            'code': 'ObjetCrc_poêle_56509-172000_Principale',
                            'type_expression': 'RESTRICTION_FAIBLE',
                            'chaine_saisie': 'poele',
                            'formes_brutes': ['poele'],
                            'libelle': 'poêle',
                            'rubriques': [{
                                'libelle_rubrique': '',
                                'code_an9': '30202500',
                                'code_an8': '172000'
                            }],
                            'type_crc': 'C',
                            'formes_normales': ['POELE'],
                            'rubriques_fines': [{
                                'libelle_rubrique': '',
                                'code_an9': '00850083',
                                'code_an8': '850083'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '24301500',
                                'code_an8': '632350'
                            }]
                        }],
                        'identifications_bloc_reponse_activite': [{
                            'origine_bloc_reponse': 'MANUEL',
                            'identifiant_bloc_reponse': '89351'
                        }],
                        'machine_learning_etat': 'valide',
                        'ordre': 1,
                        'machine_learning_source': 'rr',
                        'identifiant': 'ac3_2',
                        'rubriques': [{
                            'libelle_rubrique': 'cheminées, accessoires',
                            'code_an9': '30202500',
                            'code_an8': '172000'
                        }]
                    }]
                }, {
                    'type_interpretation': 'QUI',
                    'identifiant_de_bloc': 'ac4',
                    'activites_affichage_immediat': [{
                        'scoring_qui_quoi': 'NUL',
                        'expressions': [{
                            'type_crc': '',
                            'type_expression': 'MOT_RESIDUEL',
                            'chaine_saisie': 'poele a',
                            'libelle': 'poele a',
                            'code': 'poele a',
                            'formes_brutes': ['poele', 'a'],
                            'rubriques_fines': []
                        }, {
                            'code': 'Marque_Pellet_Principale',
                            'type_expression': 'DENOMINATION',
                            'chaine_saisie': 'pellet',
                            'formes_brutes': ['pellet'],
                            'libelle': 'pellet',
                            'rubriques': [{
                                'libelle_rubrique': '',
                                'code_an9': '30208500',
                                'code_an8': '709490'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '34106000',
                                'code_an8': '821190'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '79053800',
                                'code_an8': '900370'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '34108700',
                                'code_an8': '821220'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '00025620',
                                'code_an8': '025620'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '34200900',
                                'code_an8': '169870'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '34108300',
                                'code_an8': '820400'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '30204700',
                                'code_an8': '304040'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '30204500',
                                'code_an8': '304210'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '00850161',
                                'code_an8': '850161'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '00850040',
                                'code_an8': '850040'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '24209600',
                                'code_an8': '586350'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '00850157',
                                'code_an8': '850157'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '34105700',
                                'code_an8': '821200'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '34101100',
                                'code_an8': '242680'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '24252700',
                                'code_an8': '296320'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '00000690',
                                'code_an8': '000690'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '34105900',
                                'code_an8': '821180'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '79216400',
                                'code_an8': '905560'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '24252900',
                                'code_an8': '296500'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '34107200',
                                'code_an8': '757650'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '30209800',
                                'code_an8': '711740'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '34050600',
                                'code_an8': '097300'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '00025610',
                                'code_an8': '025610'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '30205800',
                                'code_an8': '253910'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '34354200',
                                'code_an8': '749350'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '00850270',
                                'code_an8': '850270'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '34201500',
                                'code_an8': '170300'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '00850304',
                                'code_an8': '850304'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '00850305',
                                'code_an8': '850305'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '00850306',
                                'code_an8': '850306'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '00850307',
                                'code_an8': '850307'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '72150200',
                                'code_an8': '076800'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '00850303',
                                'code_an8': '850303'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '24251100',
                                'code_an8': '121200'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '34150100',
                                'code_an8': '094250'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '34104600',
                                'code_an8': '820320'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '24251700',
                                'code_an8': '213600'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '34108800',
                                'code_an8': '820660'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '34100400',
                                'code_an8': '242500'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '00025580',
                                'code_an8': '025580'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '34108400',
                                'code_an8': '820510'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '10103300',
                                'code_an8': '552950'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '00000700',
                                'code_an8': '000700'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '79053900',
                                'code_an8': '900380'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '34108600',
                                'code_an8': '820650'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '00025600',
                                'code_an8': '025600'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '20050600',
                                'code_an8': '254100'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '34200600',
                                'code_an8': '098600'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '72259500',
                                'code_an8': '271800'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '00850980',
                                'code_an8': '850980'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '00850145',
                                'code_an8': '850145'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '30204600',
                                'code_an8': '304030'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '22101900',
                                'code_an8': '307330'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '24254300',
                                'code_an8': '308100'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '24254100',
                                'code_an8': '308200'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '24250300',
                                'code_an8': '003600'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '24250900',
                                'code_an8': '090600'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '00000872',
                                'code_an8': '000872'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '24300500',
                                'code_an8': '046980'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '00025630',
                                'code_an8': '025630'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '34107300',
                                'code_an8': '821250'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '00850296',
                                'code_an8': '850296'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '00850297',
                                'code_an8': '850297'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '00850298',
                                'code_an8': '850298'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '00850299',
                                'code_an8': '850299'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '34201800',
                                'code_an8': '233260'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '00850292',
                                'code_an8': '850292'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '00850293',
                                'code_an8': '850293'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '00850294',
                                'code_an8': '850294'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '28051800',
                                'code_an8': '304250'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '34100900',
                                'code_an8': '242600'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '30304300',
                                'code_an8': '515050'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '24257300',
                                'code_an8': '304500'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '24253500',
                                'code_an8': '304020'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '34152500',
                                'code_an8': '159660'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '34150200',
                                'code_an8': '002700'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '34106600',
                                'code_an8': '375060'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '22202100',
                                'code_an8': '303880'
                            }, {
                                'libelle_rubrique': '',
                                'code_an9': '24253900',
                                'code_an8': '304520'
                            }],
                            'type_crc': 'C',
                            'formes_normales': ['M_PELLET'],
                            'rubriques_fines': []
                        }],
                        'type_bloc_activite': 'IMMEDIAT',
                        'correction': False,
                        'machine_learning_etat': 'valide',
                        'machine_learning_source': 'rr',
                        'identifiant': 'ac4',
                        'rubriques': [],
                        'forme_canonique': 'poele a Pellet',
                        'libelle': 'poele a pellet',
                        'faible_pertinence': True
                    }]
                }]
            },
            'tags': ['743'],
            'id': 'poele a pellet',
            'requete': {
                'tx_fragile': '0.16654322',
                'libelle': 'poele a pellet',
                'frequence': 51
            },
            'creation_date': '2016-01-13T02:23:18.206228+00:00',
            'janus': {
                'request': {
                    'comments': [],
                    'tags': [],
                    'raw_query': 'poele a pellet',
                    'user': None
                },
                'status': None,
                'doc_version': '743',
                'dedupkey': '5f0f25042e1f4d77ffd78410612574a0',
                'tags': ['743']
            },
            'tech': {
                'api_response': {
                    'status_code': 200
                },
                'delphes': {
                    'versionDelphes': '6.3.2',
                    'versionADNc': '743',
                    'dateADNc': '2016-01-12 01:07:42-00:00',
                    'version': '27',
                    'ok': 'true',
                    'schemaADNc': 'adncprod',
                    'date': '2016-01-13 01:15:24-00:00',
                    'commentaire': ''
                }
            }
        }

    mapping = [{'path': '', 'id': 'id'}, {'path': 'reponse.blocs_reponses', 'id': 'identifiant_de_bloc'}, {'path': 'reponse.blocs_reponses.activites_affichage_immediat', 'id': 'identifiant'}, {'path': 'reponse.blocs_reponses.activites_affichage_immediat.rubriques', 'id': 'code_an8'}]
    ignored_fields = ['creation_date', 'auto_state', 'user', 'status', 'comments', 'requete', 'tags', 'janus', 'tech']

    diff = get_diff(obj_a, obj_b, [], mapping, ignored_fields, False, False)

    assert diff == []
