import requests
import base64


def auth():
    # Abra o arquivo para leitura
    with open('auth.txt', 'r') as arquivo:
        # Leia e armazene cada linha em uma variável
        organization = arquivo.readline().strip()
        project = arquivo.readline().strip()
        personal_access_token = arquivo.readline().strip()
        query_id = arquivo.readline().strip()

    # Codificar o token de acesso pessoal para a autenticação
    token = base64.b64encode(bytes(f":{personal_access_token}", "utf-8")).decode("utf-8")

    # Definir cabeçalhos para a solicitação
    headers = {
        "Authorization": f"Basic {token}"
    }
    get_query_results(organization, project, query_id, headers)


def get_query_results(organization, project, query_id, headers):
    task_ids = []
    # URL da API para extrair uma consulta específica
    # fonte: https://learn.microsoft.com/pt-br/rest/api/azure/devops/wit/wiql/query-by-wiql?view=azure-devops-rest-7.0&tabs=HTTP
    url = f'https://dev.azure.com/{organization}/{project}/_apis/wit/wiql/{query_id}?api-version=7.1-preview.2'

    # Fazer a solicitação GET
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        query_data = response.json()
        for query in query_data["workItems"]:
            task_ids.append(query['id'])
    else:
        print("Falha ao buscar a consulta. Código de status:", response.status_code)
    get_items_results(task_ids, organization, headers)
    return task_ids


def get_items_results(task_ids, organization, headers):
    fields = [
        "System.Id",
        "System.Title",
        "System.WorkItemType",
        "System.State",
        "System.AssignedTo",
        "System.AreaPath",
        "System.CreatedDate",
        "System.CreatedBy",
        "Microsoft.VSTS.Common.Priority",
        "Microsoft.VSTS.Common.ClosedDate",
        "Microsoft.VSTS.Common.ClosedBy",
        "Microsoft.VSTS.Common.ValueArea",
        "Custom.Customer",
        "Custom.Squad",
        "Custom.As",
        "Custom.For",
        "Custom.Iwant",
        "Custom.97a1d976-966c-491b-a2aa-ab4d34ac9caa"  # CS/GP
    ]

    lista_fields = ','.join(fields)
    for item in task_ids:
        #  fonte: https://learn.microsoft.com/pt-br/rest/api/azure/devops/wit/work-items/list?tabs=HTTP
        url_task = f'https://dev.azure.com/{organization}/_apis/wit/workitems?ids={item}&fields={lista_fields}&api-version=7.2-preview.3'
        # url_task = f'https://dev.azure.com/{organization}/_apis/wit/workitems?ids=59361&$expand=all&api-version=7.2-preview.3'
        response = requests.get(url_task, headers=headers)
        if response.status_code == 200:
            task_data = response.json()
            print(task_data)
        else:
            print("Falha ao buscar a consulta. Código de status:", response.status_code)


auth()
