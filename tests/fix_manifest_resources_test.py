from __future__ import annotations

import os
import unittest
from unittest.mock import patch

import yaml

from pre_commit_hooks.fix_manifest_resources import adjust_resources


class TestAdjustResources(unittest.TestCase):
    @patch('pre_commit_hooks.fix_manifest_resources.get_manifest_identity')
    @patch('pre_commit_hooks.fix_manifest_resources.get_metrics')
    def test_adjust_resources(self, mock_get_metrics, mock_get_manifest_identity):
        # Définir les valeurs de retour pour les fonctions mockées
        mock_get_manifest_identity.return_value = 'identity'
        mock_get_metrics.return_value = [
            {
                'metric': {
                    'target_kind': 'Deployment',
                    'target_name': 'target',
                    'container': 'container',
                    'resource': 'cpu',
                    'namespace': 'namespace',
                    'unit': 'core',
                },
                'value': [0, 0.5],
            },
        ]

        # Créer un fichier temporaire pour le test
        with open('temp.yaml', 'w') as f:
            yaml.dump(
                {
                    'spec': {
                        'template': {
                            'spec': {
                                'containers': [
                                    {
                                        'name': 'container',
                                        'resources': {
                                            'requests': {
                                                'cpu': '500m',
                                            },
                                        },
                                    },
                                ],
                            },
                        },
                    },
                }, f,
            )

        # Appeler la fonction avec le fichier temporaire
        result = adjust_resources('temp.yaml')

        # Vérifier que la fonction a retourné 1 (fichier modifié)
        self.assertEqual(result, 1)

        # Vérifier que le fichier a été modifié correctement
        with open('temp.yaml') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            self.assertEqual(data['spec']['template']['spec']['containers'][0]['resources']['requests']['cpu'], '500m')

        # Supprimer le fichier temporaire
        os.remove('temp.yaml')


if __name__ == '__main__':
    unittest.main()
