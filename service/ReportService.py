from collections import defaultdict
from datetime import datetime, timedelta
from itertools import groupby

import requests


class ReportService:

    def __init__(self):
        self.token = None
        self.url_base = "https://gitlab.prodesp.sp.gov.br/api/v4/"
        self.id_usuario = None
        self.data_atual = datetime.now()

    def gerar_relatorio(self, token, id_usuario):
        self.token = token
        self.id_usuario = id_usuario

        commit_ordenados = sorted(self.__buscar_commits(), key=lambda x: self.__formatar_data(x["created_at"]))

        lista_commit_detalhes = []

        for commit in commit_ordenados:
            if not commit.get("push_data").get("commit_to"):
                continue

            lista_commit_detalhes.append(self.__buscar_detalhes_commit(commit.get("project_id"), commit.get("push_data").get("commit_to")))

        return self.__agrupar_commits(lista_commit_detalhes)


    def __buscar_commits(self):

        url = f"{self.url_base}/users/{self.id_usuario}/events"

        params = {
            "action": "pushed",
            "private_token": self.token,
            "after": (self.data_atual - timedelta(days=3)).strftime("%Y-%m-%d"),
            "before": (self.data_atual + timedelta(days=2)).strftime("%Y-%m-%d"),
            "per_page": "100",
            "page": "1"
        }

        response = requests.get(url, params)

        return response.json()


    def __buscar_detalhes_commit(self, id_project, hash_commit):
        url = f"{self.url_base}/projects/{id_project}/repository/commits/{hash_commit}"

        params = {
            "action": "pushed",
            "private_token": self.token,
        }

        response = requests.get(url, params)
        return response.json()


    def __formatar_data(self, data_str):
        data = datetime.strptime(data_str, "%Y-%m-%dT%H:%M:%S.%f%z")
        return data.strftime("%Y-%m-%d")

    def __agrupar_commits(self, lista_commit_detalhes):
        grupos = defaultdict(lambda: {"additions": 0, "deletions": 0, "total": 0})

        for commit in lista_commit_detalhes:
            data = self.__formatar_data(commit["created_at"])
            grupos[data]["additions"] += commit["stats"]["additions"]
            grupos[data]["deletions"] += commit["stats"]["deletions"]
            grupos[data]["total"] += commit["stats"]["total"]

        resultado_acumulado = [{"data": data, "additions": valor["additions"], "deletions": valor["deletions"], "total": valor["total"]} for data, valor in grupos.items()]

        return resultado_acumulado