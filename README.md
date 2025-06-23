🏗️ Backend
Linguagem: Python

Framework: Django + Django REST Framework (DRF)

Banco de Dados: PostgreSQL

ORM: Django ORM

Armazenamento Vetorial: Qdrant (para RAG, embeddings, IA contextual)

Task Queue: Celery

Broker: Redis

API padrão: FHIR-like, com endpoints RESTful próprios

Observabilidade: Logs estruturados e possibilidade de integração com ferramentas como Datadog

🔬 IA e Machine Learning
Framework de IA:

Uso de embeddings via sentence-transformers

Testes com modelos biomédicos (ex.: pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb)

RAG: Utilização de Qdrant como vetor de contexto para sistemas de recomendação clínica e agentes inteligentes

Data Generation: Simuladores de fluxo realista de pacientes e eventos clínicos (simula dados com faker + regras clínicas do protocolo de sepse)

📱 Frontend
Framework: Flutter (projetado para multiplataforma — tablet, desktop e mobile)

Arquitetura: Modular, com controle de estado e controllers dedicados por feature

Design: Material Design, UI médica segura, com foco em legibilidade, hierarquia de informações e navegação eficiente para profissionais de saúde

☁️ Infraestrutura
Contêineres: Docker

Orquestração: Docker Compose local, com possibilidade de expansão para Kubernetes

Mensageria: Redis (via Celery)

Ambiente de desenvolvimento: WSL (Linux), MacOS e ambientes cloud-ready

Controle de versão: Git + GitHub

Ambiente de deploy (previsto): Kubernetes + PostgreSQL Cloud + Qdrant Cloud (ou local)

🔗 Integrações
Padrões de interoperabilidade: FHIR simplificado

Possibilidade futura: HL7, integração com sistemas HIS e LIS

APIs externas: Integração potencial com sistemas de IA médica, serviços de monitoramento ou EHR externos

🩺 Domínio Clínico
Modelagem: Baseada no fluxo real do protocolo de sepse

Eventos clínicos modelados:

Abertura e encerramento de episódio de sepse

Inserção de culturas (positivas e negativas)

Microbiologia (organismos, antibiogramas)

Administração de antibióticos

Sinais vitais

Exames laboratoriais

Notas clínicas

