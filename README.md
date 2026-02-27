# DNI Status Tracker
Sistema automatizado de monitoramento e notificações para trâmites de residência (Argentina).

Este projeto demonstra a implementação de um fluxo de automação completo, focado em eficiência de notificações e persistência de estado.

## Tecnologias e Conceitos
- **Python:** Lógica principal e consumo de APIs REST.
- **GitHub Actions:** Orquestração de tarefas agendadas (Cron) e automação de workflow.
- **Telegram Bot API:** Entrega de notificações em tempo real.
- **Gerenciamento de Estado:** Persistência de dados em JSON para detecção de mudanças e prevenção de notificações duplicadas.

## Diferenciais Técnicos
- **Notificações Inteligentes:** O sistema compara o estado atual com o último estado salvo, disparando alertas apenas quando uma alteração real é detectada no servidor de origem.
- **Auto-Persistência:** O workflow do GitHub Actions é capaz de atualizar o próprio repositório com o estado mais recente, garantindo continuidade sem necessidade de um banco de dados externo.

---
*Projeto desenvolvido para fins de demonstração técnica.*
