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

    assert diff == []
