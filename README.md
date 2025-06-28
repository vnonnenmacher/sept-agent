# 🦠 Projeto Sepse - Plataforma de Monitoramento e Suporte Clínico

## 📜 Descrição

O Projeto Sepse é uma plataforma para **monitoramento clínico inteligente**, com foco na detecção, acompanhamento e gestão de pacientes com sepse. A solução combina uma base de dados relacional tradicional com uma camada de inteligência semântica baseada em embeddings e busca vetorial.

Ela integra dados de diferentes sistemas hospitalares (HL7, APIs) e permite consultas tanto estruturadas quanto semânticas, facilitando a tomada de decisão clínica, geração de alertas e suporte ao protocolo de sepse.

---

## 🚀 Funcionalidades

* ✅ Ingestão de dados clínicos via **HL7** e **API REST/FHIR-like**.
* ✅ Armazenamento seguro e consistente em banco relacional (**PostgreSQL**).
* ✅ Processamento assíncrono de dados clínicos.
* ✅ Geração de contexto semântico usando **NLP e modelos de embeddings biomédicos**.
* ✅ Armazenamento vetorial no **Qdrant** para busca por similaridade semântica.
* ✅ Dashboard, APIs e ferramentas para suporte clínico e tomada de decisão.
* ✅ Arquitetura escalável e modular.

---

## 🔧 Tecnologias Principais

| Tecnologia           | Função                                    |
| -------------------- | ----------------------------------------- |
| Django + DRF         | Backend e APIs REST                       |
| PostgreSQL           | Banco relacional (Data Lake estruturado)  |
| Redis                | Broker de filas para tarefas              |
| Celery               | Processamento assíncrono                  |
| Qdrant               | Banco de dados vetorial (busca semântica) |
| SentenceTransformers | Geração de embeddings NLP biomédicos      |
| Docker               | Containers e ambiente isolado             |
| HL7 Parser           | Integração com sistemas legados (HIS/LIS) |
| Flutter              | Frontend multiplataforma (Desktop/Mobile) |

---

## 📄 Fluxo da Solução

1. 📥 **Entrada:** Dados chegam via HL7 ou API REST.
2. 💄 **Persistência:** Dados são armazenados no PostgreSQL.
3. ⚙️ **Task:** Uma task Celery é disparada para processar o dado.
4. 🧠 **Semântica:** São geradas frases descritivas com contexto clínico.
5. 📂 **Embeddings:** As frases são convertidas em vetores com NLP.
6. 🗂️ **Indexação:** Vetores são armazenados no Qdrant.
7. 🔍 **Busca:** Queries semânticas recuperam informações contextuais.

---

## 🏗️ Arquitetura

```
[HL7/API] --> [Django API] --> [PostgreSQL]
                               |
                               --> [Celery + Redis] --> [Qdrant (Vetores)]
```

---

## 🚀 Como Rodar Localmente

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/projeto-sepse.git
cd projeto-sepse

# Suba os serviços
docker-compose up --build
```

Acesse a API em: `http://localhost:8000/api/`

✅ Adiocionar protocolo de sepse 
```bash
curl -X POST http://localhost:8000/api/protocols/upload/ \
  -F "file=@hospital-protocolo-sepse-v4.pdf" \
  -F "version=v4"
```
✅ Sugerir Antibiótico
```bash
curl -X POST http://localhost:8000/api/agent/suggest-antibiotic/ \
  -H "Content-Type: application/json" \
  -d '{
        "organism": "Klebsiella pneumoniae",
        "sensitivity": "resistant to ceftriaxone, sensitive to meropenem",
        "antibiotics": []
      }'
```
✅ Sugerir próxima ação
```bash
curl -X POST http://localhost:8000/api/agent/next-step/ \
  -H "Content-Type: application/json" \
  -d '{
    "clinical_status": "culture positive 3 hours ago, no antibiotic started",
    "events": [
      "blood culture collected",
      "PCR 220",
      "fever 39ºC",
      "MAP 65"
    ]
  }'
```
✅ Sugerir recomendações do CCIH 
```bash
curl -X POST http://localhost:8000/api/agent/ccih-suggestions/ \
  -H "Content-Type: application/json" \
  -d '{
    "organism": "Klebsiella pneumoniae",
    "comorbidities": ["immunosuppression", "CKD"],
    "previous_antibiotics": ["ceftriaxone", "amikacin"]
  }'
```

---

## 📁 Documentação

* API REST disponível em `/api/`
* Documentação interativa (Swagger ou ReDoc) em `/docs/` (se configurado)

---

## 🤝 Contribuição

Contribuições são bem-vindas! Abra uma issue ou envie um pull request.

---

## 🏥 Licença

Projeto desenvolvido para fins de pesquisa e inovação em saúde.
Licença sob avaliação.

---
