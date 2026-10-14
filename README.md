# Simulador AWS Cloud Practitioner (CLF-C02)

Aplicação local para praticar para a certificação **AWS Certified Cloud Practitioner (CLF-C02)**. As questões iniciais são autorais, criadas para estudo, e não usam dumps ou conteúdo de prova.

## Abrir no Windows

1. Abra o PowerShell nesta pasta.
2. Crie e ative um ambiente virtual (somente na primeira vez):

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Instale as dependências (somente na primeira vez):

```powershell
pip install -r requirements.txt
```

4. Inicie:

```powershell
streamlit run app.py
```

O navegador abrirá em `http://localhost:8501`. Para parar, use `Ctrl+C` no PowerShell.

## Dados locais

O arquivo `data/simulator.db` é criado automaticamente e guarda questões, tentativas e respostas. Faça uma cópia desse arquivo caso queira guardar um backup do progresso. Para reiniciar todo o progresso, feche o aplicativo e exclua apenas esse arquivo.

## Banco de questões

Além das questões autorais iniciais, o projeto inclui o banco público CLF-C02 do [CloudCertPrep](https://github.com/nastaso/cloudcertprep), distribuído sob a licença MIT. Os arquivos e uma cópia da licença estão em `question_bank/cloudcertprep/`; cada questão importada é identificada no banco e na revisão como **CloudCertPrep (MIT)**. As questões desse banco foram traduzidas para português do Brasil (`question_bank/cloudcertprep/clf-c02-pt/`), mantendo os nomes de serviços em inglês, como na prova em PT-BR. O app mostra a tradução por padrão; o botão **Ver original em inglês** em cada questão abre o texto original, e a opção **Questões em inglês** na barra lateral troca o simulado inteiro para o inglês. Esse material é de prática: não é um dump, não é afiliado à AWS e não garante que uma questão apareça no exame.

## Conteúdo e lógica

- Diário: 20 questões e 30 minutos; completo: 65 questões e 90 minutos. O relógio atualiza sozinho a cada segundo.
- Reforço: até 20 questões que você errou e ainda não acertou depois, com 90 segundos por questão. Não conta para a sequência nem para a prontidão.
- Prontidão: os 3 últimos simulados completos com 80% ou mais indicam que dá para agendar a prova.
- Pesos CLF-C02: Conceitos 24%, Segurança 30%, Tecnologia 34%, Cobrança/Preços/Suporte 12%.
- Seleção adaptativa: adiciona prioridade a domínios e tópicos com menor acerto, reduzindo questões respondidas recentemente.
- A correção só aparece após **Enviar simulado**.
- Há perguntas de resposta única e múltipla. Nas múltiplas, todas as alternativas corretas precisam ser selecionadas.
## Ferramentas de estudo

- **Plano de hoje** (dashboard): flashcards e anotações que vencem hoje e erros pendentes para o reforço.
- **Caderno de erros**: embaixo de cada correção errada há um formulário com três campos (o que a questão pedia, o que você marcou e por quê, qual pista apontava para a certa). As anotações voltam para revisão em 1, 3, 7, 14 e 30 dias; se você esquecer, voltam no dia seguinte.
- **Flashcards**: cerca de 140 cards dos serviços e conceitos que mais se confundem na prova, com a mesma revisão espaçada.
- **Guia de estudo**: tabelas de comparação por grupo (com modo teste que esconde os nomes), o método de estudo e links das fontes oficiais.
- Flashcards e caderno podem ser exportados para o Anki (arquivo de texto separado por Tab).

- Referências apontam para documentação e treinamento oficiais da AWS. Confirme o guia de exame mais atual no site oficial antes de marcar a prova.

## Estrutura

```
app.py              interface e fluxo
database.py         SQLite, relatórios e seleção adaptativa
seed_questions.py   banco inicial de questões autorais
study_content.py    tabelas de comparação, flashcards e fontes oficiais
tests/              testes (python -m unittest discover -s tests -t .)
question_bank/      banco CloudCertPrep (original e tradução em clf-c02-pt/)
data/simulator.db   criado em execução (não versionar)
```
