# Proveniência e adaptação

O pacote foi construído a partir da arquitetura local `ARQUITETURA-HIBRIDA-SKILLS.md` versão 1.2 e consulta as cópias preservadas em `mattpocock-skills-filtered/` e `spec-kit/`. Nenhum desses diretórios é alterado pelo pacote.

As decisões de implementação seguem a seção 25 da arquitetura: dez skills em `skills/`, recursos compartilhados, runtime local Python, tickets canônicos no padrão, `change.md` no compacto, projeções geradas, checkpoint/invalidação/deduplicação e avaliação E01–E31 preparada. O pacote não copia a arquitetura inteira para cada skill.

Contribuições aproveitadas do pacote Matt: entrevista por decisões, glossário e ADR seletivo, Modules/Interfaces/Seams/Adapters, fatias verticais, TDD por comportamento e revisão em Standards/Spec. Contribuições aproveitadas do Spec Kit: artefatos separados de spec/plano/tarefas, requisitos identificados, análise de consistência, convergência, persistência, gates e integração em formato de skills.

Adaptações explícitas: decisões técnicas ficam no plano; caminhos e símbolos entram no ticket quando ajudam a execução; tarefas são canônicas nos tickets; publicação remota fica fora; perguntas são impacto × incerteza; e evidência precisa de execução, ambiente, revisão e limitações. Exemplos ilustrativos dos projetos de origem não substituem essas regras.
