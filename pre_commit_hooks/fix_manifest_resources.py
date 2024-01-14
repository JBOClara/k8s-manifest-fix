#!/Users/jboulanger/.virtualenvs/venv_dow_reco_resources/bin/python
from __future__ import annotations

import argparse
import logging
import os
import re
import sys
import time
import tokenize
from typing import Any
from typing import Dict
from typing import Sequence

import requests
import ruamel.yaml

# Configure logging
logging.basicConfig(stream=sys.stderr, level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')

if sys.version_info >= (3, 12):  # pragma: >=3.12 cover
    FSTRING_START = tokenize.FSTRING_START
    FSTRING_END = tokenize.FSTRING_END
else:  # pragma: <3.12 cover
    FSTRING_START = FSTRING_END = -1

START_QUOTE_RE = re.compile('^[a-zA-Z]*"')

yaml = ruamel.yaml.YAML(typ='rt')
yaml.width = 10000
yaml.indent(mapping=2, sequence=4, offset=2)
yaml.default_flow_style = False
yaml.preserve_quotes = True
yaml.representer.add_representer(
    type(None), lambda self, _: self.represent_scalar('tag:yaml.org,2002:null', 'null'),
)

# get kubernetes manifest identity


# def get_manifest_identity(filename: str) -> Dict[str, str]:
#     with open(filename) as f:
#         manifest = yaml.load(f)
#         if manifest is None:
#             return {}
#         target_kind = manifest['kind']
#         target_name = manifest['metadata']['name']
#         namespace = manifest['metadata']['namespace']
#         containers_name = [container['name'] for container in manifest['spec']['template']['spec']['containers']]
#         return {
#             'target_kind': target_kind,
#             'target_name': target_name,
#             'namespace': namespace,
#             'containers_name': containers_name,
#             'file_path': filename,
#         }

def get_manifest_identity(filename: str) -> dict[str, str | list[str]]:
    with open(filename) as f:
        manifest = yaml.safe_load(f)
        if manifest is None:
            return {}
        target_kind = manifest.get('kind', '')
        target_name = manifest.get('metadata', {}).get('name', '')
        namespace = manifest.get('metadata', {}).get('namespace', '')
        containers = manifest.get('spec', {}).get('template', {}).get('spec', {}).get('containers', [])
        containers_name = [container.get('name', '') for container in containers]
        return {
            'target_kind': target_kind,
            'target_name': target_name,
            'namespace': namespace,
            'containers_name': containers_name,
            'file_path': filename,
        }

# # Récupérer les métriques de Prometheus
# # time=<rfc3339 | unix_timestamp>: Evaluation timestamp. Optional.
# # https://prometheus.mon.preprod.ops.daysofwonder.com/api/v1/query?query=sum%28kube_customresource_vpa_containerrecommendations_target%7Bnamespace%3D%7E%22%28api%7Casmodeede%7Casmosvc%7Cblog%7Ccnsplt%7Ccron%7Cdefault%7Charfang%7Cis%7Cpostfix%7Crank%7Cscalable%7Cthoth%7Cwww%29%22%7D%29+by+%28resource%2Ctarget_name%2Ccontainer%2Ctarget_kind%2Cnamespace%2Cunit%29&time=1704804377.745
# # https://prometheus.mon.preprod.ops.daysofwonder.com/api/v1/query?query=sum%28kube_customresource_vpa_containerrecommendations_target%7Bnamespace%3D%7E%22%28api%7Casmodeede%7Casmosvc%7Cblog%7Ccnsplt%7Ccron%7Cdefault%7Charfang%7Cis%7Cpostfix%7Crank%7Cscalable%7Cthoth%7Cwww%29%22%7D%29+by+%28resource%2Ctarget_name%2Ccontainer%2Ctarget_kind%2Cnamespace%2Cunit%29&time=1704804400.752
# metrics:
# kube_customresource_vpa_containerrecommendations_target{container="accessplus-front", customresource_group="autoscaling.k8s.io", customresource_kind="VerticalPodAutoscaler", customresource_version="v1", endpoint="http", instance="10.210.25.95:8080", job="kube-state-metrics", namespace="accessplus", pod="kube-prometheus-kube-state-metrics-76c895d964-67jfr", resource="cpu", service="kube-prometheus-kube-state-metrics", target_api_version="autoscaling.k8s.io/v1", target_kind="Deployment", target_name="accessplus-front", unit="core", verticalpodautoscaler="accessplus-front"}
# query:
# sum(kube_customresource_vpa_containerrecommendations_target{namespace="%s"})+by+(resource,target_name,container,target_kind,namespace,unit)&time
# # make the time dynamic
# time_now = int(time.time())
# response = requests.get(
#     f"https://prometheus.mon.{ENV}.ops.daysofwonder.com/api/v1/query?query=sum%28kube_customresource_vpa_containerrecommendations_target%7Bnamespace%3D%7E%22%28api%7Casmodeede%7Casmosvc%7Cblog%7Ccnsplt%7Ccron%7Cdefault%7Charfang%7Cis%7Cpostfix%7Crank%7Cscalable%7Cthoth%7Cwww%29%22%7D%29+by+%28resource%2Ctarget_name%2Ccontainer%2Ctarget_kind%2Cnamespace%2Cunit%29&time={time_now}.174"
# )
# if response.status_code != 200:
#     logging.info(f"Error: {response.status_code}")
#     exit(1)
# metrics = response.json()["data"]["result"]


def get_metrics(manifest_identity: dict[str, str | list[str]], env: str) -> list[dict[str, str]]:
    time_now = int(time.time())
    # get metrics from prometheus for the manifest filter by namespace, target_kind, target_name and loop on containers_name
    response = requests.get(
        f"https://prometheus.mon.{env}.ops.daysofwonder.com/api/v1/query?query=sum%28kube_customresource_vpa_containerrecommendations_target%7Bnamespace%3D%7E%22%28{manifest_identity['namespace']}%29%22%2Ctarget_kind%3D%7E%22%28{manifest_identity['target_kind']}%29%22%2Ctarget_name%3D%7E%22%28{manifest_identity['target_name']}%29%22%7D%29+by+%28resource%2Ctarget_name%2Ccontainer%2Ctarget_kind%2Cnamespace%2Cunit%29&time={time_now}.174",
    )
    if response.status_code != 200:
        logging.info(f"Error: {response.status_code}")
        exit(1)
    metrics = response.json()['data']['result']
    return metrics


def adjust_resources(filename: str) -> int:
    manifest_identity = get_manifest_identity(filename)
    env = filename.split('/')[0]
    logging.info(f"env: {env}")
    if env not in ['preprod', 'prod']:
        return 0
    metrics = get_metrics(manifest_identity, env)
    if not manifest_identity:
        return 0
    if not metrics:
        return 0
    file_changed = 0
    with open(filename) as f:
        manifest = yaml.load(f)
        if manifest is None:
            return 0
        for metric in metrics:  # type: Dict[Any, Any]
            if isinstance(metric, Dict):
                metric_values: dict[Any, Any] = metric.get('metric', {})
                if isinstance(metric_values, Dict):
                    target_kind = metric_values.get('target_kind', '')
                    if target_kind not in ['Deployment', 'StatefulSet', 'DaemonSet']:
                        return 0
                    else:
                        logging.info(f"file: {filename}")
                target_name = metric_values.get('target_name', '')
                container_name = metric_values.get('container', '')
                resource_type = metric_values.get('resource', '')
                namespace = metric_values.get('namespace', '')
                unit = metric_values.get('unit', '')
                value = float(metric.get('value', [0, 0])[1])
                for container in manifest.get('spec', {}).get('template', {}).get('spec', {}).get('containers', []):
                    if container['name'] == container_name:
                        if 'resources' not in container:
                            container['resources'] = {}
                        if 'requests' not in container['resources']:
                            container['resources']['requests'] = {}
                        if resource_type == 'cpu':
                            if unit == 'core':
                                new_unit = 'm'
                                new_value = int(value * 1000)
                        elif resource_type == 'memory':
                            if unit == 'byte':
                                new_unit = 'Mi'
                                new_value = round(int(value) / 1024 / 1024)
                        if (
                            resource_type in container['resources']['requests'] and container['resources']['requests'][resource_type] == str(new_value) + new_unit
                        ):
                            continue
                        if resource_type in container['resources']['requests']:
                            old_value = container['resources']['requests'][resource_type]
                            logging.info(
                                f"Resource {target_kind}/{namespace}/{target_name} {resource_type} for container {container_name} changed from {old_value} to {new_value}{new_unit}",
                            )
                        container['resources']['requests'][resource_type] = (
                            str(new_value) + new_unit
                        )
                        with open(filename, 'w') as f:
                            yaml.dump(manifest, f)
                            file_changed = + 1
        if file_changed == 0:
            return 0
        else:
            return 1


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('filenames', nargs='*', help='Filenames to fix')
    parser.add_argument('--prometheus_url', help='URL of Prometheus')
    # add an placeholder into the prometheus_url
    parser.add_argument('--env_placeholder', help='prometheus placeholder of the manifest that will be replaced by the env')
    args = parser.parse_args(argv)

    # Log all environment variables
    logging.info('Environment variables:')
    for key, value in os.environ.items():
        logging.info(f"{key}: {value}")

    retv = 0

    for filename in args.filenames:
        return_value = adjust_resources(filename)
        if return_value != 0:
            logging.info(f'Adjust resources in {filename}')
        retv |= return_value

    return retv


if __name__ == '__main__':
    raise SystemExit(main())
