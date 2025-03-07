"""Fonctions utilisées de façon systématique pour le debug."""

from __future__ import annotations
from typing import TYPE_CHECKING
from apis import connection

import sys
if TYPE_CHECKING:
    from apis.kinds import Castle


def test_debug() -> bool:
    """Test si le programme est executé en mode debug."""
    return len(sys.argv) > 2 and sys.argv[2] == "debug" and connection.current_player() == "A"


def log_func(name: str):
    """Affiche le début de la fonction en mode debug."""
    if test_debug():
        print(f"DEBUT de {name}")


def log_func_destination(i: int, j: int):
    """Affiche la destination d'une unité sur la carte."""
    if test_debug():
        print(f"destination is {i,j}")


def pause(id: str):
    """Met en pause le programme."""
    if test_debug():
        input("Press Enter to continue...\r")


def log_create_unit(castle: Castle, unit: str):
    """Affiche la création d'une unité."""
    if test_debug():
        print(f"Created {unit} at {castle}")

def log_create_castle(castle: Castle):
    """Affiche la création d'un château."""
    if test_debug():
        print(f"Created castle at {castle}")
