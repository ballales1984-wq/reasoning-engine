#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Launcher rapido per il Question-Based Reasoner.

Mantiene un singolo entrypoint stabile e delega tutta la logica a
menu_question_based.py (API aggiornata).
"""

from menu_question_based import menu_question_based


def main():
    menu_question_based()


if __name__ == "__main__":
    main()
