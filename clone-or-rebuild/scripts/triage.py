#!/usr/bin/env python3
"""Heuristic, explainable routing for authorized software reconstruction.

Pure standard library; no network, filesystem writes or target execution.
Not legal advice or an objective quality benchmark.
"""
from __future__ import annotations

import argparse
import json

ROUTES = {
    "repo": ["git", "rg", "test runner / AST"],
    "legacy": ["repository + schema", "characterization tests", "incremental migration"],
    "web": ["DevTools/DOM/CSS", "Playwright", "authorized HTTP traces"],
    "api": ["OpenAPI/SDK", "contract tests", "authorized HTTP client"],
    "electron": ["file + hash", "@electron/asar + rg -uu", "REA if IPC/graph needs it"],
    "native": ["file + hash", "strings/imports/exports", "Ghidra/IDA or REA if needed"],
    "dotnet": ["assembly metadata", "IL/managed inspector", "REA if needed"],
    "android": ["manifest + JADX", "Apktool", "REA/ADB authorized"],
    "ios": ["package/plist inspection", "Mach-O tools", "authorized tracing if needed"],
    "firmware": ["hash + file", "binwalk/unblob", "isolated ISA analysis if needed"],
    "protocol": ["public RFC/schema", "authorized HAR/pcap", "comparison tests"],
    "game": ["engine/scripts/assets inventory", "behavior fixtures", "targeted authorized analysis"],
    "files": ["format spec + OSS parsers", "golden fixtures", "focused binary inspection"],
    "unknown": ["identify actual artifact", "obtain authorized reference", "choose minimal tooling"],
}


def recommend(source: str, target: str, oracle: str, authorized: str,
              goal: str = "behavior", oss: str = "unknown") -> dict:
    """Returns one primary route and explicit reasons; never infers legal rights."""
    warnings = []
    if authorized == "no":
        route = "STOP"
        why = "A operação pretendida não está autorizada; não analisar/executar o alvo."
    elif authorized == "unknown":
        route = "PLAN_ONLY"
        why = "Direitos de inspeção/execução/captura precisam ser esclarecidos."
    elif oss == "yes":
        route = "REUSE"
        why = "Existe componente/API/OSS potencialmente adequado; avaliar compatibilidade e licença antes de reconstruir."
    elif source == "complete":
        route = "SOURCE_FIRST"
        why = "Fonte completa e autorizada: ler código/docs/testes antes de RE; conferir correspondência com o deploy."
    elif source == "partial":
        route = "SOURCE_FIRST_PLUS_FOCUSED_RE"
        why = "Explorar fonte disponível e pesquisar somente as lacunas relevantes no artefato."
    elif goal == "visual" and target == "web":
        route = "VISUAL_BLACK_BOX"
        why = "Fidelidade visual requer DOM/CSS, snapshots e testes de interação, não descompilação nativa."
    elif target in ("api", "protocol", "files") and oracle == "yes":
        route = "SPEC_FIRST_OR_BLACK_BOX"
        why = "Contrato/oráculo observável pode permitir implementação independente sem RE profunda."
    elif source == "none" and oracle == "yes":
        route = "BLACK_BOX_THEN_FOCUSED_RE"
        why = "Testar comportamento observável; subir para RE estática/dinâmica apenas nas lacunas específicas."
    else:
        route = "DISCOVER_CONTRACT"
        why = "Falta fonte ou oráculo confiável; delimitar objetivo/artefato e obter prova antes de prometer clone."

    if oracle != "yes":
        warnings.append("Defina ou obtenha um oráculo/testes de aceitação para alegações de fidelidade.")
    if source == "complete":
        warnings.append("REA normalmente desnecessário em análise ordinária de repositório completo.")
    if target in {"native", "firmware", "android", "ios", "electron"}:
        warnings.append("Trabalho com artefatos e runtime exige aprovação separada para ações não estáticas.")
    if goal == "whole":
        warnings.append("Dividir em fatias; não prometer reprodução integral sem mapa e testes de cobertura.")

    return {
        "route": route,
        "why": why,
        "target": target,
        "initial_tools": ROUTES[target],
        "flags": warnings,
        "next_steps": [
            "Confirmar a primeira funcionalidade prioritária e os direitos para ações concretas.",
            "Registrar versão/hash e examinar fonte/contratos/disponibilidade de alternativas.",
            "Definir teste de referência antes de implementar ou aumentar a profundidade de RE.",
        ],
        "disclaimer": "Recomendação heurística, não benchmark ou aconselhamento jurídico.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", choices=["complete", "partial", "none", "unknown"], required=True)
    parser.add_argument("--target", choices=sorted(ROUTES), required=True)
    parser.add_argument("--oracle", choices=["yes", "no", "unknown"], default="unknown")
    parser.add_argument("--authorized", choices=["yes", "no", "unknown"], default="unknown")
    parser.add_argument("--oss", choices=["yes", "no", "unknown"], default="unknown")
    parser.add_argument("--goal", choices=["visual", "behavior", "migration", "interoperability", "whole", "unknown"], default="behavior")
    args = parser.parse_args()
    print(json.dumps(recommend(args.source, args.target, args.oracle, args.authorized,
                               args.goal, args.oss), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
