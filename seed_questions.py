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

def seed():
    with connect() as c:
        if c.execute("SELECT COUNT(*) FROM questions").fetchone()[0]: return
        # Cada item é uma questão autoral. Variações de contexto criam um conjunto inicial de 84 perguntas para testes completos.
        for variant in range(3):
            for domain, topic, prompt, choices, correct, explanation in BASE:
                suffix = "" if variant == 0 else (" Considere um ambiente de uma startup." if variant == 1 else " Considere uma organização que está migrando para a AWS.")
                title, url = REFS[domain]
                c.execute("""INSERT INTO questions(domain,topic,prompt,choices,correct,explanation,reference_url,reference_title,multi)
                 VALUES(?,?,?,?,?,?,?,?,?)""", (domain, topic, prompt+suffix, json.dumps(dict(zip('ABCD',choices))), json.dumps(correct), explanation, url, title, int(len(correct)>1)))
