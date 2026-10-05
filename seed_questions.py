import json
from database import connect

REFS = {
 "Conceitos de Nuvem": ("AWS Cloud Computing", "https://aws.amazon.com/what-is-cloud-computing/"),
 "Segurança e Conformidade": ("AWS Security", "https://aws.amazon.com/security/"),
 "Tecnologia e Serviços": ("AWS Cloud Practitioner Essentials", "https://aws.amazon.com/training/digital/aws-cloud-practitioner-essentials/"),
 "Cobrança, Preços e Suporte": ("AWS Pricing", "https://aws.amazon.com/pricing/"),
}

BASE = [
("Conceitos de Nuvem","Benefícios","Qual benefício da nuvem permite trocar gasto inicial elevado por pagamento conforme o uso?",["Economia de escala","Elasticidade","Despesa variável","Alta disponibilidade"],["C"],"O modelo de pagamento conforme o uso transforma parte do investimento inicial em custo operacional variável."),
("Conceitos de Nuvem","Elasticidade","Uma aplicação aumenta servidores automaticamente em um pico e os reduz depois. Qual conceito descreve isso?",["Elasticidade","Governança","Região","Criptografia"],["A"],"Elasticidade ajusta recursos à demanda e evita manter capacidade ociosa."),
("Conceitos de Nuvem","Modelo de implantação","Qual opção descreve uma nuvem híbrida?",["Somente data center próprio","Recursos on-premises integrados a recursos de nuvem","Duas regiões AWS","Apenas SaaS"],["B"],"Nuvem híbrida combina ambiente local com infraestrutura de nuvem."),
("Conceitos de Nuvem","Infraestrutura global","Qual elemento da infraestrutura global AWS é uma localização geográfica física com várias Zonas de Disponibilidade?",["Edge location","Região","VPC","Subnet"],["B"],"Uma Região AWS é uma área geográfica separada composta por múltiplas AZs."),
("Conceitos de Nuvem","Alta disponibilidade","Para aumentar disponibilidade de uma carga de trabalho, qual arquitetura é recomendada?",["Uma instância em uma AZ","Recursos em várias AZs","Uma subnet pública","Um único bucket S3"],["B"],"Distribuir componentes entre AZs reduz o impacto de falha em uma única zona."),
("Segurança e Conformidade","Responsabilidade compartilhada","Em EC2, quem é responsável por aplicar patches no sistema operacional convidado?",["AWS","Cliente","Fornecedor de internet","AWS Marketplace"],["B"],"No modelo compartilhado, o cliente gerencia o SO convidado e suas configurações em EC2."),
("Segurança e Conformidade","IAM","Qual prática é mais indicada para uma aplicação em EC2 acessar um bucket S3?",["Chave de acesso no código","Usuário root","IAM role anexada à instância","Senha compartilhada"],["C"],"Uma role fornece credenciais temporárias sem armazenar chaves de longa duração no código."),
("Segurança e Conformidade","MFA","Qual controle adiciona uma segunda evidência para entrar em uma conta AWS?",["Security Group","MFA","Tag","CloudTrail"],["B"],"A autenticação multifator exige mais de um fator de verificação."),
("Segurança e Conformidade","IAM","Qual princípio recomenda conceder apenas as permissões necessárias?",["Menor privilégio","Alta disponibilidade","Elasticidade","Cobrança consolidada"],["A"],"Menor privilégio limita o acesso ao mínimo exigido pela tarefa."),
("Segurança e Conformidade","Auditoria","Qual serviço registra chamadas de API e atividades da conta AWS para auditoria?",["CloudTrail","CloudWatch","Trusted Advisor","Inspector"],["A"],"AWS CloudTrail registra eventos de atividade e API na conta."),
("Segurança e Conformidade","Criptografia","Qual serviço gerencia chaves usadas para criptografia em muitos serviços AWS?",["AWS KMS","Amazon SQS","Amazon Route 53","AWS Budgets"],["A"],"AWS Key Management Service cria e controla chaves de criptografia."),
("Tecnologia e Serviços","Compute","Qual serviço oferece máquinas virtuais configuráveis sob demanda?",["Amazon EC2","Amazon S3","Amazon RDS","Amazon SNS"],["A"],"Amazon EC2 fornece capacidade de computação virtualizada."),
("Tecnologia e Serviços","Serverless","Qual serviço executa código em resposta a eventos sem administrar servidores?",["AWS Lambda","Amazon EBS","Amazon EC2","AWS Direct Connect"],["A"],"AWS Lambda executa funções sem que você provisione ou gerencie servidores."),
("Tecnologia e Serviços","Armazenamento","Qual serviço é armazenamento de objetos altamente durável?",["Amazon S3","Amazon EFS","Amazon EBS","Instance Store"],["A"],"Amazon S3 armazena objetos em buckets."),
("Tecnologia e Serviços","Banco de dados","Qual serviço é um banco relacional gerenciado?",["Amazon RDS","Amazon DynamoDB","Amazon S3","Amazon Redshift"],["A"],"Amazon RDS facilita operar bancos de dados relacionais na AWS."),
("Tecnologia e Serviços","Banco de dados","Qual serviço NoSQL gerenciado atende cargas com baixa latência em escala?",["Amazon DynamoDB","Amazon RDS","Amazon Aurora","Amazon EFS"],["A"],"DynamoDB é um banco NoSQL serverless e gerenciado."),
("Tecnologia e Serviços","Rede","Qual serviço fornece uma rede virtual logicamente isolada na AWS?",["Amazon VPC","Amazon Route 53","AWS IAM","Amazon CloudFront"],["A"],"Amazon VPC permite definir recursos de rede em um ambiente virtual isolado."),
("Tecnologia e Serviços","CDN","Qual serviço entrega conteúdo por meio de locais de borda mais próximos dos usuários?",["Amazon CloudFront","AWS Global Accelerator","Amazon S3","Elastic Load Balancing"],["A"],"CloudFront é uma CDN que usa uma rede global de edge locations."),
("Tecnologia e Serviços","Monitoramento","Qual serviço coleta métricas e pode disparar alarmes sobre recursos AWS?",["Amazon CloudWatch","AWS CloudTrail","AWS Artifact","AWS Shield"],["A"],"CloudWatch fornece observabilidade, métricas, logs e alarmes."),
("Tecnologia e Serviços","Mensageria","Qual serviço desacopla componentes usando filas de mensagens?",["Amazon SQS","Amazon SNS","Amazon SES","AWS Step Functions"],["A"],"Amazon SQS oferece filas para comunicação assíncrona entre componentes."),
("Tecnologia e Serviços","Múltipla escolha","Quais são serviços de computação? Selecione DUAS opções.",["Amazon EC2","AWS Lambda","Amazon S3","Amazon RDS"],["A","B"],"EC2 fornece máquinas virtuais e Lambda executa código serverless; S3 é armazenamento e RDS é banco de dados."),
("Segurança e Conformidade","Múltipla escolha","Quais ações ajudam a proteger a conta root? Selecione DUAS opções.",["Ativar MFA","Usar a root para tarefas diárias","Evitar criar chaves de acesso root","Compartilhar a senha"],["A","C"],"A AWS recomenda MFA para root e não criar/usar chaves de acesso root para operações cotidianas."),
("Cobrança, Preços e Suporte","Preços","Qual ferramenta permite definir um orçamento e receber alertas sobre custos ou uso?",["AWS Budgets","AWS IAM","Amazon Inspector","AWS CloudFormation"],["A"],"AWS Budgets permite acompanhar custos, uso e cobertura e emitir alertas."),
("Cobrança, Preços e Suporte","Otimização de custos","Qual ferramenta apresenta recomendações de economia com base no uso de EC2?",["AWS Cost Explorer","AWS Trusted Advisor","AWS Artifact","AWS CloudTrail"],["B"],"Trusted Advisor fornece verificações e recomendações, inclusive de otimização de custos."),
("Cobrança, Preços e Suporte","Faturamento","Qual serviço ajuda a visualizar e analisar custos e uso ao longo do tempo?",["AWS Cost Explorer","Amazon CloudWatch","AWS Config","Amazon QuickSight"],["A"],"Cost Explorer visualiza e explora custos e uso históricos e previstos."),
("Cobrança, Preços e Suporte","Suporte","Qual plano de suporte AWS inclui um Technical Account Manager (TAM) designado?",["Basic","Developer","Business","Enterprise Support"],["D"],"O Enterprise Support inclui um TAM designado para orientação proativa."),
("Cobrança, Preços e Suporte","Pricing","Qual opção de compra costuma oferecer desconto em troca de compromisso de uso por um período?",["On-Demand","Savings Plans","Free Tier","Data transfer out"],["B"],"Savings Plans oferecem preços reduzidos mediante compromisso de uso consistente."),
("Cobrança, Preços e Suporte","Organizações","Qual serviço permite cobrança consolidada para múltiplas contas AWS?",["AWS Organizations","AWS IAM","AWS Support","Amazon Cognito"],["A"],"AWS Organizations permite gerenciar várias contas e usar faturamento consolidado."),
]

