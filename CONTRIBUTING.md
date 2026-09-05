# Guia de Contribuição — CyberFlow

## Estratégia de branches (Trunk-Based)
- A branch `main` é protegida: nenhum push direto é permitido.
- Toda alteração deve ser feita em uma branch curta criada a partir da `main`.
- Ao terminar, abra um Pull Request para a `main`.
- O PR só pode ser mesclado após aprovação de pelo menos 1 revisor (e, futuramente, após a pipeline passar).


## Padrão de nomes de branch
- feature/nome-da-tarefa
- fix/nome-do-bug


## Padrão de commits
Use prefixos para identificar o tipo de alteração:
- `feat:` nova funcionalidade (ex: `feat: criar tela de login`)
- `fix:` correção de bug (ex: `fix: arrumar bug na API`)
- `docs:` alterações em documentação
- `refactor:` refatoração sem mudar comportamento
- `test:` adição ou ajuste de testes
- `chore:` tarefas de manutenção (configs, dependências etc.)
