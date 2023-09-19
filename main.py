import requests
import base64
import csv


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
    return organization, project, query_id, headers


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
    return task_ids


def get_items_results(task_ids, organization, headers):
    processed_data = []
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
        "Custom.As",
        "Custom.For",
        "Custom.Iwant",
        "Custom.97a1d976-966c-491b-a2aa-ab4d34ac9caa"  # CS/GP
    ]
    lista_fields = ','.join(fields)
    for item in task_ids:
        #  fonte: https://learn.microsoft.com/pt-br/rest/api/azure/devops/wit/work-items/list?tabs=HTTP
        url_task = f'https://dev.azure.com/{organization}/_apis/wit/workitems?ids={item}&fields={lista_fields}&api-version=7.2-preview.3'
        response = requests.get(url_task, headers=headers)
        if response.status_code == 200:
            task_data = response.json()
            id = task_data['value'][0]['fields']['System.Id']
            title = task_data['value'][0]['fields']['System.Title']
            type = task_data['value'][0]['fields']['System.WorkItemType']
            state = task_data['value'][0]['fields']['System.State']
            if 'System.AssignedTo' in task_data['value'][0]['fields']:
                assigned_to = task_data['value'][0]['fields']['System.AssignedTo']['displayName']
            else:
                assigned_to = ''
            area_path = task_data['value'][0]['fields']['System.AreaPath']
            if 'System.CreatedDate' in task_data['value'][0]['fields']:
                created_date = task_data['value'][0]['fields']['System.CreatedDate']
            else:
                created_date = ''
            created_by = task_data['value'][0]['fields']['System.CreatedBy']['displayName']
            priority = task_data['value'][0]['fields']['Microsoft.VSTS.Common.Priority']
            if 'Microsoft.VSTS.Common.ClosedDate' in task_data['value'][0]['fields']:
                closed_date = task_data['value'][0]['fields']['Microsoft.VSTS.Common.ClosedDate']
            else:
                closed_date = ''
            if 'Microsoft.VSTS.Common.ClosedBy' in task_data['value'][0]['fields']:
                closed_by = task_data['value'][0]['fields']['Microsoft.VSTS.Common.ClosedBy']['displayName']
            else:
                closed_by = ''
            if 'Microsoft.VSTS.Common.ValueArea' in task_data['value'][0]['fields']:
                value_area = task_data['value'][0]['fields']['Microsoft.VSTS.Common.ValueArea']
            else:
                value_area = ''
            customer = task_data['value'][0]['fields']['Custom.Customer']
            if 'Custom.97a1d976-966c-491b-a2aa-ab4d34ac9caa' in task_data['value'][0]['fields']:
                gp_cs = task_data['value'][0]['fields']['Custom.97a1d976-966c-491b-a2aa-ab4d34ac9caa']['displayName']
            else:
                gp_cs = ''
            processed_data.append([id,
                                   title,
                                   type,
                                   state,
                                   assigned_to,
                                   area_path,
                                   created_date,
                                   created_by,
                                   priority,
                                   closed_date,
                                   closed_by,
                                   value_area,
                                   customer,
                                   gp_cs])
        else:
            print("Falha ao buscar a consulta. Código de status:", response.status_code)
            # Salvar o arquivo
    return processed_data


def salvar_csv(processed_data):
    with open('teste.csv', "w", newline="", encoding="utf-8") as arquivo_csv:
        escritor_csv = csv.writer(arquivo_csv, delimiter=";")
        # Escrever o cabeçalho
        cabecalho = ['id',
                     'title',
                     'type',
                     'state',
                     'assigned_to',
                     'area_path',
                     'created_date',
                     'created_by',
                     'priority',
                     'closed_date',
                     'closed_by',
                     'value_area',
                     'customer',
                     'gp_cs']
        escritor_csv.writerow(cabecalho)
        for linha in processed_data:
            escritor_csv.writerow(linha)


organization, project, query_id, headers = auth()
task_ids = get_query_results(organization, project, query_id, headers)
processed_data = get_items_results(task_ids, organization, headers)
salvar_csv(processed_data)