# Perguntas adicionais e distintas, redigidas para este projeto a partir dos
# tópicos do guia CLF-C02 e documentação oficial. Não são questões de prova.
EXTRA = [
 ("Conceitos de Nuvem","Economia de escala","Por que a AWS pode oferecer preços menores quando muitos clientes usam a mesma infraestrutura?",["Economias de escala","Uma única AZ","MFA obrigatório","Um contrato anual"],["A"],"A escala global da AWS dilui custos de infraestrutura entre muitos clientes."),
 ("Conceitos de Nuvem","Agilidade","Qual benefício permite experimentar uma ideia sem comprar hardware antes?",["Provisionamento sob demanda","Criptografia gerenciada","Suporte Basic","Cache local"],["A"],"Recursos sob demanda permitem criar e encerrar ambientes rapidamente."),
 ("Conceitos de Nuvem","Serviços em nuvem","Qual modelo oferece uma aplicação pronta para uso pela internet?",["IaaS","PaaS","SaaS","On-premises"],["C"],"SaaS entrega o software pronto; o provedor opera a infraestrutura e a aplicação."),
 ("Conceitos de Nuvem","Serviços em nuvem","Em qual modelo o cliente normalmente gerencia sistema operacional e aplicações?",["SaaS","IaaS","Software gerenciado","CDN"],["B"],"No IaaS, o provedor oferece infraestrutura e o cliente gerencia o SO e acima dele."),
 ("Conceitos de Nuvem","Infraestrutura global","Qual recurso usa pontos de presença para reduzir a latência até o usuário final?",["Edge location","Availability Zone","Subnet privada","Placement group"],["A"],"Pontos de presença/edge locations ficam próximos aos usuários e são usados por serviços de borda."),
 ("Conceitos de Nuvem","Infraestrutura global","Qual é a melhor descrição de uma Zona de Disponibilidade?",["Uma Região inteira","Um ou mais data centers isolados dentro de uma Região","Uma conta AWS","Uma rede de entrega"],["B"],"AZs são locais isolados dentro de uma Região, projetados para tolerância a falhas."),
 ("Conceitos de Nuvem","Resiliência","Qual conceito descreve continuar operando mesmo quando um componente falha?",["Tolerância a falhas","Menor privilégio","Cobrança consolidada","Tagueamento"],["A"],"Tolerância a falhas mantém o serviço disponível apesar de falhas de componentes."),
 ("Conceitos de Nuvem","Escalabilidade","Uma aplicação passa de duas para dez instâncias para atender mais tráfego. Isso é qual capacidade?",["Escalabilidade","Conformidade","Auditoria","Imutabilidade"],["A"],"Escalabilidade é a capacidade de aumentar ou diminuir recursos para atender demanda."),
 ("Conceitos de Nuvem","Globalização","Para atender requisitos de residência de dados, qual decisão é mais relevante?",["Escolher a Região adequada","Trocar uma IAM role","Criar uma tag","Usar SQS"],["A"],"A escolha de Região determina onde os dados e recursos são hospedados."),
 ("Conceitos de Nuvem","AWS Well-Architected","Qual pilar trata de recuperação de falhas e adaptação a mudanças de demanda?",["Confiabilidade","Segurança","Sustentabilidade","Otimização de custos"],["A"],"O pilar de Confiabilidade inclui recuperação de falhas e adaptação dinâmica."),
 ("Conceitos de Nuvem","AWS Well-Architected","Qual pilar busca evitar gastos desnecessários?",["Excelência operacional","Otimização de custos","Segurança","Performance"],["B"],"Otimização de custos foca em eliminar despesas desnecessárias e medir eficiência."),
 ("Conceitos de Nuvem","Tags","Para que tags são mais úteis em uma conta AWS?",["Organizar e alocar custos por projeto","Substituir permissões IAM","Criptografar dados","Criar backups"],["A"],"Tags permitem identificar recursos e detalhar custos por centro de custo, projeto ou ambiente."),
 ("Segurança e Conformidade","AWS Organizations","Qual controle define o limite máximo de permissões em contas de uma organização?",["SCP","Security Group","NACL","MFA"],["A"],"Service Control Policies definem a permissão máxima disponível às contas de uma organização."),
 ("Segurança e Conformidade","AWS Config","Qual serviço registra configurações de recursos e avalia regras de conformidade?",["AWS Config","CloudTrail","CloudWatch","IAM Access Analyzer"],["A"],"AWS Config mantém inventário e histórico de configurações e pode avaliar regras."),
 ("Segurança e Conformidade","DDoS","Qual serviço oferece proteção gerenciada contra ataques DDoS?",["AWS Shield","AWS KMS","Amazon GuardDuty","AWS Artifact"],["A"],"AWS Shield fornece proteção contra ataques DDoS; há camadas Standard e Advanced."),
 ("Segurança e Conformidade","Ameaças","Qual serviço usa análise contínua para detectar atividades potencialmente maliciosas?",["Amazon GuardDuty","AWS Budgets","Amazon Macie","AWS CloudFormation"],["A"],"GuardDuty detecta ameaças com base em logs e inteligência de ameaças."),
 ("Segurança e Conformidade","Dados sensíveis","Qual serviço ajuda a descobrir dados sensíveis armazenados no Amazon S3?",["Amazon Macie","Amazon Inspector","AWS Shield","AWS WAF"],["A"],"Macie usa machine learning e padrões para descobrir e proteger dados sensíveis no S3."),
 ("Segurança e Conformidade","Vulnerabilidades","Qual serviço avalia vulnerabilidades em workloads e imagens de contêiner?",["Amazon Inspector","Amazon Detective","AWS Config","AWS Artifact"],["A"],"Inspector faz avaliação automatizada de vulnerabilidades e exposição."),
 ("Segurança e Conformidade","Aplicações web","Qual serviço filtra tráfego HTTP(S) malicioso com regras configuráveis?",["AWS WAF","AWS Shield","Amazon GuardDuty","AWS KMS"],["A"],"AWS WAF permite criar regras contra padrões como SQL injection e bots."),
 ("Segurança e Conformidade","Conformidade","Onde encontrar relatórios de conformidade e acordos da AWS, como SOC e ISO?",["AWS Artifact","AWS Trusted Advisor","AWS Config","AWS Budgets"],["A"],"AWS Artifact disponibiliza documentos de conformidade e acordos sob demanda."),
 ("Segurança e Conformidade","Credenciais","Qual recurso deve ser preferido para acessos temporários de aplicações e usuários federados?",["Credenciais temporárias do AWS STS","Chaves root","Senha da conta","Access key no código"],["A"],"STS emite credenciais temporárias que reduzem o risco de chaves persistentes."),
 ("Segurança e Conformidade","Federação","Qual serviço facilita conceder acesso AWS a usuários corporativos com identidade central?",["IAM Identity Center","Amazon Route 53","AWS Budgets","Amazon EBS"],["A"],"IAM Identity Center centraliza acesso a contas AWS e aplicações usando identidades existentes."),
 ("Segurança e Conformidade","Rede","Qual componente controla tráfego de entrada e saída de uma instância EC2?",["Security Group","AWS Organizations","KMS key","IAM user"],["A"],"Security Groups funcionam como firewall virtual para instâncias e outros recursos."),
 ("Segurança e Conformidade","Responsabilidade compartilhada","Quem é responsável pela segurança física dos data centers AWS?",["AWS","Cliente","Usuário IAM","Parceiro APN"],["A"],"A AWS é responsável pela segurança da nuvem, incluindo instalações físicas."),
 ("Segurança e Conformidade","Múltipla escolha","Quais são boas práticas de IAM? Selecione DUAS opções.",["Conceder menor privilégio","Ativar MFA","Compartilhar usuários IAM","Usar root diariamente"],["A","B"],"Menor privilégio e MFA reduzem a superfície de ataque e são práticas recomendadas."),
 ("Tecnologia e Serviços","Armazenamento","Qual serviço fornece volumes de bloco persistentes para instâncias EC2?",["Amazon EBS","Amazon S3","Amazon EFS","Amazon Glacier"],["A"],"Amazon EBS fornece armazenamento em bloco que pode ser anexado a instâncias EC2."),
 ("Tecnologia e Serviços","Armazenamento","Qual serviço fornece um sistema de arquivos elástico compartilhado para Linux?",["Amazon EFS","Amazon EBS","Amazon S3","AWS Storage Gateway"],["A"],"Amazon EFS fornece armazenamento de arquivos elástico e compartilhado para workloads Linux."),
 ("Tecnologia e Serviços","Backup","Qual serviço automatiza a criação e retenção de backups em vários serviços AWS?",["AWS Backup","AWS Budgets","Amazon SQS","AWS WAF"],["A"],"AWS Backup centraliza políticas e operações de backup para serviços compatíveis."),
 ("Tecnologia e Serviços","DNS","Qual serviço registra domínios e roteia consultas DNS?",["Amazon Route 53","Amazon VPC","AWS Direct Connect","Amazon CloudFront"],["A"],"Route 53 oferece DNS gerenciado e registro de domínios."),
 ("Tecnologia e Serviços","Conectividade","Qual serviço cria uma conexão privada dedicada entre o data center e a AWS?",["AWS Direct Connect","AWS VPN","Amazon CloudFront","AWS Transit Gateway"],["A"],"Direct Connect fornece conectividade dedicada da rede local à AWS."),
 ("Tecnologia e Serviços","Balanceamento","Qual serviço distribui tráfego entre vários destinos saudáveis?",["Elastic Load Balancing","Amazon Route 53","Amazon SQS","AWS Lambda"],["A"],"Elastic Load Balancing distribui tráfego e melhora disponibilidade das aplicações."),
 ("Tecnologia e Serviços","Auto Scaling","Qual serviço ajusta automaticamente a quantidade de instâncias EC2 conforme a demanda?",["EC2 Auto Scaling","AWS CloudTrail","Amazon CloudFront","AWS KMS"],["A"],"EC2 Auto Scaling mantém a capacidade desejada e reage a métricas ou agendas."),
 ("Tecnologia e Serviços","IaC","Qual serviço cria recursos AWS a partir de templates declarativos?",["AWS CloudFormation","AWS Config","AWS Budgets","Amazon Inspector"],["A"],"CloudFormation trata infraestrutura como código usando templates."),
 ("Tecnologia e Serviços","Contêineres","Qual serviço permite executar contêineres sem administrar servidores?",["AWS Fargate","Amazon EC2","Amazon EBS","AWS Outposts"],["A"],"Fargate é computação serverless para contêineres em ECS e EKS."),
 ("Tecnologia e Serviços","Notificações","Qual serviço publica mensagens para vários assinantes por tópicos?",["Amazon SNS","Amazon SQS","Amazon SES","Amazon EventBridge"],["A"],"Amazon SNS usa o padrão pub/sub para distribuir mensagens a assinantes."),
 ("Tecnologia e Serviços","E-mail","Qual serviço AWS envia e-mails transacionais e em massa?",["Amazon SES","Amazon SNS","Amazon SQS","Amazon Connect"],["A"],"Amazon Simple Email Service é um serviço de envio de e-mail escalável."),
 ("Tecnologia e Serviços","Migração","Qual serviço ajuda a descobrir servidores on-premises e planejar migração para AWS?",["AWS Application Discovery Service","AWS Backup","Amazon Macie","AWS WAF"],["A"],"Application Discovery Service coleta dados de servidores para planejamento de migração."),
 ("Tecnologia e Serviços","Suporte","Qual serviço oferece recomendações sobre custos, desempenho, segurança e limites de serviço?",["AWS Trusted Advisor","AWS CloudTrail","AWS Artifact","Amazon GuardDuty"],["A"],"Trusted Advisor analisa o ambiente e produz recomendações em várias categorias."),
 ("Cobrança, Preços e Suporte","Free Tier","Qual página ajuda a acompanhar o consumo de ofertas gratuitas da AWS?",["AWS Free Tier","AWS Artifact","IAM Identity Center","Amazon VPC"],["A"],"O painel AWS Free Tier mostra uso e limites aplicáveis das ofertas gratuitas."),
 ("Cobrança, Preços e Suporte","Preços","Qual ferramenta estima custos antes de criar recursos?",["AWS Pricing Calculator","AWS Cost Explorer","AWS Config","CloudTrail"],["A"],"AWS Pricing Calculator ajuda a estimar preços de arquiteturas antes da implantação."),
 ("Cobrança, Preços e Suporte","Faturamento","Qual relatório detalhado pode ser entregue em S3 para análise de custos?",["Cost and Usage Report","AWS Artifact","CloudTrail trail","Config snapshot"],["A"],"Cost and Usage Report contém dados detalhados de uso e custo para análise."),
 ("Cobrança, Preços e Suporte","Suporte","Qual plano AWS inclui acesso 24x7 por e-mail, chat e telefone para casos de suporte?",["Developer Support","Business Support","Basic Support","AWS Marketplace"],["B"],"Business Support inclui suporte técnico 24x7 por e-mail, chat e telefone."),
 ("Cobrança, Preços e Suporte","Suporte","Qual plano é incluído automaticamente em todas as contas AWS?",["Basic Support","Business Support","Enterprise Support","Developer Support"],["A"],"Toda conta AWS recebe o plano Basic, com documentação, fóruns e suporte de contas/faturamento."),
 ("Cobrança, Preços e Suporte","Preços","Qual modelo cobra pela capacidade computacional sem compromisso de longo prazo?",["On-Demand","Savings Plans","Reserved Instances","Spot Fleet"],["A"],"On-Demand não exige compromisso antecipado e cobra pelo uso."),
]

