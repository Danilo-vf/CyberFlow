"""Implementação do padrão Prototype para modelos de incidentes.

Um protótipo é um objeto configurado que pode ser clonado para criar novas
instâncias sem reconstruir seus dados manualmente.
"""

from copy import deepcopy
from dataclasses import asdict, dataclass


@dataclass
class PrototipoIncidente:
    """Modelo reutilizável de incidente de segurança."""

    titulo: str
    categoria: str
    descricao: str

    def clonar(self):
        """Retorna uma cópia independente deste protótipo."""
        return deepcopy(self)

    def para_dict(self):
        """Converte o protótipo em um dicionário para a API."""
        return asdict(self)


class CatalogoPrototipos:
    """Mantém os protótipos disponíveis e cria cópias personalizadas."""

    def __init__(self):
        self._modelos = {
            "phishing": PrototipoIncidente(
                titulo="Suspeita de phishing",
                categoria="Phishing",
                descricao=(
                    "E-mail ou mensagem suspeita com links ou anexos. "
                    "Preservar a mensagem original, verificar o remetente e "
                    "não abrir links ou anexos até a análise."
                ),
            ),
            "ransomware": PrototipoIncidente(
                titulo="Suspeita de ransomware",
                categoria="Ransomware",
                descricao=(
                    "Possível sequestro de arquivos ou pedido de resgate. "
                    "Isolar o equipamento da rede, preservar evidências e "
                    "acionar imediatamente a equipe de segurança."
                ),
            ),
            "malware": PrototipoIncidente(
                titulo="Detecção de malware",
                categoria="Malware",
                descricao=(
                    "Possível software malicioso identificado em um dispositivo. "
                    "Registrar o alerta do antivírus, evitar executar o arquivo "
                    "e encaminhar o equipamento para análise."
                ),
            ),
            "ddos": PrototipoIncidente(
                titulo="Suspeita de ataque DDoS",
                categoria="DDoS",
                descricao=(
                    "Indisponibilidade ou lentidão possivelmente causada por "
                    "volume anormal de requisições. Registrar horários, serviços "
                    "afetados e métricas de tráfego."
                ),
            ),
            "vazamento-dados": PrototipoIncidente(
                titulo="Suspeita de vazamento de dados",
                categoria="Vazamento de Dados",
                descricao=(
                    "Possível exposição ou compartilhamento não autorizado de "
                    "informações. Registrar quais dados podem ter sido expostos, "
                    "o período e os sistemas envolvidos."
                ),
            ),
            "acesso-indevido": PrototipoIncidente(
                titulo="Suspeita de acesso indevido",
                categoria="Acesso Indevido",
                descricao=(
                    "Possível acesso a conta ou sistema sem autorização. "
                    "Preservar logs, registrar usuário, origem e horário e "
                    "solicitar análise das credenciais envolvidas."
                ),
            ),
        }

    def listar(self):
        """Lista os modelos sem expor os objetos armazenados no catálogo."""
        return [
            {"id": modelo_id, **prototipo.para_dict()}
            for modelo_id, prototipo in self._modelos.items()
        ]

    def clonar(self, modelo_id, *, titulo=None, descricao=None):
        """Clona um modelo e aplica personalizações somente à cópia.

        Raises:
            KeyError: quando o identificador não existe no catálogo.
        """
        prototipo = self._modelos.get(modelo_id)
        if prototipo is None:
            raise KeyError(modelo_id)

        novo_incidente = prototipo.clonar()

        if titulo is not None:
            novo_incidente.titulo = titulo.strip()
        if descricao is not None:
            novo_incidente.descricao = descricao.strip()

        return novo_incidente


# Instância compartilhada do catálogo; os incidentes criados são clones
# independentes dos modelos originais.
catalogo_prototipos = CatalogoPrototipos()