def seed():
    with connect() as c:
        c.execute("CREATE TABLE IF NOT EXISTS seed_meta (version INTEGER NOT NULL)")
        version = c.execute("SELECT version FROM seed_meta LIMIT 1").fetchone()
        if version and version[0] >= 2:
            return
        # Migração do primeiro banco: mantém as 28 primeiras perguntas e desativa
        # as variações quase idênticas que geravam repetição no mesmo simulado.
        if c.execute("SELECT COUNT(*) FROM questions").fetchone()[0]:
            c.execute("UPDATE questions SET active=0 WHERE id > 28")
        else:
            for domain, topic, prompt, choices, correct, explanation in BASE:
                title, url = REFS[domain]
                c.execute("""INSERT INTO questions(domain,topic,prompt,choices,correct,explanation,reference_url,reference_title,multi)
                 VALUES(?,?,?,?,?,?,?,?,?)""", (domain, topic, prompt, json.dumps(dict(zip('ABCD',choices))), json.dumps(correct), explanation, url, title, int(len(correct)>1)))
        for domain, topic, prompt, choices, correct, explanation in EXTRA:
            title, url = REFS[domain]
            c.execute("""INSERT INTO questions(domain,topic,prompt,choices,correct,explanation,reference_url,reference_title,multi)
             VALUES(?,?,?,?,?,?,?,?,?)""", (domain, topic, prompt, json.dumps(dict(zip('ABCD',choices))), json.dumps(correct), explanation, url, title, int(len(correct)>1)))
        c.execute("DELETE FROM seed_meta")
        c.execute("INSERT INTO seed_meta(version) VALUES(2)")
